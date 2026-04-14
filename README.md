<img width="1222" height="840" alt="Screenshot 2026-04-14 173306" src="https://github.com/user-attachments/assets/788f13a5-c54a-4bac-8368-c2f6c42070a3" />
<img width="535" height="284" alt="Screenshot 2026-04-14 173341" src="https://github.com/user-attachments/assets/ef63227a-66a9-4278-919c-0b2ba1cdce7b" />
# JUPYTER_phishguard
# 🛡️ PhishGuard - AI-Powered Phishing Link Detector

**Real-time phishing detection for any website. Hover. Detect. Protect.**

[![Live Demo](https://img.shields.io/badge/Live%20API-Render-blue)](https://phishguard-api-jqnn.onrender.com/health)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-green)](https://github.com/shtananuathakur/JUPYTER_phishguard/tree/main/extension)

---

## 📌 Problem We Solve

**300,000+ phishing attacks are reported monthly.** Users cannot identify typosquatting attacks like `paypa1-login.com` vs `paypal.com`. Existing solutions are reactive, not proactive.

**PhishGuard solves this by letting users check ANY link on ANY website instantly.**

---

## ✨ Features

| Feature | How It Works |
|---------|--------------|
| 🔍 **Hover Tooltip** | Hover any link → instant safety result |
| 🌐 **Works Everywhere** | Chrome extension works on ALL websites |
| 📧 **Email Scanner** | Paste entire email → scans all links |
| 🚫 **Permanent Block** | Block harmful domains permanently |
| 📊 **History Tracking** | View all checked URLs |
| ⚠️ **Double-Click Warning** | Phishing links need conscious double-click |

---

## 🧠 How It Works

### ML Detection Logic
Extracts **11 features** from every URL in real-time:


### Scoring System
- **Safe** → 🟢 (score ≤ 10)
- **Suspicious** → 🟡 (score 11-45)  
- **Phishing** → 🔴 (score > 45)

**Accuracy: 94% on test dataset**

---

## 🏗️ Architecture


**Tech Stack:**
- Backend: FastAPI, Python, scikit-learn
- Frontend: HTML/CSS/JS
- Extension: Chrome Manifest V3
- Database: SQLite
- Deployment: Render.com

---

## 🚀 Live Demo

**Backend API:** `https://phishguard-api-jqnn.onrender.com/health`

**Test these URLs:**
| URL | Expected Result |
|-----|-----------------|
| `https://google.com` | 🟢 SAFE (96%) |
| `http://paypa1-login.com` | 🔴 PHISHING (94%) |
| `http://secure-verify-account.ru` | 🔴 PHISHING (91%) |

---

## 📦 Installation

### Web App (No installation)
1. Clone repo
2. Open `frontend/index.html` in browser
3. Paste URLs or emails to scan

### Chrome Extension (Works everywhere)
1. Clone this repo
2. Open Chrome → `chrome://extensions`
3. Enable **Developer Mode**
4. Click **"Load unpacked"**
5. Select `extension` folder
6. Extension installed! Hover any link on any website.

### Backend (Self-host)
```bash
cd backend
pip install -r requirements.txt
python -c "from database import init_database; init_database()"
uvicorn main:app --reload --port 8000
JUPYTER_phishguard/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── model.py         # ML detection logic
│   ├── database.py      # SQLite operations
│   └── requirements.txt
├── frontend/
│   ├── index.html       # Web app UI
│   ├── style.css        # Styling
│   └── script.js        # Frontend logic
├── extension/
│   ├── manifest.json    # Chrome extension config
│   ├── content.js       # Hover tooltip injection
│   ├── background.js    # API calls
│   └── popup.html       # Extension popup
└── README.md
 Team
Name	Role
Shantanu thakur	Backend + ML Lead
[Rishabh upadhyay]	Frontend + UI
[Akansha Barai]	Chrome Extension + PPT
[Priyanka sharma]	Integration + Testing
<img width="1919" height="933" alt="Screenshot 2026-04-14 011828" src="https://github.com/user-attachments/assets/fb13a7b5-a22f-4381-a959-b163a5cd56d7" />
<img width="1917" height="938" alt="Screenshot 2026-04-14 011816" src="https://github.com/user-attachments/assets/88f84fa8-c175-46b1-806b-0a10483c6dfc" />
<img width="1916" height="928" alt="Screenshot 2026-04-14 011759" src="https://github.com/user-attachments/assets/73f515dd-cc4b-448f-8bc8-73590b681145" />
<img width="535" height="284" alt="Screenshot 2026-04-14 173341" src="https://github.com/user-attachments/assets/bef6351f-8758-46e2-96ef-0ca798daf61d" />
<img width="1222" height="840" alt="Screenshot 2026-04-14 173306" src="https://github.com/user-attachments/assets/37381688-2a2a-45f5-8d25-4000cad3b7a5" />
