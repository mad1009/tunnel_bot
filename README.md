# LocalTunnel Telegram Bot

## Overview

The LocalTunnel Telegram Bot project automates the process of exposing a local web application to the internet using LocalTunnel. The bot, built with Python and the `aiogram` library, allows users to create, manage, and monitor LocalTunnel sessions through Telegram commands. It also handles automatic tunnel expiration and provides secure access to local services from anywhere.

## Features

- Start and stop LocalTunnel sessions.
- Retrieve and display the tunnel URL and password.
- Automatic tunnel termination after a specified duration.
- User-friendly Telegram interface with command support.

## Installation

Follow these steps to set up and install the LocalTunnel Telegram Bot:

1. **Clone the Repository**

   Clone the repository to your local machine:

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo

2. **Run the Setup Script**
    Execute the setup script to set up the Python environment, install dependencies, and configure Supervisor:
   ```bash
   bash ./install.sh

2. **Create a telegram bot**
    Follow this tutorial to create a [telegram bot](https://docs.radist.online/docs/our-products/radist-web/connections/telegram-bot/instructions-for-creating-and-configuring-a-bot-in-botfather)


4. **Configure Environment Variables**
    Create a .env file in the root directory of the project with the following content:
   ```bash
    BOT_TOKEN=your-telegram-bot-token
    TARGET_PORT=your-local-port
    TUNNEL_DURATION=3600
    ```
    Replace your-telegram-bot-token with your Telegram bot token, your-local-port with the port of your local service, and 3600 with the desired tunnel duration in seconds.

5. **Start Supervisor**
    Ensure Supervisor is managing the bot script. Load the configuration and start the service:
   ```bash
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start localtunnel_manager
    ```
    Replace your-telegram-bot-token with your Telegram bot token, your-local-port with the port of your local service, and 3600 with the desired tunnel duration in seconds.

6. **Usage**
    - /start_tunnel: Initiate a LocalTunnel session.
    - /stop_tunnel: Terminate the current LocalTunnel session.
    - /status: Check the status of the LocalTunnel session.

## Licence

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any questions or feedback, please contact [Mad](mailto:moadakharraz.@gmail.com).

## Contribution

Contributions are welcome! If you find any issues or have suggestions for improvements, please submit an issue or a pull request. Make sure to follow the project's coding standards and guidelines.

This project is intended for fun and personal use only. I do not take any responsibility for any errors or issues that may occur while using this project. Use it at your own risk.

