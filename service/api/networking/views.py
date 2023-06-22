from .responses import ListWifiResponse, WifiConnectResponse
from service.wifi_service import WifiService
from service import utils, display
from .args import ConnectWifiArgs
from service.errors import Abort
from ..views import router
from fastapi import Query

@router.get(
    "/wifi/list",
    tags=["Wifi"],
    summary="List available wifi networks",
    response_model=ListWifiResponse
)
async def wifi_list():
    result_list = WifiService.list_wifi_networks()

    return display.wifi_list(result_list)

@router.post(
    "/wifi/connect",
    tags=["Wifi"],
    summary="Connect to a wifi network",
    response_model=WifiConnectResponse
)
async def wifi_connect(
    body: ConnectWifiArgs,
):
    result = WifiService.connect(body.ssid, body.password)

    if result["error"]:
        raise Abort("wifi", "couldnt-connect")

    return {
        "ssid": body.ssid
    }
