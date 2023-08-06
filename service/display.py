# Helper functions to format the response dict


def wifi_list(result_list):
    result = {"wifi_list": []}

    for wifi in result_list:
        result["wifi_list"].append(
            {
                "ssid": wifi["SSID"],
                "quality": wifi["quality"],
                "encrypted": wifi["encrypted"],
            }
        )

    result["wifi_list"] = sorted(
        result["wifi_list"], key=lambda x: (-x["quality"], x["ssid"])
    )

    return result


def info(cpu, memory, network, current_wifi, current_wifi_info, ip_address):
    internet_connection = False
    internet_interfaces = []

    for interface in network:
        if not interface["isup"]:
            continue

        internet_connection = True

        if interface["type"] == "wifi":
            internet_interfaces.append(
                {
                    "type": "wifi",
                    "quality": current_wifi_info["quality"],
                    "current_network": current_wifi,
                }
            )

        if interface["type"] == "ethernet":
            internet_interfaces.append(
                {"type": "ethernet", "quality": 100, "current_network": None}
            )

    return {
        "cpu_usage": cpu,
        "total_memory": round(memory["total"] / (1024 * 1024), 1),
        "free_memory": round(memory["available"] / (1024 * 1024), 1),
        "memory_usage": memory["percent"],
        "internet_connection": internet_connection,
        "internet_interfaces": internet_interfaces,
        "ip_address": ip_address,
    }
