from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from localtunnel import LocalTunnelManager
from keyboard import get_persistent_keyboard, get_service_keyboard, get_active_service_keyboard

# Create an instance of LocalTunnelManager
manager = LocalTunnelManager()

async def start(message: types.Message):
    intro_message = (
        "Welcome to the LocalTunnel Bot!\n\n"
        "This bot allows you to create and manage temporary LocalTunnel URLs for accessing local services.\n"
        "Here are the available commands:"
    )
    await message.answer(intro_message, reply_markup=get_persistent_keyboard())

async def process_start_tunnel(callback_query: CallbackQuery):
    data_parts = callback_query.data.split(':')
    service_name = data_parts[1]
    port = int(data_parts[2])
    response = manager.start_localtunnel(service_name=service_name, port=port)
    await callback_query.message.answer(response, parse_mode='HTML')
    await callback_query.answer()

async def process_stop_tunnel(callback_query: CallbackQuery):
    service_name = callback_query.data.split(':')[1]
    if service_name in manager.active_tunnels:
        process = manager.active_tunnels[service_name]
        try:
            process.terminate()
            process.wait()
            del manager.active_tunnels[service_name]
            await callback_query.message.answer(f"LocalTunnel for {service_name} stopped successfully.")
        except Exception as e:
            await callback_query.message.answer(f"Failed to stop LocalTunnel for {service_name}: {e}")
    else:
        await callback_query.message.answer(f"No active tunnel found for {service_name}.")
    await callback_query.answer()

async def process_tunnel_status(callback_query: CallbackQuery):
    if manager.localtunnel_process:
        status_message = f"LocalTunnel is running: {manager.public_url}"
        if manager.password:
            status_message += f"\nPassword: {manager.password}"
        await callback_query.message.answer(status_message)
    else:
        await callback_query.message.answer("LocalTunnel is not running.")
    await callback_query.answer()

async def stop_tunnel(message: types.Message):
    if manager.active_tunnels:
        # Present the list of active services to stop
        await message.answer("Select a service to stop the tunnel:", reply_markup=get_active_service_keyboard(manager.active_tunnels))
    else:
        await message.answer("No tunnels are currently active.")

async def start_tunnel(message: types.Message):
    # Present the list of available services to the user
    if manager.services:
        await message.answer("Select a service to start the tunnel:", reply_markup=get_service_keyboard(manager.services))
    else:
        await message.answer("No services available.")
