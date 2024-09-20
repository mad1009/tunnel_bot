from aiogram.filters import Command
from aiogram import Router
from aiogram.types import Message, CallbackQuery

from localtunnel.tunnel_manager import TunnelManager
from keyboards.tunnel_keyboards import get_persistent_keyboard, get_service_keyboard, get_active_service_keyboard
from middlewares.auth import AuthorizationMiddleware

tunnel_manager = TunnelManager()

router = Router()

router.message.middleware(AuthorizationMiddleware())
router.callback_query.middleware(AuthorizationMiddleware())

@router.message(Command("start"))
async def cmd_start(message: Message):
    intro_message = (
        "Welcome to the LocalTunnel Bot!\n\n"
        "This bot allows you to create and manage temporary LocalTunnel URLs for accessing local services.\n"
        "Here are the available commands:"
    )
    await message.answer(intro_message, reply_markup=get_persistent_keyboard())


@router.message(Command('start_tunnel'))
async def start_tunnel(message: Message):
    # Present the list of available services to the user
    if tunnel_manager.services:
        await message.answer("Select a service to start the tunnel:", reply_markup=get_service_keyboard(tunnel_manager.services))
    else:
        await message.answer("No services available.")


# Callback query handler for Start Tunnel
@router.callback_query(lambda c: c.data.startswith('start_tunnel'))
async def process_start_tunnel(callback_query: CallbackQuery):
    # Extract service_name and port from callback data (format: start_tunnel:service_name:port)
    data_parts = callback_query.data.split(':')
    service_name = data_parts[1]
    port = int(data_parts[2])

    # Start the tunnel using the selected service and port
    response = tunnel_manager.start_localtunnel(service_name=service_name, port=port)
    
    await callback_query.message.answer(response, parse_mode='HTML')
    await callback_query.answer()


@router.message(Command('stop_tunnel'))
async def stop_tunnel(message: Message):
    if tunnel_manager.active_tunnels:
        # Present the list of active services to stop
        await message.answer("Select a service to stop the tunnel:", reply_markup=get_active_service_keyboard(active_tunnels=tunnel_manager.active_tunnels))
    else:
        await message.answer("No tunnels are currently active.")



@router.callback_query(lambda c: c.data.startswith('stop_tunnel'))
async def process_stop_tunnel(callback_query: CallbackQuery):
    service_name = callback_query.data.split(':')[1]  # Extract service name from callback data (format: stop_tunnel:service_name)

    if service_name in tunnel_manager.active_tunnels:
        response = tunnel_manager.stop_localtunnel(service_name)
    else:
        response = f"No active tunnel found for {service_name}."
    await callback_query.message.answer(response)
    await callback_query.answer()  # Remove the loading icon


# Callback query handler for Tunnel Status
@router.message(Command("status"))
async def tunnel_status(message: Message):
    response = tunnel_manager.status_tunnels()
    await message.answer(response, parse_mode='HTML')
