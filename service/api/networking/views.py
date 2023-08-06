from .responses import (
    ListWifiResponse,
    WifiConnectResponse,
    WifiDisconnectResponse,
)
from service.wifi_service import WifiService
from .args import ConnectWifiArgs
from service.errors import Abort
from service import display
from ..views import router
from service import utils


@router.get(
    "/wifi/list",
    tags=["Wifi"],
    summary="List available wifi networks",
    response_model=ListWifiResponse,
)
async def wifi_list():
    result = WifiService.list_wifi_networks()

    if "error" in result and result["error"]:
        raise Abort("wifi", result["error"])

    return display.wifi_list(result)


@router.post(
    "/wifi/connect",
    tags=["Wifi"],
    summary="Connect to a wifi network",
    response_model=WifiConnectResponse,
)
async def wifi_connect(
    body: ConnectWifiArgs,
):
    result = WifiService.connect(body.ssid, body.password)

    if "error" in result and result["error"]:
        raise Abort("wifi", result["error"])

    ip_address = utils.get_local_ip()

    return {"ssid": body.ssid, "ip_address": ip_address}


@router.post(
    "/wifi/disconnect",
    tags=["Wifi"],
    summary="Disconnect from a wifi network",
    response_model=WifiDisconnectResponse,
)
async def wifi_disconnect():
    result = WifiService.disconnect()

    if "error" in result and result["error"]:
        raise Abort("wifi", result["error"])

    return {"message": "Disconnected"}
