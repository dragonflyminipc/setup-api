from getmac import get_mac_address as gma
from typing import Dict, Union
import subprocess
import socket


def check_mac(mac_address: str) -> bool:
    return (
        mac_address.replace("-", ":") == gma().replace("-", ":")
        or gma().replace("-", ":") == "00:00:00:00:00:00"
    )


def get_local_ip() -> Union[str, None]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        return local_ip
    except Exception:
        return None


def shell_command(command: str) -> Dict[str, Union[int, str]]:
    result = b""
    status = 0

    try:
        result = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as cmd_error:
        status = cmd_error.returncode
        result = cmd_error.output

    return {"status": status, "result": result.decode("utf-8")}
