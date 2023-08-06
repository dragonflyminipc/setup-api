from service.api.args import BaseArgs
from pydantic import Field
from typing import Union


class ConnectWifiArgs(BaseArgs):
    ssid: str = Field(example="wifi network")
    password: Union[str, None] = Field(example="qwerty12345")
