import subprocess
import threading
import requests
import json
from config import get_localtunnel_path, TUNNEL_DURATION

class LocalTunnelManager:
    def __init__(self):
        self.localtunnel_process = None
        self.public_url = None
        self.password = None
        self.auto_stop_timer = None
        self.active_tunnels = {}
        self.services = self.load_ports().get('services', [])

    def fetch_password(self):
        try:
            response = requests.get('https://loca.lt/mytunnelpassword')
            if response.status_code == 200 and response.text.strip():
                return response.text.strip()
            else:
                return "Password unavailable."
        except Exception as e:
            return f"Error fetching password: {e}"

    def start_localtunnel(self, service_name, port, duration=TUNNEL_DURATION):
        if service_name in self.active_tunnels:
            return f"LocalTunnel for {service_name} is already running."

        try:
            lt_path = get_localtunnel_path()
            self.localtunnel_process = subprocess.Popen(
                [lt_path, '--port', str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            for line in self.localtunnel_process.stdout:
                if 'your url is' in line.lower():
                    self.public_url = line.split()[-1]
                    self.password = self.fetch_password()
                    if self.password:
                        self.auto_stop_timer = threading.Timer(duration, self.stop_tunnel_automatically)
                        self.auto_stop_timer.start()
                        self.active_tunnels[service_name] = self.localtunnel_process
                        return (
                            f"Tunnel link for {service_name}: <b>{self.public_url}</b>\n\n"
                            f"Password (click to copy): <b><code>{self.password}</code> \n\n</b>"
                            f"The tunnel will automatically stop after {self.humanize_duration(duration)}."
                        )
                    else:
                        return f"LocalTunnel for {service_name} started: {self.public_url}\nFailed to retrieve password."
        except Exception as e:
            return f"Failed to start LocalTunnel for {service_name}: {e}"

    def stop_localtunnel(self):
        if self.localtunnel_process is None:
            return "LocalTunnel is not running."

        try:
            self.localtunnel_process.terminate()
            self.localtunnel_process = None

            if self.auto_stop_timer:
                self.auto_stop_timer.cancel()
                self.auto_stop_timer = None

            return "LocalTunnel stopped successfully."
        except Exception as e:
            return f"Failed to stop LocalTunnel: {e}"

    def stop_tunnel_automatically(self):
        if self.localtunnel_process:
            self.stop_localtunnel()

    def humanize_duration(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{int(hours)} hours and {int(minutes)} minutes"
        else:
            return f"{int(minutes)} minutes"

    def load_ports(self):
        try:
            with open('services.json') as f:
                return json.load(f)
        except Exception as e:
            return None
