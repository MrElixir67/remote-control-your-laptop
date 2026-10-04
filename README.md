# Remote Control Your Laptop 🖥️📱

Control your laptop remotely via Telegram bot - lock, unlock, reboot, shutdown, and check status from your phone!

## Features

- 🔒 **Lock Screen** - Lock laptop remotely
- 🔓 **Unlock** - Auto-type password and unlock (Wayland/X11)
- 📊 **Status** - Check uptime, load average, and memory usage
- 🔄 **Reboot** - Restart laptop with confirmation
- ⚡ **Shutdown** - Power off laptop with confirmation
- 🔐 **Security** - Whitelist your Telegram user ID only

## Screenshots

Persistent keyboard interface with buttons for quick access:

```
🔒 Lock Screen    🔓 Unlock
📊 Status
🔄 Reboot         ⚡ Shutdown
```

## Requirements

- Ubuntu/Debian Linux (tested on Ubuntu 26.04)
- Python 3.10+
- Telegram Bot Token
- Wayland or X11 session

## Installation

### 1. Install Dependencies

```bash
# Python Telegram Bot library
pip3 install python-telegram-bot --user

# For Wayland (Ubuntu 26.04+)
sudo apt install -y ydotool util-linux-extra

# For X11 (optional fallback)
sudo apt install -y xdotool
```

### 2. Clone Repository

```bash
git clone https://github.com/MrElixir67/remote-control-your-laptop.git
cd remote-control-your-laptop
```

### 3. Setup Telegram Bot

1. Chat with [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)

### 4. Configure Environment

Create `.env` file in your home directory (or anywhere safe):

```bash
nano ~/.env
```

Add these lines:

```env
LAPTOP_CONTROL_BOT_TOKEN=your_bot_token_here
TELEGRAM_USER_ID=your_telegram_user_id
LAPTOP_PASSWORD=your_laptop_password
```

**⚠️ Security Warning:** Your laptop password is stored in plaintext. Keep `.env` file permissions locked:

```bash
chmod 600 ~/.env
```

### 5. Setup Systemd Services

#### ydotoold daemon (for Wayland)

```bash
mkdir -p ~/.config/systemd/user
cp ydotoold.service ~/.config/systemd/user/
systemctl --user enable --now ydotoold
```

#### Laptop Control Bot

Edit `laptop-control-bot.service` and update the paths:

```ini
EnvironmentFile=/home/YOUR_USERNAME/.env
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/remote-control-laptop/laptop-control-bot.py
```

Then install:

```bash
cp laptop-control-bot.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now laptop-control-bot
```

### 6. Verify Installation

Check services are running:

```bash
systemctl --user status ydotoold
systemctl --user status laptop-control-bot
```

Check logs:

```bash
journalctl --user -u laptop-control-bot -f
```

## Usage

1. Open your Telegram bot
2. Send `/start`
3. Use the persistent keyboard buttons to control your laptop

### Commands

- **🔒 Lock Screen** - Immediately locks the screen
- **🔓 Unlock** - Wakes display and auto-types password
- **📊 Status** - Shows system information (uptime, load, memory)
- **🔄 Reboot** - Asks confirmation, then reboots
- **⚡ Shutdown** - Asks confirmation, then shuts down

## How It Works

### Wayland Support

On Wayland sessions, the bot uses `ydotool` for input injection:
- `ydotoold` daemon runs in the background
- Bot sends input commands via `/run/user/$UID/.ydotool_socket`
- Works across all Wayland compositors (GNOME, KDE, Sway, etc.)

### X11 Fallback

On X11 sessions, the bot falls back to `xdotool`:
- Direct X11 input injection
- No daemon required

### Security

- Only whitelisted Telegram user ID can control the bot
- All other users receive "❌ Unauthorized" message
- Password stored locally, never transmitted to Telegram servers
- Bot runs as user service (no root required)

## Troubleshooting

### Unlock doesn't work

**On Wayland:**
```bash
# Check ydotoold is running
systemctl --user status ydotoold

# Check socket exists
ls -la /run/user/$(id -u)/.ydotool_socket

# Test manually
ydotool type test
```

**On X11:**
```bash
# Check xdotool is installed
which xdotool

# Test manually
xdotool type test
```

### Bot doesn't respond

```bash
# Check bot service
systemctl --user status laptop-control-bot

# Check logs
journalctl --user -u laptop-control-bot -n 50
```

### Permission denied errors

```bash
# Add user to input group (required for ydotool)
sudo usermod -aG input $USER

# Logout and login, or run:
newgrp input
```

## Auto-Start on Boot

Both services are configured to auto-start:

```bash
systemctl --user list-unit-files | grep enabled
# Should show:
# laptop-control-bot.service  enabled
# ydotoold.service            enabled
```

## Uninstall

```bash
# Stop and disable services
systemctl --user stop laptop-control-bot ydotoold
systemctl --user disable laptop-control-bot ydotoold

# Remove files
rm ~/.config/systemd/user/laptop-control-bot.service
rm ~/.config/systemd/user/ydotoold.service
rm -rf ~/remote-control-laptop

# Remove credentials (optional)
rm ~/.env

systemctl --user daemon-reload
```

## Security Considerations

1. **Password Storage**: Your laptop password is stored in plaintext in `.env`. Consider:
   - Using full disk encryption
   - Setting strong file permissions (`chmod 600`)
   - Using a separate unlock password vs. your main password
   - Disabling lock screen if laptop is in a secure location

2. **Telegram Bot Token**: Keep your bot token private. If compromised:
   - Revoke the token via @BotFather
   - Generate a new bot

3. **Network Security**: 
   - Bot communicates via Telegram's encrypted API
   - No ports opened on your laptop
   - Works behind NAT/firewall

## Contributing

Pull requests welcome! Feel free to:
- Add new features
- Improve security
- Support more platforms
- Fix bugs

## License

MIT License - feel free to use and modify!

## Author

Built by [@MrElixir67](https://github.com/MrElixir67) with ❤️

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [ydotool](https://github.com/ReimuNotMoe/ydotool) - Generic Linux command-line automation tool (Wayland)
- [xdotool](https://github.com/jordansissel/xdotool) - X11 automation tool

---

**⚠️ Use responsibly! Remote control tools can be dangerous if misconfigured.**
