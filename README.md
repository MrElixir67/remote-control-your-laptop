# Remote Control Your Laptop

Control your Linux laptop remotely through a Telegram bot. Lock, unlock, reboot, shutdown, and monitor system status from your phone.

## Features

- Lock screen remotely
- Unlock with automatic password entry
- System status monitoring (uptime, load, memory)
- Reboot and shutdown with confirmation
- Security whitelist by Telegram user ID
- Auto-start on boot

## Requirements

- Linux with systemd (tested on Ubuntu 26.04)
- Python 3.10 or newer
- Telegram account
- Wayland or X11 display server

## Installation

### Install dependencies

```bash
# Python library
pip3 install python-telegram-bot --user

# For Wayland sessions
sudo apt install -y ydotool util-linux-extra

# For X11 sessions (optional)
sudo apt install -y xdotool
```

### Clone repository

```bash
git clone https://github.com/MrElixir67/remote-control-your-laptop.git
cd remote-control-your-laptop
```

### Create Telegram bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save the bot token
4. Get your user ID from [@userinfobot](https://t.me/userinfobot)

### Configure credentials

Create a `.env` file in a secure location (example: `~/.env`):

```bash
nano ~/.env
```

Add these values:

```
LAPTOP_CONTROL_BOT_TOKEN=your_bot_token_here
TELEGRAM_USER_ID=your_user_id_here
LAPTOP_PASSWORD=your_laptop_password
```

Set secure permissions:

```bash
chmod 600 ~/.env
```

### Setup services

Copy bot service and update the paths in `laptop-control-bot.service`:

```ini
EnvironmentFile=/home/YOUR_USERNAME/.env
ExecStart=/usr/bin/python3 /path/to/laptop-control-bot.py
```

Install services:

```bash
# Copy service files
cp laptop-control-bot.service ~/.config/systemd/user/
cp ydotoold.service ~/.config/systemd/user/

# Enable and start
systemctl --user daemon-reload
systemctl --user enable --now ydotoold
systemctl --user enable --now laptop-control-bot
```

### Verify installation

```bash
systemctl --user status laptop-control-bot
systemctl --user status ydotoold
```

Check logs if needed:

```bash
journalctl --user -u laptop-control-bot -f
```

## Usage

Open your bot on Telegram and send `/start`. Use the keyboard buttons:

- **Lock Screen** - Lock immediately
- **Unlock** - Wake display and type password automatically
- **Status** - Show system information
- **Reboot** - Restart after confirmation
- **Shutdown** - Power off after confirmation

## Security Notes

Your laptop password is stored in plaintext in the `.env` file. Keep it secure:

- Set file permissions to 600
- Use a separate unlock password if possible
- Consider full disk encryption
- Only your Telegram user ID can control the bot

## Troubleshooting

### Unlock not working

Check if ydotoold is running:

```bash
systemctl --user status ydotoold
```

Test manually:

```bash
ydotool type test
```

### Bot not responding

Check service status and logs:

```bash
systemctl --user status laptop-control-bot
journalctl --user -u laptop-control-bot -n 50
```

### Permission errors

Add your user to the input group:

```bash
sudo usermod -aG input $USER
newgrp input
```

## How It Works

The bot runs as a systemd user service and connects to Telegram. On Wayland, it uses ydotool for input injection through a local socket. On X11, it falls back to xdotool. Only your whitelisted user ID can send commands.

## License

MIT License

## Author

[@MrElixir67](https://github.com/MrElixir67)
