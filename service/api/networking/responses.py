from pydantic import BaseModel, Field
from typing import List

class WifiResponse(BaseModel):
    ssid: str = Field(example="wifi name")
    quality: int = Field(example=100)
    encrypted: bool = Field(example=True)

class ListWifiResponse(BaseModel):
    wifi_list: List[WifiResponse]

class WifiConnectResponse(BaseModel):
    ssid: str = Field(example="wifi name")
