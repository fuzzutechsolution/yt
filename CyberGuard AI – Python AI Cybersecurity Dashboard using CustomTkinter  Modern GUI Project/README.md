# CyberGuard AI – Smart Privacy Protection & Threat Detection

A modern, interactive cybersecurity-themed web application built with Python Flask, HTML5, CSS3, and JavaScript. This project is designed to demonstrate basic AI-like threat detection and privacy protection concepts using clear, beginner-friendly rule-based algorithms. 

This website features a high-end, futuristic dark cyber design with responsive layouts, glassmorphism, glowing accents, loading animations, and dynamic transitions.

## 🚀 Features

1. **Dashboard**: Live analytics of scan metrics (total scans, threats detected, safe files, and average risk rating) tracked across scanning modules.
2. **URL Scanner**: Scans links for common phishing cues (SSL/HTTPS configuration, suspicious domain keywords, numeric IP domains, and excessive URL lengths) and outputs a detailed risk warning.
3. **Email Scanner**: Checks message blocks for classic urgency-driven and incentive-based phishing vocabulary, showing a breakdown of found indicators.
4. **Password Checker**: Evaluates passwords locally across multiple security criteria (length, casing, numerical inputs, and special characters) to gauge overall strength.
5. **Privacy Tips**: A grid of cards showcasing crucial modern cyber hygiene actions, expandable for detailed steps.
6. **Futuristic UI**: Fully responsive CSS layout, custom glassmorphism components, animated loading transitions, and glowing visual cues.

---

## 📁 Folder Structure

```text
CyberGuardAI/
│
├── app.py                   # Main Flask application (under 300 lines)
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
│
├── templates/               # Flask HTML templates
│   ├── base.html            # Shared base template (navbar, footer, global styles/scripts)
│   ├── index.html           # Landing home page
│   ├── url_scanner.html     # URL threat detector page
│   ├── email_scanner.html   # Email phishing detector page
│   ├── password_checker.html# Password strength verification page
│   ├── privacy_tips.html    # Practical cybersecurity actions grid
│   └── dashboard.html       # Analytics overview dashboard
│
└── static/                  # Static assets
    ├── style.css            # Central CSS stylesheet (dark cyber theme, glassmorphism)
    └── script.js            # UI behavior, animations, and dynamic dashboard mock data
```

---

## 🛠️ Installation & Setup

Follow these simple steps to set up and run CyberGuard AI locally:

### 1. Install Python
Make sure you have Python 3.8+ installed on your system. You can check your version in the terminal:
```bash
python --version
```

### 2. Clone or Extract the Project
Open your terminal or command prompt in the `CyberGuardAI/` project folder.

### 3. Install Dependencies
Install Flask from the root directory using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the Flask development server:
```bash
python app.py
```

### 5. Access the Web Application
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 📊 Screenshots Placeholder

*Placeholder for YouTube video thumbnail / Application demo screens*
- **Landing Home Page**: Custom neon graphics and clean CTAs.
- **Scanner Output**: Glowing gauges indicating Safe/Warning/Danger states.

---

## 🔒 Security Principles Covered
- **HTTPS & SSL Encryption**: Highlighting security headers in URLs.
- **Phishing Language Patterns**: Pattern identification inside email spam.
- **Password Entropy**: Character diversity and length requirements.
