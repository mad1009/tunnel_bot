import subprocess
import threading
import requests
import logging

from config import TUNNEL_DURATION
from utils import load_services, get_localtunnel_path, humanize_duration


class TunnelManager:
    def __init__(self):
        # format {'service_name': {'url':'xxxx', 'password': 'xxxx', process: Process Object}}
        self.active_tunnels = {}
        self.services = load_services().get('services', [])

    def fetch_password(self):
        try:
            response = requests.get('https://loca.lt/mytunnelpassword')
            if response.status_code == 200 and response.text.strip():
                return response.text.strip()
            else:
                return "Password unavailable."
        except Exception as e:
            logging.error(str(e))
            return f"Error fetching password: {e}"

    def start_localtunnel(self, service_name, port, duration=TUNNEL_DURATION):
        # Check if service tunnel aleady exist
        if service_name in self.active_tunnels:
            return f"LocalTunnel for {service_name} is already running."

        try:
            # Create tunnel process
            lt_path = get_localtunnel_path()
            localtunnel_process = subprocess.Popen(
                [lt_path, '--port', str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            for line in localtunnel_process.stdout:
                if 'your url is' in line.lower():
                    public_url = line.split()[-1]
                    password = self.fetch_password()
                    if password:
                        # Kill tunnel process after the specified duration
                        auto_stop_timer = threading.Timer(duration, self.stop_localtunnel, (service_name, ))
                        auto_stop_timer.start()
                        # Add tunnel to active tunnels dict
                        self.active_tunnels[service_name] = {
                            "process": localtunnel_process,
                            "password": password,
                            "url": public_url
                        }
                        return (
                            f"Tunnel link for {service_name}: <b>{public_url}</b>\n\n"
                            f"Password (click to copy): <b><code>{password}</code> \n\n</b>"
                            f"The tunnel will automatically stop after {humanize_duration(duration)}."
                        )
                    else:
                        # if password failed kill tunnel process
                        localtunnel_process.terminate()
                        return f"Failed to retrieve password for {service_name}.\nTry again later"
        except Exception as e:
            logging.error(str(e))
            return f"Failed to start LocalTunnel for {service_name}: {e}"


    def stop_localtunnel(self, service_name):
        if service_name not in self.active_tunnels:
            return f"{service_name} is not running a local tunnel"
        try:
            self.active_tunnels[service_name]["process"].terminate()
            return f"{service_name} tunnel stopped successfully."
        except Exception as e:
            logging.error(str(e))
            return f"Failed to stop {service_name} tunnel: {e}"

    def status_tunnels(self):
        try:
            if not self.active_tunnels:
                return "No tunnels are currently active."
            print(self.active_tunnels)
            # Collect status information for all active tunnels
            status_messages = []
            for service_name in self.active_tunnels.keys():
                text = (
                    f"Tunnel <b>{service_name}</b> is running.\n\n"
                    f"URL: {self.active_tunnels[service_name]['url']}\n\n"
                    f"Code: <code>{self.active_tunnels[service_name]['password']}</code>"
                )
                status_messages.append(text + "\n\n\n")
            return "\n".join(status_messages)
        except Exception as e:
            logging.error(str(e))
            return f"Failed to get tunnels status: {e}"
