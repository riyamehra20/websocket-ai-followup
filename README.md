# WebSocket AI Follow-up Questions

Real-time AI-powered follow-up question generator using WebSocket and Google Gemini API.

## 🔗 Live Demo

**🌐 Live Application:** [Coming Soon]

**📂 GitHub Repository:** [Your GitHub Link]

## ✨ Features

- ✅ Real-time WebSocket communication
- ✅ AI-generated follow-up questions using Google Gemini
- ✅ Each question includes exact words from user's previous input
- ✅ 3 dynamic follow-ups followed by completion message
- ✅ Beautiful, responsive UI

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** HTML, CSS, JavaScript
- **AI:** Google Gemini API
- **WebSocket:** Native WebSocket
- **Deployment:** Render.com

## 🚀 Local Setup

### Prerequisites

- Python 3.8+
- Google Gemini API Key

### Installation

1. Clone repository
```bash
git clone [your-repo-url]
cd websocket-ai-followup
```

2. Set up backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

3. Create `.env` file in backend folder
```
GEMINI_API_KEY=your_key_here
```

4. Run server
```bash
uvicorn app:app --reload
```

5. Open http://localhost:8000

## 📸 Screenshots

[Add screenshots here]

## 📄 License


