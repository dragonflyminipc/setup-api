from pydantic import BaseModel, Field
from typing import Union, List


class InternetInterfaceResponse(BaseModel):
    type: str = Field(example="wifi")
    quality: int = Field(example=90)
    current_network: Union[str, None] = Field(example="my wifi")


class InfoResponse(BaseModel):
    cpu_usage: Union[float, None] = Field(example=50.4)
    total_memory: Union[float, None] = Field(example=2048)
    free_memory: Union[float, None] = Field(example=400)
    memory_usage: Union[float, None] = Field(example=80.4)
    internet_connection: bool = Field(example=True)
    ip_address: Union[str, None] = Field(example="192.168.1.30")
    internet_interfaces: Union[List[InternetInterfaceResponse], None]
