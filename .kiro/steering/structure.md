# Project Structure

```
discord-selfbot-python/
├── src/
│   ├── bot.py            # Main bot logic (client, events, voice connection)
│   └── test_imports.py   # Dependency verification script
├── config/               # Reserved for future config files (currently empty)
├── venv/                 # Python virtual environment (not committed)
├── .env                  # Runtime secrets and IDs (not committed)
├── .gitignore
├── install.bat           # Creates venv and installs dependencies
├── run.bat               # Activates venv and starts the bot
├── requirements.txt      # Pinned dependencies
└── README.md
```

## Conventions
- All source code lives in `src/`
- Entry point is `src/bot.py`
- Secrets and environment config go in `.env` only — never hardcoded
- Use `py` (not `python`) when invoking Python on Windows
- Comments and print statements are in Spanish (project language)
- Global state for the voice connection is managed via the `voice_connection` module-level variable in `bot.py`
