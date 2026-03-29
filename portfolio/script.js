document.addEventListener("DOMContentLoaded", function () {
    // ==================== ELEMENTS ====================
    const themeToggle = document.getElementById("themeToggle");
    const body = document.body;
    const terminalInput = document.getElementById("terminalInput");
    const terminalOutput = document.getElementById("terminalOutput");
    const terminalBody = document.getElementById("terminalBody");
    const cmdButtons = document.querySelectorAll(".cmd-button");

    let commandHistory = [];
    let historyIndex = -1;
    let currentTheme = "dark";

    // ==================== THEME TOGGLE ====================
    themeToggle.addEventListener("click", function () {
        if (currentTheme === "dark") {
            body.classList.remove("dark-theme");
            body.classList.add("light-theme");
            themeToggle.innerHTML = '<span class="theme-icon">🌙</span>';
            currentTheme = "light";
            localStorage.setItem("theme", "light");
        } else {
            body.classList.remove("light-theme");
            body.classList.add("dark-theme");
            themeToggle.innerHTML = '<span class="theme-icon">☀️</span>';
            currentTheme = "dark";
            localStorage.setItem("theme", "dark");
        }
    });

    // Load saved theme
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") {
        body.classList.remove("dark-theme");
        body.classList.add("light-theme");
        themeToggle.innerHTML = '<span class="theme-icon">🌙</span>';
        currentTheme = "light";
    }

    // ==================== TERMINAL COMMANDS ====================
    const commands = {
        help: `<div class="cmd-result">
<span style="color: var(--accent-1); font-weight: 700; font-size: 1.1em;">━━━ AVAILABLE COMMANDS ━━━</span><br><br>
<span style="color: var(--accent-3); font-weight: 700;">📋 INFO</span><br>
  whoami          →  Who I am<br>
  status          →  Current status<br>
  experience      →  View internships (then exp1/exp2/exp3)<br>
  projects        →  View projects (then proj1/proj2/proj3)<br>
  skills          →  View skills (then skill1/skill2/skill3)<br>
  certifications  →  View certifications (then cert1/cert2/cert3)<br>
  others          →  Leadership & extras<br><br>
<span style="color: var(--accent-3); font-weight: 700;">🚀 ACTIONS</span><br>
  resume          →  Download resume (then resume1/resume2/resume3)<br>
  github          →  Open GitHub profile<br>
  linkedin        →  Open LinkedIn profile<br>
  email           →  Copy email address<br><br>
<span style="color: var(--accent-3); font-weight: 700;">⚙️ SYSTEM</span><br>
  clear           →  Clear terminal<br>
  help            →  Show this message<br>
</div>`,

       whoami: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700; font-size: 1.6em; display: block; margin-bottom: 8px;">
⚡ SOMAPURAM UDAY
</span>
<span style="color: var(--accent-1); font-weight: 600; font-size: 1.1em; display: block; margin-bottom: 16px;">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</span>
<span style="color: var(--text); line-height: 2;">
<strong style="color: var(--accent-3);">Role:</strong> AI/ML, Data Science & Analytics Enthusiast<br>
<strong style="color: var(--accent-3);">Education:</strong> 4th Year Computer Science Student<br>
<strong style="color: var(--accent-3);">Institution:</strong> GPREC<br>
<strong style="color: var(--accent-3);">Status:</strong> <span style="color: var(--accent-4);">● OPEN TO OPPORTUNITIES</span>
</span>
</div>`,


        status: `<div class="cmd-result">
<span style="color: var(--accent-1); font-weight: 700;">CURRENT STATUS:</span><br>
→ Final Year (7th Semester) CS Student @ GPREC<br>
→ Building: <span style="color: var(--accent-1); font-weight: 600;">Blockchain Credential System</span><br>
→ Team: Shashi & Varshith<br>
→ Actively preparing for placements<br>
→ Core: AI/ML • Data Science • Data Analytics
</div>`,

        experience: `<div class="cmd-result">
<span style="color: var(--accent-3); font-weight: 700;">🎯 SELECT DOMAIN:</span><br><br>
Type <span style="color: var(--accent-1); font-weight: 700;">exp1</span> → AI/ML Internships<br>
Type <span style="color: var(--accent-1); font-weight: 700;">exp2</span> → Data Science Internships<br>
Type <span style="color: var(--accent-1); font-weight: 700;">exp3</span> → Data Analytics Internships
</div>`,

        exp1: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">🤖 AI/ML INTERNSHIPS:</span><br>
→ AI + Azure Intern — Edunet Foundation — May–Jun 2025<br>
→ AI & Deep Learning Intern — GENZ Educatewing — May–Jun 2025<br>
→ AI/ML Intern — The Web Blinders — May 2025
</div>`,

        exp2: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">📊 DATA SCIENCE INTERNSHIP:</span><br>
→ Data Science Master Virtual Internship — Apr–Jun 2024
</div>`,

        exp3: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">📈 DATA ANALYTICS INTERNSHIP:</span><br>
→ Data Analytics Intern — SmartInternz — May–Jun 2025
</div>`,

        projects: `<div class="cmd-result">
<span style="color: var(--accent-3); font-weight: 700;">🎯 SELECT DOMAIN:</span><br><br>
Type <span style="color: var(--accent-1); font-weight: 700;">proj1</span> → AI/ML Projects<br>
Type <span style="color: var(--accent-1); font-weight: 700;">proj2</span> → Data Science Projects<br>
Type <span style="color: var(--accent-1); font-weight: 700;">proj3</span> → Data Analytics Projects
</div>`,

        proj1: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">🚀 AI/ML PROJECTS:</span><br>
→ Anime Recommendation System — Python, scikit-learn<br>
→ YOLOv8 Object Detection Pipeline — TensorFlow, Keras, OpenCV<br>
→ Sentiment Analysis CNN — TensorFlow, Keras
</div>`,

        proj2: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">🔬 DATA SCIENCE PROJECTS:</span><br>
→ Cosmetic Insights Dashboard — Python, Pandas, Tableau<br>
→ Mobile Device Usage Analysis — Matplotlib, Seaborn<br>
→ Advanced Sales Forecasting — Prophet, ARIMA
</div>`,

        proj3: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">📊 DATA ANALYTICS PROJECTS:</span><br>
→ Cosmetic Insights Dashboard — Tableau, Python, SQL<br>
→ Mobile Device Usage Analysis — Python, Matplotlib, Seaborn
</div>`,

        skills: `<div class="cmd-result">
<span style="color: var(--accent-3); font-weight: 700;">🎯 SELECT DOMAIN:</span><br><br>
Type <span style="color: var(--accent-1); font-weight: 700;">skill1</span> → AI/ML Skills<br>
Type <span style="color: var(--accent-1); font-weight: 700;">skill2</span> → Data Science Skills<br>
Type <span style="color: var(--accent-1); font-weight: 700;">skill3</span> → Data Analytics Skills
</div>`,

        skill1: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">⚙️ AI/ML SKILLS:</span><br>
Python • TensorFlow • Keras • PyTorch • CNN • NLP • YOLOv8 • OpenCV • Clustering
</div>`,

        skill2: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">📊 DATA SCIENCE SKILLS:</span><br>
Python • Pandas • NumPy • SQL • Tableau • Power BI • Regression • Classification • Generative AI
</div>`,

        skill3: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">📈 DATA ANALYTICS SKILLS:</span><br>
Python • Pandas • NumPy • SQL • Tableau • Power BI • Excel • EDA • Feature Engineering
</div>`,

        certifications: `<div class="cmd-result">
<span style="color: var(--accent-3); font-weight: 700;">🎯 SELECT DOMAIN:</span><br><br>
Type <span style="color: var(--accent-1); font-weight: 700;">cert1</span> → AI/ML Certifications<br>
Type <span style="color: var(--accent-1); font-weight: 700;">cert2</span> → Data Science Certifications<br>
Type <span style="color: var(--accent-1); font-weight: 700;">cert3</span> → Data Analytics Certifications
</div>`,

        cert1: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">🏆 AI/ML CERTIFICATIONS:</span><br>
→ Machine Learning for All — University of London<br>
→ Google AI/ML Virtual Internship — EduSkills Foundation<br>
→ Microsoft AI-900 — Microsoft / AICTE Edunet<br>
→ Smart Coder Certification — Smart Interviews
</div>`,

        cert2: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">🏆 DATA SCIENCE CERTIFICATIONS:</span><br>
→ Data Science Foundations — University of London<br>
→ Google Advanced Data Analytics — Google<br>
→ Machine Learning for All — University of London
</div>`,

        cert3: `<div class="cmd-result">
<span style="color: var(--accent-2); font-weight: 700;">🏆 DATA ANALYTICS CERTIFICATIONS:</span><br>
→ Google Advanced Data Analytics — Google<br>
→ Excel Basics for Data Analysis — SkillUp<br>
→ Microsoft Excel Basics — Coursera
</div>`,

        others: `<div class="cmd-result">
<span style="color: var(--accent-1); font-weight: 700;">🌟 LEADERSHIP & EXTRAS:</span><br>
→ Student Coordinator — CSI Chapter @ GPREC<br>
→ Intensive Training Program — Smart Interviews<br>
→ Google Code-in 2018 — Open Source Contribution<br><br>
<span style="color: var(--accent-1); font-weight: 700;">📚 OTHER PLATFORMS:</span><br>
Infosys Springboard • EduSkills Academy • NPTEL • edX • Coursera
</div>`,

        resume: `<div class="cmd-result">
<span style="color: var(--accent-3); font-weight: 700;">📄 SELECT RESUME:</span><br><br>
Type <span style="color: var(--accent-1); font-weight: 700;">resume1</span> → AI/ML Resume<br>
Type <span style="color: var(--accent-1); font-weight: 700;">resume2</span> → Data Science Resume<br>
Type <span style="color: var(--accent-1); font-weight: 700;">resume3</span> → Data Analytics Resume
</div>`,

        resume1: () => {
            downloadFile("resumes/resume_ai_ml.pdf", "SOMAPURAM_UDAY_AI_ML_Resume.pdf");
            return `<div class="cmd-result success-msg">✓ Downloading AI/ML Resume...</div>`;
        },

        resume2: () => {
            downloadFile("resumes/resume_datascience.pdf", "SOMAPURAM_UDAY_DataScience_Resume.pdf");
            return `<div class="cmd-result success-msg">✓ Downloading Data Science Resume...</div>`;
        },

        resume3: () => {
            downloadFile("resumes/resume_dataanalytics.pdf", "SOMAPURAM_UDAY_DataAnalytics_Resume.pdf");
            return `<div class="cmd-result success-msg">✓ Downloading Data Analytics Resume...</div>`;
        },

        github: () => {
            window.open("https://github.com/udaycodespace", "_blank");
            return `<div class="cmd-result success-msg">✓ Opening GitHub profile...</div>`;
        },

        linkedin: () => {
            window.open("https://www.linkedin.com/in/somapuram-uday/", "_blank");
            return `<div class="cmd-result success-msg">✓ Opening LinkedIn profile...</div>`;
        },

        email: () => {
            copyToClipboard("udaysomapuram@gmail.com");
            return `<div class="cmd-result success-msg">✓ Email copied: udaysomapuram@gmail.com</div>`;
        },

        clear: () => {
            terminalOutput.innerHTML = "";
            showWelcome();
            return null;
        }
    };

    // Aliases
    const aliases = {
        h: "help",
        cls: "clear",
        clr: "clear",
        gh: "github",
        ln: "linkedin",
        mail: "email",
        certs: "certifications"
    };

    // ==================== FUNCTIONS ====================
function showWelcome() {
    terminalOutput.innerHTML = `
        <div class="output-line">
            <span style="color: var(--accent-1); font-weight: 700; font-size: 1.2em; display: block; margin-bottom: 12px;">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</span>
            <span style="color: var(--accent-2); font-weight: 700; font-size: 1.4em; display: block; margin-bottom: 8px;">
⚡ SOMAPURAM UDAY — PORTFOLIO TERMINAL
</span>
            <span style="color: var(--accent-1); font-weight: 700; font-size: 1.2em; display: block; margin-bottom: 16px;">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</span>
            <span style="color: var(--text); display: block; margin-bottom: 8px;">
Welcome! Type <span style="color: var(--accent-3); font-weight: 700;">'help'</span> to explore my portfolio
</span>
            <span style="color: var(--text-dim); font-size: 0.9em;">
or use the quick command buttons →
</span>
        </div>
    `;
}


    function processCommand(input) {
        const cmd = input.toLowerCase().trim();

        if (!cmd) return;

        // Add to history
        commandHistory.push(cmd);
        historyIndex = commandHistory.length;

        // Echo command
        const echo = document.createElement("div");
        echo.className = "output-line";
        echo.innerHTML = `<span class="cmd-echo">➜ ${input}</span>`;
        terminalOutput.appendChild(echo);

        // Process command
        let resolvedCmd = aliases[cmd] || cmd;
        let output;

        if (commands[resolvedCmd]) {
            const result = typeof commands[resolvedCmd] === "function" 
                ? commands[resolvedCmd]() 
                : commands[resolvedCmd];
            
            if (result !== null) {
                output = document.createElement("div");
                output.className = "output-line";
                output.innerHTML = result;
                terminalOutput.appendChild(output);
            }
        } else {
            output = document.createElement("div");
            output.className = "output-line";
            output.innerHTML = `<div class="cmd-result error-msg">✗ Command not found: '${cmd}'<br>Type 'help' to see available commands</div>`;
            terminalOutput.appendChild(output);
        }

        // Scroll to bottom
        terminalBody.scrollTop = terminalBody.scrollHeight;
        terminalInput.value = "";
    }

    function downloadFile(path, filename) {
        const link = document.createElement("a");
        link.href = path;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("copy");
            document.body.removeChild(textArea);
        }
    }

    // ==================== EVENT LISTENERS ====================
    terminalInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            processCommand(terminalInput.value);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            if (historyIndex > 0) {
                historyIndex--;
                terminalInput.value = commandHistory[historyIndex];
            }
        } else if (e.key === "ArrowDown") {
            e.preventDefault();
            if (historyIndex < commandHistory.length - 1) {
                historyIndex++;
                terminalInput.value = commandHistory[historyIndex];
            } else {
                historyIndex = commandHistory.length;
                terminalInput.value = "";
            }
        }
    });

    // Quick command buttons
    cmdButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            const cmd = this.getAttribute("data-cmd");
            terminalInput.value = cmd;
            processCommand(cmd);
            terminalInput.focus();
        });
    });

    // Initialize
    showWelcome();
    terminalInput.focus();
});
