import os
import platform
import json


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


def load_services():
    try:
        with open('services.json') as f:
            return json.load(f)
    except Exception as e:
        return None


def humanize_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{int(hours)} hours and {int(minutes)} minutes"
    else:
        return f"{int(minutes)} minutes"

