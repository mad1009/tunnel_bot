#!/bin/bash

set -e  # Exit on error

# Define variables
APP_NAME="localtunnel_manager"  # Change this to your application name
VENV_DIR="venv"
SCRIPT_NAME="main.py"
INSTALL_SCRIPT="../setup_env.sh"
SUPERVISOR_CONF_DIR="/etc/supervisor/conf.d"
SUPERVISOR_CONF_FILE="$SUPERVISOR_CONF_DIR/${APP_NAME}.conf"
LOG_DIR="/var/log/supervisor"
APP_LOG_DIR="$LOG_DIR/$APP_NAME"

# Function to clean up previous steps
cleanup() {
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
    fi
    echo "Cleanup complete."
}

# Set up a trap to run cleanup on errors
trap cleanup ERR

echo "Install virtualenv"
sudo apt-get update
sudo  apt install virtualenv


# Check and install supervisorctl if necessary
if ! command -v supervisorctl &> /dev/null; then
    echo "supervisorctl not found. Installing it..."
    sudo apt-get update
    sudo apt-get install -y supervisor
fi

# Check and install Node.js and npm if necessary
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_current.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

if ! command -v npm &> /dev/null; then
    echo "npm not found. Installing npm..."
    sudo apt-get install -y npm
fi

# Check and install localtunnel globally
if ! npm list -g localtunnel &> /dev/null; then
    echo "localtunnel not found. Installing it globally..."
    sudo npm install -g localtunnel
fi

# Create and activate the virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating a new one..."
    virtualenv  "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# Upgrade pip and install requirements
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping package installation."
fi

# Create Supervisor configuration for main.py
if [ ! -d "$SUPERVISOR_CONF_DIR" ]; then
    echo "Supervisor configuration directory $SUPERVISOR_CONF_DIR not found. Please ensure Supervisor is installed correctly."
    exit 1
fi

echo "Creating Supervisor configuration file..."

sudo tee "$SUPERVISOR_CONF_FILE" > /dev/null <<EOL
[program:$APP_NAME]
command=${VENV_DIR}/bin/python ${SCRIPT_NAME}
directory=$(pwd)
autostart=true
autorestart=true
stderr_logfile=${APP_LOG_DIR}/$APP_NAME.err.log
stdout_logfile=${APP_LOG_DIR}/$APP_NAME.out.log
EOL

# Create log directory if it does not exist
sudo mkdir -p "$APP_LOG_DIR"

# Update Supervisor and restart
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart $APP_NAME

echo "Setup complete. Virtual environment is activated, Supervisor is configured, and the script is running."
