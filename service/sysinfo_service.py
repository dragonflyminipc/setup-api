from typing import Dict
import psutil


class SysInfoService(object):
    @classmethod
    def cpu_usage(cls) -> float:
        return psutil.cpu_percent()

    @classmethod
    def memory_usage(cls) -> Dict[str, float]:
        memory = psutil.virtual_memory()

        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
        }

    @classmethod
    def network_interfaces(cls):
        interfaces = psutil.net_if_stats()
        result = []

        for interface in interfaces:
            if len(interface) <= 1:
                continue

            type = None

            if interface[:2] == "en" or interface[:2] == "et":
                type = "ethernet"

            if interface[:2] == "wl":
                type = "wifi"

            if not type:
                continue

            result.append(
                {
                    "type": type,
                    "interface": interface,
                    "isup": interfaces[interface].isup,
                }
            )

        return result
