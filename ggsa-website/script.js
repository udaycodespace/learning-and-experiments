/* GGSA SYSTEM CORE SCRIPT v2.0 */
/* AUTH: UDAY-WORKS */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initScrollEffects();
    initCountdown();
    initHeroRotator(); // Initializes the text changer
    console.log("%c SYSTEM_ONLINE // GGSA_GPREC ", "background: #000; color: #ccff00; font-size: 12px; padding: 4px;");
});

/* --- 1. Navigation Logic (Mobile + Active State) --- */
function initNavigation() {
    const navContainer = document.querySelector('.nav-container');
    const navLinksContainer = document.querySelector('.nav-links');
    
    // A. Mobile Toggle Injection
    if (!document.querySelector('.mobile-toggle')) {
        const toggleBtn = document.createElement('div');
        toggleBtn.className = 'mobile-toggle';
        toggleBtn.innerHTML = '/// MENU';
        toggleBtn.style.cssText = `
            display: none; 
            font-family: var(--font-mono); 
            cursor: pointer; 
            font-size: 0.8rem;
            border: 1px solid var(--text-main);
            padding: 5px 10px;
            color: var(--text-main);
        `;
        
        // Insert before the Join button
        navContainer.insertBefore(toggleBtn, document.querySelector('.nav-action'));

        // CSS Injection for Mobile Menu
        const style = document.createElement('style');
        style.innerHTML = `
            @media (max-width: 768px) {
                .mobile-toggle { display: block !important; }
                .nav-links { 
                    position: absolute; 
                    top: 100%; left: 0; width: 100%; 
                    background: var(--bg); 
                    flex-direction: column; 
                    padding: 2rem; 
                    border-bottom: 1px solid var(--border);
                    display: none;
                    z-index: 999;
                }
                .nav-links.active { display: flex; }
                .nav-item { margin-bottom: 1rem; font-size: 1.2rem; }
            }
        `;
        document.head.appendChild(style);

        // Toggle Click Event
        toggleBtn.addEventListener('click', () => {
            navLinksContainer.classList.toggle('active');
            toggleBtn.innerHTML = navLinksContainer.classList.contains('active') ? '/// CLOSE' : '/// MENU';
            
            // Visual feedback
            toggleBtn.style.background = navLinksContainer.classList.contains('active') ? 'var(--text-main)' : 'transparent';
            toggleBtn.style.color = navLinksContainer.classList.contains('active') ? 'var(--bg)' : 'var(--text-main)';
        });
    }

    // B. Active Link Highlighting
    const currentPage = window.location.pathname.split("/").pop() || "index.html";
    const links = document.querySelectorAll('.nav-item');
    
    links.forEach(link => {
        const linkHref = link.getAttribute('href');
        
        // Check if link matches current page
        if (linkHref === currentPage) {
            link.classList.add('active-link');
            // Force CSS styles via JS to ensure visibility
            link.style.color = 'var(--accent)';
            link.style.fontWeight = 'bold';
            link.innerHTML = `> ${link.innerText}`; 
        }
    });
}

/* --- 2. Scroll Reveal Effects --- */
function initScrollEffects() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Target elements to animate
    const targets = document.querySelectorAll('.card, .timeline-block, .bounty-card, .node-card, .list-row, .reveal-container');
    
    targets.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        observer.observe(el);
    });

    const style = document.createElement('style');
    style.innerHTML = `
        .visible { opacity: 1 !important; transform: translateY(0) !important; }
    `;
    document.head.appendChild(style);
}

/* --- 3. Hero Text Rotator --- */
/* --- 3. Hero Text Rotator (Short & Crispy) --- */
function initHeroRotator() {
    const heroTextEl = document.getElementById('dynamic-hero-text');
    if (!heroTextEl) return; 

    // THE NEW SHORT LIST
    const phrases = [
        "SYSTEM<br>ONLINE",
        "CODE<br>IS<br>LAW",
        "GEMINI<br>CORE",
        "BUILD<br>THE<br>NEXT"
    ];

    let currentIndex = 0;

    setInterval(() => {
        // 1. Fade out
        heroTextEl.classList.add('fade-out');

        // 2. Wait 500ms, swap text
        setTimeout(() => {
            currentIndex = (currentIndex + 1) % phrases.length;
            heroTextEl.innerHTML = phrases[currentIndex];
            
            // 3. Fade back in
            heroTextEl.classList.remove('fade-out');
        }, 500);

    }, 2500); // Changed to 2.5 seconds for faster impact
}

/* --- 4. Countdown Timer (For Events Page) --- */
function initCountdown() {
    const timerEl = document.getElementById('timer');
    if (!timerEl) return; 

    // Set deadline (Currently simulated to 48 hours from now)
    // To set a specific date, use: new Date("Dec 17, 2025 15:30:00").getTime();
    let countDownDate = new Date().getTime() + (48 * 60 * 60 * 1000);

    const x = setInterval(function() {
        const now = new Date().getTime();
        const distance = countDownDate - now;

        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Format with leading zeros
        const h = hours < 10 ? "0" + hours : hours;
        const m = minutes < 10 ? "0" + minutes : minutes;
        const s = seconds < 10 ? "0" + seconds : seconds;

        timerEl.innerHTML = `${h}:${m}:${s}`;

        if (distance < 0) {
            clearInterval(x);
            timerEl.innerHTML = "EXEC_COMPLETE";
            timerEl.style.color = "red";
        }
    }, 1000);
}