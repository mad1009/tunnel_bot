from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from dotenv import load_dotenv

import subprocess
import requests
import logging
import threading
import asyncio
import os
import json
import platform


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
        response = requests.get('https://loca.lt/mytunnelpassword')
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
        else:
            return "Password unavailable."
    except Exception as e:
        return f"Error fetching password: {e}"

# Get the path to the LocalTunnel executable
def get_localtunnel_path():
    if platform.system() == 'Windows':
        npm_global_path = os.path.join(os.getenv('APPDATA'), 'npm', 'lt.cmd')
        if os.path.exists(npm_global_path):
            return npm_global_path
        else:
            raise FileNotFoundError(
                f"LocalTunnel executable not found at {npm_global_path}. "
                "Ensure LocalTunnel is installed globally. You can install it using `npm install -g localtunnel`."
            )
    else:
        return 'lt'

def humanize_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{int(hours)} hours and {int(minutes)} minutes"
    else:
        return f"{int(minutes)} minutes"

def load_ports():
    try:
        with open('services.json') as f:
            return json.load(f)
    except Exception as e:
        return None


# Function to stop LocalTunnel after a set duration
def stop_tunnel_automatically():
    global localtunnel_process, auto_stop_timer
    if localtunnel_process:
        stop_localtunnel()

def start_localtunnel(service_name, port, duration=TUNNEL_DURATION):
    global localtunnel_process, public_url, password, auto_stop_timer, active_tunnels

    if service_name in active_tunnels:
        return f"LocalTunnel for {service_name} is already running."

    try:
        # Get the path to the LocalTunnel executable
        lt_path = get_localtunnel_path()

        # Start the LocalTunnel process with the specified port
        localtunnel_process = subprocess.Popen(
            [lt_path, '--port', str(port)],  # Use the specified port
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
                    
                    # Store the active tunnel
                    active_tunnels[service_name] = localtunnel_process

                    return (
                        f"Tunnel link for {service_name}: <b>{public_url}</b>\n\n"
                        f"Password (click to copy):     <b><code>{password}</code> \n\n</b>"
                        f"The tunnel will automatically stop after {humanize_duration(duration)}."
                    )
                else:
                    return f"LocalTunnel for {service_name} started: {public_url}\nFailed to retrieve password."

    except Exception as e:
        return f"Failed to start LocalTunnel for {service_name}: {e}"


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

# Load ports and services from the JSON file
services = load_ports().get('services', [])
active_tunnels = {}

# Function to present services in a list for selection
def get_service_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=service["name"], callback_data=f"start_tunnel:{service['name']}:{service['port']}")]
        for service in services
    ])
    
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
@dp.callback_query(lambda c: c.data.startswith('start_tunnel'))
async def process_start_tunnel(callback_query: CallbackQuery):
    # Extract service_name and port from callback data (assumes format: start_tunnel:service_name:port)
    data_parts = callback_query.data.split(':')
    service_name = data_parts[1]
    port = int(data_parts[2])

    # Start the tunnel using the selected service and port
    response = start_localtunnel(service_name=service_name, port=port)
    
    await callback_query.message.answer(response, parse_mode='HTML')
    await callback_query.answer()

# Function to present active services for stopping tunnels
def get_active_service_keyboard():
    # Create a list to hold the buttons
    buttons = []

    # Create a button for each active service
    for service_name in active_tunnels.keys():
        button = InlineKeyboardButton(text=service_name, callback_data=f"stop_tunnel:{service_name}")
        buttons.append([button])  # Each button needs to be in a separate list (row)

    # Return InlineKeyboardMarkup with the buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@dp.message(Command('stop_tunnel'))
async def stop_tunnel(message: types.Message):
    if active_tunnels:
        # Present the list of active services to stop
        await message.answer("Select a service to stop the tunnel:", reply_markup=get_active_service_keyboard())
    else:
        await message.answer("No tunnels are currently active.")


@dp.callback_query(lambda c: c.data.startswith('stop_tunnel'))
async def process_stop_tunnel(callback_query: CallbackQuery):
    service_name = callback_query.data.split(':')[1]  # Extract service name from callback data

    if service_name in active_tunnels:
        process = active_tunnels[service_name]

        try:
            # Terminate and ensure the process has fully exited
            process.terminate()
            process.wait()  # Ensure the process is completely stopped
            del active_tunnels[service_name]  # Remove from active tunnels
            await callback_query.message.answer(f"LocalTunnel for {service_name} stopped successfully.")
        except Exception as e:
            await callback_query.message.answer(f"Failed to stop LocalTunnel for {service_name}: {e}")
    else:
        await callback_query.message.answer(f"No active tunnel found for {service_name}.")

    await callback_query.answer()  # Remove the loading icon

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


@dp.message(Command('stop_tunnel'))
async def stop_tunnel(message: types.Message):
    if active_tunnels:
        # Present the list of active services to stop
        await message.answer("Select a service to stop the tunnel:", reply_markup=get_active_service_keyboard())
    else:
        await message.answer("No tunnels are currently active.")

@dp.message(Command('start_tunnel'))
async def start_tunnel(message: types.Message):
    # Present the list of available services to the user
    if services:
        await message.answer("Select a service to start the tunnel:", reply_markup=get_service_keyboard())
    else:
        await message.answer("No services available.")



# Telegram command: /stop_tunnel
@dp.message(Command('stop_tunnel'))
async def stop_tunnel(message: types.Message):
    response = stop_localtunnel()
    await message.answer(response)

# Telegram command: /status
@dp.message(Command('status'))
async def tunnel_status(message: types.Message):
    if not active_tunnels:
        await message.answer("No tunnels are currently active.")
        return
    
    # Collect status information for all active tunnels
    status_messages = []
    for service_name, process in active_tunnels.items():
        if process.poll() is None:
            # Process is still running
            status_message = f"{service_name}: Tunnel is running."
            if public_url:
                status_message += f" URL: {public_url}"
            if password:
                status_message += f" Password: {password}"
            status_messages.append(status_message + "\n\n\n" )
        else:
            # Process has terminated
            status_messages.append(f"{service_name}: Tunnel is not running.")
    
    # Send all status messages to the user
    if status_messages:
        await message.answer("\n".join(status_messages))
    else:
        await message.answer("No active tunnels found.")

# Main function to set up the Telegram bot
async def main():
    log = logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())