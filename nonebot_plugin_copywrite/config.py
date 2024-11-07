from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel): ...


copywrite_config = get_plugin_config(Config)
