#!/usr/bin/env python3
"""
Laptop Control Bot - Remote control laptop via Telegram
Security: Whitelist user ID only
"""
import os
import subprocess
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load config
BOT_TOKEN = os.getenv("LAPTOP_CONTROL_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

if not BOT_TOKEN:
    raise ValueError("LAPTOP_CONTROL_BOT_TOKEN not set in .env")
if ALLOWED_USER_ID == 0:
    raise ValueError("TELEGRAM_USER_ID not set in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_auth(user_id: int) -> bool:
    """Only allow whitelisted user"""
    return user_id == ALLOWED_USER_ID

def run_command(cmd: list[str]) -> tuple[bool, str]:
    """Execute system command safely"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout or result.stderr
    except Exception as e:
        return False, str(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main control panel"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    # Force remove keyboard completely first
    from telegram import ReplyKeyboardRemove
    await update.message.reply_text(
        "🔄 Resetting keyboard...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Wait a moment
    import asyncio
    await asyncio.sleep(0.5)
    
    # Send new keyboard
    keyboard = [
        [KeyboardButton("🔒 Lock Screen"), KeyboardButton("🔓 Unlock")],
        [KeyboardButton("🔄 Reboot"), KeyboardButton("⚡ Shutdown")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
    
    await update.message.reply_text(
        "🖥️ *Laptop Control Panel*\n\n"
        "Gunakan keyboard di bawah untuk kontrol laptop:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle keyboard button presses"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    text = update.message.text
    
    # Lock screen
    if text == "🔒 Lock Screen":
        success, output = run_command(["loginctl", "lock-session"])
        if success:
            await update.message.reply_text("🔒 Screen locked!")
        else:
            await update.message.reply_text(f"❌ Lock failed:\n{output}")
    
    # Unlock (wake + auto-type password)
    elif text == "🔓 Unlock":
        password = os.getenv("LAPTOP_PASSWORD")
        if not password:
            await update.message.reply_text("❌ Password belum diset!\n\nTambahkan di .env:\n`LAPTOP_PASSWORD=password_lu`")
            return
        
        # Wake display
        run_command(["xset", "dpms", "force", "on"])
        
        # Wait for lock screen
        import time
        time.sleep(2)
        
        # Try ydotool first (Wayland), fallback to xdotool (X11)
        success, _ = run_command(["ydotool", "type", password])
        if success:
            time.sleep(0.3)
            run_command(["ydotool", "key", "28:1", "28:0"])  # Enter key
            await update.message.reply_text("🔓 Unlocked!")
        else:
            # Fallback to xdotool
            success2, _ = run_command(["xdotool", "type", "--clearmodifiers", password])
            if success2:
                run_command(["xdotool", "key", "Return"])
                await update.message.reply_text("🔓 Unlocked!")
            else:
                await update.message.reply_text("❌ Unlock failed\n\nInstall ydotool (Wayland):\n`sudo apt install ydotool`\n`sudo systemctl enable --now ydotool`")
    

    # Reboot
    elif text == "🔄 Reboot":
        # Store pending action
        context.user_data['pending_action'] = 'reboot'
        keyboard = [[KeyboardButton("✅ Confirm Reboot"), KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "⚠️ *Confirm Reboot?*\n\nLaptop will restart immediately.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    # Shutdown
    elif text == "⚡ Shutdown":
        context.user_data['pending_action'] = 'shutdown'
        keyboard = [[KeyboardButton("✅ Confirm Shutdown"), KeyboardButton("❌ Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "⚠️ *Confirm Shutdown?*\n\nLaptop will power off immediately.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    # Confirm reboot
    elif text == "✅ Confirm Reboot":
        # Restore main keyboard
        keyboard = [
            [KeyboardButton("🔒 Lock Screen"), KeyboardButton("🔓 Unlock")],
            [KeyboardButton("🔄 Reboot"), KeyboardButton("⚡ Shutdown")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
        await update.message.reply_text("🔄 Rebooting laptop...", reply_markup=reply_markup)
        subprocess.Popen(["systemctl", "reboot"])
    
    # Confirm shutdown
    elif text == "✅ Confirm Shutdown":
        keyboard = [
            [KeyboardButton("🔒 Lock Screen"), KeyboardButton("🔓 Unlock")],
            [KeyboardButton("🔄 Reboot"), KeyboardButton("⚡ Shutdown")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
        await update.message.reply_text("⚡ Shutting down laptop...", reply_markup=reply_markup)
        subprocess.Popen(["systemctl", "poweroff"])
    
    # Cancel
    elif text == "❌ Cancel":
        context.user_data.pop('pending_action', None)
        keyboard = [
            [KeyboardButton("🔒 Lock Screen"), KeyboardButton("🔓 Unlock")],
            [KeyboardButton("🔄 Reboot"), KeyboardButton("⚡ Shutdown")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)
        await update.message.reply_text("Cancelled.", reply_markup=reply_markup)

def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("🤖 Laptop Control Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
