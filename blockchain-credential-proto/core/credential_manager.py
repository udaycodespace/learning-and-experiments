import json
import uuid
from datetime import datetime
import logging
from pathlib import Path
import os

# FIXED: Import DATA_DIR from core package [web:42]
from . import DATA_DIR, PROJECT_ROOT  # [web:42]

logging.basicConfig(level=logging.INFO)

class CredentialManager:
    """Manages verifiable credentials using blockchain and IPFS"""
    
    def __init__(self, blockchain, crypto_manager, ipfs_client):
        self.blockchain = blockchain
        self.crypto_manager = crypto_manager
        self.ipfs_client = ipfs_client
        # FIXED: Use DATA_DIR instead of relative path [web:72]
        self.credentials_file = DATA_DIR / "credentials_registry.json"
        self.credentials_registry = self.load_credentials_registry()
    
    def issue_credential(self, transcript_data):
        """Issue a new verifiable credential"""
        try:
            # Generate unique credential ID
            credential_id = str(uuid.uuid4())
            
            # Create verifiable credential structure with extended academic fields
            credential = {
                '@context': [
                    'https://www.w3.org/2018/credentials/v1',
                    'https://example.org/academic/v1'
                ],
                'id': f'urn:uuid:{credential_id}',
                'type': ['VerifiableCredential', 'AcademicTranscript'],
                'issuer': {
                    'id': 'did:example:university',
                    'name': 'G. Pulla Reddy Engineering College',
                    'department': 'Computer Science Engineering'
                },
                'issuanceDate': datetime.now().isoformat(),
                'credentialSubject': {
                    'id': f'did:example:student:{transcript_data["student_id"]}',
                    'name': transcript_data['student_name'],
                    'studentId': transcript_data['student_id'],
                    'degree': transcript_data['degree'],
                    'university': transcript_data['university'],
                    'gpa': transcript_data['gpa'],
                    'graduationYear': transcript_data['graduation_year'],
                    'courses': transcript_data.get('courses', []),
                    'issueDate': transcript_data['issue_date'],
                    # NEW: Extended academic fields
                    'semester': transcript_data.get('semester'),
                    'year': transcript_data.get('year'),
                    'className': transcript_data.get('class_name'),
                    'section': transcript_data.get('section'),
                    'backlogCount': transcript_data.get('backlog_count', 0),
                    'backlogs': transcript_data.get('backlogs', []),
                    'conduct': transcript_data.get('conduct')
                }
            }
            
            # Create digital signature
            signature = self.crypto_manager.sign_data(credential)
            if not signature:
                return {'success': False, 'error': 'Failed to create digital signature'}
            
            # Add proof to credential
            credential['proof'] = {
                'type': 'RsaSignature2018',
                'created': datetime.now().isoformat(),
                'verificationMethod': 'did:example:university#keys-1',
                'signatureValue': signature
            }
            
            # Store full credential on IPFS
            ipfs_cid = self.ipfs_client.add_json(credential)
            if not ipfs_cid:
                return {'success': False, 'error': 'Failed to store credential on IPFS'}
            
            # Create blockchain record with credential hash and metadata
            blockchain_data = {
                'credential_id': credential_id,
                'ipfs_cid': ipfs_cid,
                'credential_hash': self.crypto_manager.hash_data(credential),
                'issuer': credential['issuer']['name'],
                'subject_id': credential['credentialSubject']['studentId'],
                'subject_name': credential['credentialSubject']['name'],
                'issue_date': credential['issuanceDate'],
                'type': 'credential_issuance'
            }
            
            # Add to blockchain
            block = self.blockchain.add_block(blockchain_data)
            
            # Update local registry with extended fields
            self.credentials_registry[credential_id] = {
                'credential_id': credential_id,
                'ipfs_cid': ipfs_cid,
                'block_hash': block.hash,
                'student_name': transcript_data['student_name'],
                'student_id': transcript_data['student_id'],
                'degree': transcript_data['degree'],
                'gpa': transcript_data['gpa'],
                'issue_date': credential['issuanceDate'],
                'status': 'active',
                # NEW: Store extended academic fields in registry
                'semester': transcript_data.get('semester'),
                'year': transcript_data.get('year'),
                'class_name': transcript_data.get('class_name'),
                'section': transcript_data.get('section'),
                'backlog_count': transcript_data.get('backlog_count', 0),
                'backlogs': transcript_data.get('backlogs', []),
                'conduct': transcript_data.get('conduct')
            }
            
            self.save_credentials_registry()
            
            logging.info(f"Credential issued successfully with extended fields: {credential_id}")
            
            return {
                'success': True,
                'credential_id': credential_id,
                'ipfs_cid': ipfs_cid,
                'block_hash': block.hash,
                'message': 'Credential issued and stored successfully'
            }
            
        except Exception as e:
            logging.error(f"Error issuing credential: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_credential(self, credential_id):
        """Verify the authenticity of a credential"""
        try:
            # Accept credential IDs in different formats (e.g. 'urn:uuid:<id>')
            credential_id = self._normalize_credential_id(credential_id)
            
            # Check if credential exists in registry
            if credential_id not in self.credentials_registry:
                return {'valid': False, 'error': 'Credential not found in registry'}
            
            registry_entry = self.credentials_registry[credential_id]
            
            # Retrieve credential from IPFS
            credential = self.ipfs_client.get_json(registry_entry['ipfs_cid'])
            if not credential:
                return {'valid': False, 'error': 'Could not retrieve credential from IPFS'}
            
            # Find corresponding blockchain block
            block = self.blockchain.find_credential_block(credential_id)
            if not block:
                return {'valid': False, 'error': 'Credential block not found in blockchain'}
            
            # Verify blockchain integrity
            if not self.blockchain.is_chain_valid():
                return {'valid': False, 'error': 'Blockchain integrity compromised'}
            
            # Verify credential hash matches blockchain record
            current_hash = self.crypto_manager.hash_data(credential)
            if current_hash != block.data['credential_hash']:
                return {'valid': False, 'error': 'Credential has been tampered with'}
            
            # Verify digital signature
            signature = credential.get('proof', {}).get('signatureValue')
            if not signature:
                return {'valid': False, 'error': 'No digital signature found'}
            
            # Remove proof for signature verification
            credential_without_proof = credential.copy()
            del credential_without_proof['proof']
            
            if not self.crypto_manager.verify_signature(credential_without_proof, signature):
                return {'valid': False, 'error': 'Digital signature verification failed'}
            
            logging.info(f"Credential verified successfully: {credential_id}")
            
            return {
                'valid': True,
                'credential': credential,
                'verification_details': {
                    'blockchain_verified': True,
                    'signature_verified': True,
                    'hash_verified': True,
                    'verification_date': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logging.error(f"Error verifying credential: {str(e)}")
            return {'valid': False, 'error': str(e)}
    
    def selective_disclosure(self, credential_id, selected_fields):
        """Create a selective disclosure of credential fields"""
        try:
            # Normalize credential id formats
            credential_id = self._normalize_credential_id(credential_id)
            
            # Verify credential first
            verification_result = self.verify_credential(credential_id)
            if not verification_result['valid']:
                return {'success': False, 'error': verification_result['error']}
            
            credential = verification_result['credential']
            subject_data = credential['credentialSubject']
            
            # Create selective disclosure - supports new fields
            disclosed_data = {}
            for field in selected_fields:
                if field in subject_data:
                    disclosed_data[field] = subject_data[field]
                else:
                    return {'success': False, 'error': f'Field "{field}" not found in credential'}
            
            # Create proof for selective disclosure
            proof = self.crypto_manager.create_proof_for_fields(subject_data, disclosed_data)
            
            # Create selective disclosure document
            disclosure_doc = {
                '@context': [
                    'https://www.w3.org/2018/credentials/v1',
                    'https://example.org/academic/v1'
                ],
                'type': 'SelectiveDisclosure',
                'originalCredentialId': credential_id,
                'disclosedFields': disclosed_data,
                'proof': proof,
                'issuer': credential['issuer'],
                'issuanceDate': credential['issuanceDate'],
                'disclosureDate': datetime.now().isoformat()
            }
            
            logging.info(f"Selective disclosure created for credential: {credential_id}")
            
            return {
                'success': True,
                'disclosure': disclosure_doc,
                'message': f'Selective disclosure created with {len(selected_fields)} fields'
            }
            
        except Exception as e:
            logging.error(f"Error creating selective disclosure: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_all_credentials(self):
        """Get all credentials in the registry with extended fields"""
        credentials = []
        for cred_id, registry_entry in self.credentials_registry.items():
            # Enrich with full credential data if available
            full_credential = self.ipfs_client.get_json(registry_entry['ipfs_cid'])
            if full_credential:
                registry_entry['full_credential'] = full_credential['credentialSubject']
            credentials.append(registry_entry)
        return credentials
    
    def get_credential(self, credential_id):
        """Get a specific credential by ID"""
        credential_id = self._normalize_credential_id(credential_id)
        if credential_id in self.credentials_registry:
            registry_entry = self.credentials_registry[credential_id]
            # Also get full credential from IPFS
            full_credential = self.ipfs_client.get_json(registry_entry['ipfs_cid'])
            if full_credential:
                registry_entry['full_credential'] = full_credential
            return registry_entry
        return None
    
    def load_credentials_registry(self):
        """Load credentials registry from data/ folder"""
        try:
            # FIXED: Ensure data directory exists
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r') as f:
                    registry = json.load(f)
                    logging.info(f"Credentials registry loaded from {self.credentials_file} with {len(registry)} entries")
                    return registry
            else:
                logging.info(f"No existing credentials registry found at {self.credentials_file}")
                return {}
        except Exception as e:
            logging.error(f"Error loading credentials registry: {str(e)}")
            return {}
    
    def _normalize_credential_id(self, credential_id):
        """Normalize credential ID so callers can pass either raw UUID or URN forms."""
        if not credential_id:
            return credential_id
        try:
            # If it's bytes or other, convert to str
            cid = str(credential_id)
            # Common URN prefix used for UUIDs
            if cid.startswith('urn:uuid:'):
                return cid.split('urn:uuid:')[-1]
            if cid.startswith('urn:'):
                # fallback: return last component after ':'
                return cid.split(':')[-1]
            return cid
        except Exception:
            return credential_id
    
    def save_credentials_registry(self):
        """Save credentials registry to data/ folder"""
        try:
            # FIXED: Ensure data directory exists
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(self.credentials_file, 'w') as f:
                json.dump(self.credentials_registry, f, indent=2)
            logging.info(f"Credentials registry saved to {self.credentials_file}")
        except Exception as e:
            logging.error(f"Error saving credentials registry: {str(e)}")
    
    def revoke_credential(self, credential_id, reason=""):
        """Revoke a credential (mark as revoked)"""
        try:
            credential_id = self._normalize_credential_id(credential_id)
            if credential_id not in self.credentials_registry:
                return {'success': False, 'error': 'Credential not found'}
            
            # Update status in registry
            self.credentials_registry[credential_id]['status'] = 'revoked'
            self.credentials_registry[credential_id]['revocation_date'] = datetime.now().isoformat()
            self.credentials_registry[credential_id]['revocation_reason'] = reason
            
            # Add revocation record to blockchain
            revocation_data = {
                'credential_id': credential_id,
                'type': 'credential_revocation',
                'reason': reason,
                'revocation_date': datetime.now().isoformat()
            }
            
            self.blockchain.add_block(revocation_data)
            self.save_credentials_registry()
            
            logging.info(f"Credential revoked: {credential_id}")
            
            return {'success': True, 'message': 'Credential revoked successfully'}
            
        except Exception as e:
            logging.error(f"Error revoking credential: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_credential(self, credential_id):
        """Permanently remove a credential from the registry."""
        try:
            credential_id = self._normalize_credential_id(credential_id)
            if credential_id not in self.credentials_registry:
                return {'success': False, 'error': 'Credential not found'}

            # Remove entry and persist
            del self.credentials_registry[credential_id]
            self.save_credentials_registry()

            logging.info(f"Credential deleted from registry: {credential_id}")
            return {'success': True, 'message': 'Credential deleted successfully'}
        except Exception as e:
            logging.error(f"Error deleting credential: {str(e)}")
            return {'success': False, 'error': str(e)}
