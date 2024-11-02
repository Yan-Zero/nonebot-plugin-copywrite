import yaml
from openai import AsyncOpenAI
from nonebot import get_plugin_config

from .config import Config

config: Config = get_plugin_config(Config)
OPENAI_CONFIG = {}
try:
    with open("configs/chatgpt-vision/keys.yaml") as f:
        for i in yaml.safe_load(f):
            OPENAI_CONFIG[i.get("model")] = {
                "api_key": i.get("key"),
                "base_url": i.get("url"),
            }
except Exception:
    pass


async def chat(message: list, model: str, times: int = 3, temperature: int = 0.65):
    """
    Chat with ChatGPT

    Parameters
    ----------
    message : list
        The message you want to send to ChatGPT
    model : str
        The model you want to use
    times : int
        The times you want to try
    """
    if model not in OPENAI_CONFIG:
        raise ValueError(f"The model {model} is not supported.")
    try:
        rsp = await AsyncOpenAI(**OPENAI_CONFIG[model]).chat.completions.create(
            messages=message, model=model, temperature=temperature
        )
        if not rsp:
            raise ValueError("The Response is Null.")
        if not rsp.choices:
            raise ValueError("The Choice is Null.")
        return rsp
    except ValueError:
        pass


async def draw_image(model: str, prompt: str, size: str = "1024x1024", times: int = 3):
    if model not in OPENAI_CONFIG:
        raise ValueError(f"The model {model} is not supported.")
    return await AsyncOpenAI(**OPENAI_CONFIG[model]).images.generate(
        model=model, prompt=prompt, size=size
    )
