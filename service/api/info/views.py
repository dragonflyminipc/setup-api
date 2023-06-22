from service.sysinfo_service import SysInfoService
from service.wifi_service import WifiService
from .responses import InfoResponse
from service import utils, display
from service.errors import Abort
from ..views import router
from fastapi import Query

@router.get(
    "/info",
    tags=["Info"],
    summary="System stats and information",
    response_model=InfoResponse
)
async def info():
    cpu_usage = SysInfoService.cpu_usage()
    memory_usage = SysInfoService.memory_usage()
    network_interfaces = SysInfoService.network_interfaces()

    current_wifi = WifiService.current_wifi()

    current_wifi_info = None

    if current_wifi:
        current_wifi_info = WifiService.wifi_info(current_wifi)

    return display.info(
        cpu_usage,
        memory_usage,
        network_interfaces,
        current_wifi,
        current_wifi_info
    )
