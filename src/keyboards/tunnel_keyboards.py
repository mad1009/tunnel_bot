from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

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

def get_service_keyboard(services):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=service["name"], callback_data=f"start_tunnel:{service['name']}:{service['port']}")]
        for service in services
    ])
    
    return keyboard

def get_active_service_keyboard(active_tunnels):
    # Create a list to hold the buttons
    buttons = []

    # Create a button for each active service
    for service_name in active_tunnels.keys():
        button = InlineKeyboardButton(text=service_name, callback_data=f"stop_tunnel:{service_name}")
        buttons.append([button])  # Each button needs to be in a separate list (row)

    # Return InlineKeyboardMarkup with the buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
