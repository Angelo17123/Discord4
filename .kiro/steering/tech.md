# Tech Stack

## Language
- Python 3.10+

## Key Libraries
- `discord.py-self` — fork of discord.py for user account (self-bot) support
- `python-dotenv` — loads environment variables from `.env`
- `PyNaCl` — voice encryption support
- `opuslib` — Opus audio codec for voice

## Environment
- Windows-first (`.bat` scripts for setup and execution)
- Virtual environment via `venv`

## Common Commands

### Install dependencies
```bat
install.bat
```

### Run the bot
```bat
run.bat
```

### Verify dependencies manually
```bat
call venv\Scripts\activate
py src\test_imports.py
```

### Run bot manually
```bat
call venv\Scripts\activate
py src\bot.py
```

## Configuration
All runtime config lives in `.env` at the project root:
```
TOKEN=      # Discord user token
GUILD_ID=   # Target guild (server) ID
CHANNEL_ID= # Target voice channel ID
```
