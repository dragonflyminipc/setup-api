from .decorators import retry_on_exception
from .utils import shell_command
from typing import Union
import netifaces
import logging


class NmcliResponseHandler(object):
    @classmethod
    def generic_check(cls, status_code: int, message: str):
        if status_code == 2:
            return {
                "error": "wrong-nmcli-invocation",
                "message": None,
            }

        elif status_code == 3:
            return {
                "error": "timeout",
                "message": None,
            }

        elif status_code == 4:
            return {
                "error": "activation-failed",
                "message": None,
            }

        elif status_code == 5:
            return {
                "error": "deactivation-failed",
                "message": None,
            }

        elif status_code == 6:
            return {
                "error": "disconnecting-failed",
                "message": None,
            }

        elif status_code == 7:
            return {
                "error": "deletion-failed",
                "message": None,
            }

        elif status_code == 8:
            return {
                "error": "networkmanager-not-running",
                "message": None,
            }

        elif status_code == 10:
            return {
                "error": "not-found",
                "message": None,
            }

        elif status_code == 127:
            return {
                "error": "nmcli-not-installed",
                "message": None,
            }

        return {
            "error": None,
            "message": "Success",
        }

    @classmethod
    def connect_check(
        cls, status_code: int, message: str, password_passed: bool
    ):
        # exit code 0 is a lie, nmcli can still return an error -.-
        if status_code == 0:
            if "Secrets were required, but not provided" in message:
                if password_passed:
                    return {
                        "error": "invalid-password",
                        "message": None,
                    }

                else:
                    return {
                        "error": "password-required",
                        "message": None,
                    }

            return {
                "error": None,
                "message": "Success",
            }

        if status_code == 1:
            if "property is invalid" in message:
                return {
                    "error": "invalid-password",
                    "message": None,
                }

            return {
                "error": "unknown-error",
                "message": None,
            }

        return {
            "error": "unknown-error",
            "message": None,
        }

    @classmethod
    def disconnect_check(cls, status_code: int, message: str):
        # exit code 0 is a lie, nmcli can still return an error -.-
        if status_code == 0:
            return {
                "error": None,
                "message": "Success",
            }

        if status_code == 1:
            return {
                "error": "unknown-error",
                "message": None,
            }

        return {
            "error": "unknown-error",
            "message": None,
        }

    @classmethod
    def wifilist_check(cls, status_code: int, message: str):
        # exit code 0 is a lie, nmcli can still return an error -.-
        if status_code == 0:
            return {
                "error": None,
                "message": "Success",
            }

        if status_code == 1:
            return {
                "error": "unknown-error",
                "message": None,
            }

        return {
            "error": "unknown-error",
            "message": None,
        }


class WifiService(object):
    # Return "SSID", "quality" and "encrypted" information for all available
    # networks
    @classmethod
    @retry_on_exception(max_retries=5, fail_response=[])
    def list_wifi_networks(cls):
        wifi_networks = []

        try:
            result = shell_command("nmcli -t -f ALL dev wifi")

            response = NmcliResponseHandler.generic_check(
                int(result["status"]), str(result["result"])
            )

            if response["error"]:
                return response

            response = NmcliResponseHandler.wifilist_check(
                int(result["status"]),
                str(result["result"]),
            )

            if response["error"]:
                return response

            lines = result["result"].replace("\:", "#")
            lines = lines.split("\n")

            for line in lines:
                if not line:
                    continue

                parts = line.split(":")

                name = parts[1]
                signal = parts[8]
                security = parts[10]

                if not name:
                    continue

                if security:
                    security = True
                else:
                    security = False

                wifi_networks.append(
                    {
                        "SSID": name,
                        "quality": int(signal),
                        "encrypted": security,
                    }
                )

        except Exception as e:
            logging.warning(f"Exception trying to list wifi interfaces: {e}\n")

        # Remove duplicates
        unique_ssids = {}

        for network in wifi_networks:
            ssid = network["SSID"]
            quality = network["quality"]

            if (
                ssid not in unique_ssids
                or quality > unique_ssids[ssid]["quality"]
            ):
                unique_ssids[ssid] = network

        wifi_networks = list(unique_ssids.values())

        return wifi_networks

    # Returns a dict:
    # {
    #     "error": Union[None, str],
    #     "message": Union[str, None],
    # }
    # "error" and "message" are mutually exclusive
    @classmethod
    def connect(cls, ssid: str, password: Union[str, None] = ""):
        try:
            command = f'nmcli dev wifi connect "{ssid}"'

            if password:
                command += f' password "{password}"'

            result = shell_command(command)

            response = NmcliResponseHandler.generic_check(
                int(result["status"]), str(result["result"])
            )

            if response["error"]:
                return response

            return NmcliResponseHandler.connect_check(
                int(result["status"]),
                str(result["result"]),
                password is not None,
            )

        except Exception as e:
            logging.warning(
                f"Exception while trying to connect to network {ssid}"
                f"with password {password}: {e}"
            )

        return {"error": "unknown-error", "message": None}

    @classmethod
    def disconnect(cls):
        try:
            ssid = cls.current_wifi()

            if not ssid:
                return {
                    "error": None,
                    "message": "Weren't connected to a network to begin with",
                }

            result = shell_command(f'nmcli connection delete "{ssid}"')

            response = NmcliResponseHandler.generic_check(
                int(result["status"]),
                str(result["result"]),
            )

            if response["error"]:
                return response

            return NmcliResponseHandler.disconnect_check(
                int(result["status"]),
                str(result["result"]),
            )

        except Exception as e:
            logging.warning(f"Exception while trying to disconnect: {e}")

        return {"error": "unknown-error", "message": None}

    @classmethod
    @retry_on_exception(max_retries=5, fail_response=[])
    def wifi_interfaces(cls):
        wifi_interfaces = []
        interfaces = netifaces.interfaces()

        # Go through all available interfaces and pick out ones that start
        # with wl, such as wlan1 or wlp0s20f4
        for interface in interfaces:
            if len(interface) > 1 and interface[:2] == "wl":
                wifi_interfaces.append(interface)

        return wifi_interfaces

    @classmethod
    @retry_on_exception(max_retries=5, fail_response=None)
    def current_wifi(cls):
        result = shell_command("iwgetid -r")

        if result["status"] == 0:
            return result["result"].strip()

        else:
            return None

    @classmethod
    @retry_on_exception(max_retries=5, fail_response=None)
    def wifi_info(cls, ssid):
        wifi_list = cls.list_wifi_networks()

        if "error" in wifi_list and wifi_list["error"]:
            return wifi_list

        for wifi_info in wifi_list:
            if ssid == wifi_info["SSID"]:
                return wifi_info

        return None
