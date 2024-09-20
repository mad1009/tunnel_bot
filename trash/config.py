import os
import platform
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_PORT = int(os.getenv('TARGET_PORT'))
TUNNEL_DURATION = int(os.getenv('TUNNEL_DURATION', 3600))

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
