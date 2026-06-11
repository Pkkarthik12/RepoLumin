# RepoLumin: Local Automated GitHub AI Curator


RepoLumin is an autonomous AI agent that runs locally on your machine to discover, curate, and summarize the best new GitHub repositories in your specific areas of interest.

## 🚀 Features

- **Personalized Discovery:** Select from AI, Robotics, Cybersecurity, GameDev, and more, or add your own.
- **AI-Enhanced Summaries:** Uses Google Gemini to distill complex repository descriptions into clear, actionable insights.
- **Daily Local Storage:** Automatically generates date-stamped spreadsheets (`.csv`) directly on your machine.
- **Autonomous Scheduler:** Runs in the background and executes its mission every 24 hours.
- **Duplicate Prevention:** Tracks discovered repositories to ensure every entry in your spreadsheet is unique.

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Sourcing:** GitHub Search API
- **AI Intelligence:** Google Gemini API
- **Processing:** Pandas & Python-Schedule

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/RepoLumin.git
   cd RepoLumin
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY and GITHUB_TOKEN to .env
   ```

## 🚦 Usage

Start the agent:
```bash
python main.py
```
On the first run, the agent will guide you through selecting your interests. After that, it will enter a background loop, performing a fresh harvest every 24 hours.

## 📂 Project Structure

```text
RepoLumin/
├── agent/
│   ├── ai_processor.py   # Gemini API integration
│   ├── github_client.py  # Repository discovery logic
│   └── storage.py        # CSV & State management
├── exports/              # Your daily spreadsheets live here
├── main.py               # CLI & Daily Scheduler
├── .env.example          # Template for API keys
└── requirements.txt      # Project dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT © 2026 RepoLumin Team
