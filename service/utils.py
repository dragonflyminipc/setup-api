from getmac import get_mac_address as gma

def check_mac(mac_address):
    return mac_address.replace("-", ":") == gma().replace("-", ":") or\
        gma().replace("-", ":") == "00:00:00:00:00:00"
