import subprocess
import requests
import logging
import threading
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import os
import platform
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Telegram bot token (replace with your bot's token from BotFather)
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_PORT = int(os.getenv('TARGET_PORT'))
TUNNEL_DURATION = int(os.getenv('TUNNEL_DURATION', 3600))

# Initialize variables
localtunnel_process = None
public_url = None
password = None
auto_stop_timer = None

# Initialize Bot and Dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Function to fetch the LocalTunnel password
def fetch_password():
    try:
        # Send a GET request to retrieve the password
        response = requests.get('https://loca.lt/mytunnelpassword')

        if response.status_code == 200:
            return response.text.strip()
        else:
            return None
    except Exception as e:
        return f"Error fetching password: {e}"

# Get the path to the LocalTunnel executable
def get_localtunnel_path():
    if platform.system() == 'Windows':
        npm_global_path = os.path.join(os.getenv('APPDATA'), 'npm', 'lt.cmd')
        if os.path.exists(npm_global_path):
            return npm_global_path
        else:
            raise FileNotFoundError(f"'lt' executable not found at {npm_global_path}. "
                                    "Make sure LocalTunnel is installed globally.")
    else:
        return 'lt'

def humanize_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{int(hours)} hours and {int(minutes)} minutes"
    else:
        return f"{int(minutes)} minutes"

# Function to stop LocalTunnel after a set duration
def stop_tunnel_automatically():
    global localtunnel_process, auto_stop_timer
    if localtunnel_process:
        stop_localtunnel()

# Start LocalTunnel
def start_localtunnel(port=TARGET_PORT, duration=TUNNEL_DURATION):
    global localtunnel_process, public_url, password, auto_stop_timer

    if localtunnel_process is not None:
        return "LocalTunnel is already running."

    try:
        # Get the path to the LocalTunnel executable
        lt_path = get_localtunnel_path()

        # Start the LocalTunnel process
        localtunnel_process = subprocess.Popen(
            [lt_path, '--port', str(port)],  # Use the full path to lt if needed
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Capture the public URL from the process output
        for line in localtunnel_process.stdout:
            if 'your url is' in line.lower():
                public_url = line.split()[-1]

                # Fetch the password for the tunnel
                password = fetch_password()
                if password:
                    # Start a timer to automatically stop the tunnel after the given duration
                    auto_stop_timer = threading.Timer(duration, stop_tunnel_automatically)
                    auto_stop_timer.start()
                    
                    return(
                        f"Tunnel link: <b>{public_url}</b>\n\n"
                        f"Password (click to copy):     <b><code>{password}</code> \n\n</b>"
                        f"The tunnel will automatically stop after {humanize_duration(duration)}.")
                else:
                    return f"LocalTunnel started: {public_url}\nFailed to retrieve password."

    except Exception as e:
        return f"Failed to start LocalTunnel: {e}"

# Stop LocalTunnel
def stop_localtunnel():
    global localtunnel_process, auto_stop_timer

    if localtunnel_process is None:
        return "LocalTunnel is not running."

    try:
        localtunnel_process.terminate()
        localtunnel_process = None

        # Cancel the auto-stop timer if the tunnel is stopped manually
        if auto_stop_timer:
            auto_stop_timer.cancel()
            auto_stop_timer = None

        return "LocalTunnel stopped successfully."

    except Exception as e:
        return f"Failed to stop LocalTunnel: {e}"

# Start command with buttons
# Define a persistent keyboard
def get_persistent_keyboard():
    # Create the keyboard layout with resize_keyboard set to True
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start_tunnel")],
            [KeyboardButton(text="/stop_tunnel")],
            [KeyboardButton(text="/status")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Start command with persistent keyboard
@dp.message(Command('start'))
async def start(message: types.Message):
    intro_message = (
        "Welcome to the LocalTunnel Bot!\n\n"
        "This bot allows you to create and manage temporary LocalTunnel URLs for accessing local services.\n"
        "Here are the available commands:"
    )
    
    # Send the welcome message with the persistent keyboard
    await message.answer(intro_message, reply_markup=get_persistent_keyboard())

# Callback query handler for Start Tunnel
@dp.callback_query(lambda c: c.data == 'start_tunnel')
async def process_start_tunnel(callback_query: CallbackQuery):
    # Start the tunnel and respond to the user
    response = start_localtunnel()  # Call your function to start the tunnel
    for msg in response:
        await callback_query.message.answer(msg, parse_mode='HTML')
    await callback_query.answer()  # Answer the callback to remove the loading icon

# Callback query handler for Stop Tunnel
@dp.callback_query(lambda c: c.data == 'stop_tunnel')
async def process_stop_tunnel(callback_query: CallbackQuery):
    # Stop the tunnel and respond to the user
    response = stop_localtunnel()  # Call your function to stop the tunnel
    await callback_query.message.answer(response)
    await callback_query.answer()

# Callback query handler for Tunnel Status
@dp.callback_query(lambda c: c.data == 'status_tunnel')
async def process_tunnel_status(callback_query: CallbackQuery):
    # Check the status of the tunnel and respond to the user
    global public_url, password
    if localtunnel_process:
        status_message = f"LocalTunnel is running: {public_url}"
        
        if password:
            status_message += f"\nPassword: {password}"
        await callback_query.message.answer(status_message)
    else:
        await callback_query.message.answer("LocalTunnel is not running.")
    await callback_query.answer()

# Telegram command: /start_tunnel
@dp.message(Command('start_tunnel'))
async def start_tunnel(message: types.Message):
    response = start_localtunnel()
    logging.info(f"New tunnel created: {message.from_user.full_name}")
    await message.answer(response, parse_mode="HTML")

# Telegram command: /stop_tunnel
@dp.message(Command('stop_tunnel'))
async def stop_tunnel(message: types.Message):
    response = stop_localtunnel()
    await message.answer(response)

# Telegram command: /status
@dp.message(Command('status'))
async def tunnel_status(message: types.Message):
    global public_url, password
    if localtunnel_process:
        status_message = f"LocalTunnel is running: {public_url}"
        if password:
            status_message += f"\nPassword: {password}"
        await message.answer(status_message)
    else:
        await message.answer("LocalTunnel is not running.")

# Main function to set up the Telegram bot
async def main():
    log = logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
