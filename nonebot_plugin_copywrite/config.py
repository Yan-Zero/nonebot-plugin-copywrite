from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """四档模型（小 / 中 / 大 / 超大杯）各自使用的模型名。"""

    copywrite_model_luna: str = "gpt-6-luna"
    copywrite_model_terra: str = "gpt-6-luna"
    copywrite_model_sol: str = "gpt-6-luna"
    copywrite_model_astra: str = "gpt-6-luna"


copywrite_config = get_plugin_config(Config)
