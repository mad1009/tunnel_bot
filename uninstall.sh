APP_NAME="localtunnel_manager"
VENV_DIR="venv"
SCRIPT_NAME="bot.py"
SUPERVISOR_CONF_DIR="/etc/supervisor/conf.d"
SUPERVISOR_CONF_FILE="$SUPERVISOR_CONF_DIR/${APP_NAME}.conf"
LOG_DIR="/var/log/supervisor"
APP_LOG_DIR="$LOG_DIR/$APP_NAME"

set -e  # Exit on error

echo "Cleaning up..."
if [ -d "$VENV_DIR" ]; then
    echo "Removing virtual environment..."
    rm -rf "$VENV_DIR"
fi
if [ -f "$SUPERVISOR_CONF_FILE" ]; then
    echo "Removing Supervisor configuration..."
    sudo rm "$SUPERVISOR_CONF_FILE"
    sudo supervisorctl reread
    sudo supervisorctl update
fi
if [ -d "$APP_LOG_DIR" ]; then
    echo "Removing log directory..."
    cat "$APP_LOG_DIR/$APP_NAME.err.log"
    sudo rm -rf "$APP_LOG_DIR"
    echo "Cleanup success"
fi