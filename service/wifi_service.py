from .decorators import retry_on_exception
import subprocess
import netifaces
import wifi
import os

class WifiService(object):
    @classmethod
    @retry_on_exception(max_retries=5, fail_response=[])
    def list_wifi_networks(cls):
        interfaces = cls.wifi_interfaces()

        if len(interfaces) <= 0:
            return []

        interface = interfaces[0]
        wifi_networks = wifi.Cell.all(interface)

        result = []

        for network in wifi_networks:
            signal = network.signal
            quality = 0

            if signal <= -100:
                quality = 0
            elif signal >= -40:
                quality = 100
            else:
                quality = (5/3) * (signal + 100)

            result.append({
                "SSID": network.ssid,
                "quality": int(quality),
                "encrypted": network.encrypted
            })

        return result

    @classmethod
    def connect(cls, ssid, password=""):
        try:
            command = f"nmcli dev wifi connect \"{ssid}\""

            if password:
                command += f" password \"{password}\""

            result = os.system(command)

            if result == 0:
                return {
                    "error": None,
                    "message": f"Connected to {ssid} sucessfully"
                }
        except:
            pass

        return {
            "error": f"Failed to connect to {ssid}",
            "message": None
        }

    @classmethod
    @retry_on_exception(max_retries=5, fail_response=[])
    def wifi_interfaces(cls):
        wifi_interfaces = []
        interfaces = netifaces.interfaces()

        for interface in interfaces:
            if len(interface) > 1 and interface[:2] == "wl":
                wifi_interfaces.append(interface)

        return wifi_interfaces

    @classmethod
    @retry_on_exception(max_retries=5, fail_response=None)
    def current_wifi(cls):
        result = subprocess.check_output([
            "iwgetid", "-r"
        ])

        return result.decode("utf-8").strip()

    @classmethod
    @retry_on_exception(max_retries=5, fail_response=None)
    def wifi_info(cls, ssid):
        wifi_list = cls.list_wifi_networks()

        for wifi in wifi_list:
            if ssid == wifi["SSID"]:
                return wifi

        return None
