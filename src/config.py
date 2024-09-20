import os
from dotenv import load_dotenv
import json

# Load env variables
load_dotenv() 

# Bot api token
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')
# Tunnel max duration
TUNNEL_DURATION = int(os.getenv('TUNNEL_DURATION', 3600)) # default to 1 hour

ADMINS = json.loads(os.environ['ADMINS'])