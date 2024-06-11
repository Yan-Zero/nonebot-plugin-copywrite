import random
from typing import Any
from datetime import datetime
from datetime import timedelta
from openai import AsyncOpenAI

from nonebot import get_plugin_config
from .config import Config


class OpenAI_Config:
    baseurl: str
    apikey: str
    model: str

    def __init__(self, *, model: str, apikey: str = None, baseurl: str = None) -> None:
        self.apikey = apikey
        self.baseurl = baseurl
        self.model = model


class OpenAI_Pool:
    __cilents: dict[str, list[AsyncOpenAI]]
    __request_limit: dict[
        str,
        list[tuple[datetime, AsyncOpenAI, timedelta]],
    ]

    def __init__(self, config: list[OpenAI_Config] = None) -> None:
        self.__cilents = {}
        for i in config:
            if i.model not in self.__cilents:
                self.__cilents[i.model] = []
            self.__cilents[i.model].append(
                AsyncOpenAI(base_url=i.baseurl, api_key=i.apikey)
            )
        self.__request_limit = {}

    def add_config(self, config: OpenAI_Config) -> None:
        self.__cilents.append(
            AsyncOpenAI(base_url=config.baseurl, api_key=config.apikey)
        )

    def __call__(self, model: str, *args: Any, **kwds: Any) -> AsyncOpenAI:
        cilent = self.__request_limit.get(model, [])
        if cilent:
            time, cilent, delta = cilent[0]
            if datetime.now() - time > delta:
                self.__request_limit[model].pop(0)
                self.__cilents[model].append(cilent)

        cilent = random.choice(self.__cilents.get(model, []))
        return cilent

    def RequestLimit(self, model: str, cilent: AsyncOpenAI, timeout: timedelta):
        index = -1

        for i, c in enumerate(self.__cilents[model]):
            if c.api_key != cilent.api_key:
                continue
            if c.base_url == cilent.base_url:
                index = i
                break
        if index >= 0:
            self.__cilents[model].pop(index)

        if model not in self.__request_limit:
            self.__request_limit[model] = []
        self.__request_limit[model].append(
            (datetime.now(), cilent, timedelta(minutes=timeout))
        )


config: Config = get_plugin_config(Config)

list_for_config: list[OpenAI_Config] = []
for i in range(len(config.openai_pool_model_config)):
    model = config.openai_pool_model_config[i]
    key = config.openai_pool_key_config[i]
    url = config.openai_pool_baseurl_config[i]
    if url == "ditto":
        url = list_for_config[-1].baseurl
    if model == "ditto":
        model = list_for_config[-1].model
    if key == "ditto":
        key = list_for_config[-1].apikey
    list_for_config.append(OpenAI_Config(baseurl=url, apikey=key, model=model))

POOL = OpenAI_Pool(config=list_for_config)


async def chat(message: list, model: str, times: int = 3):
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
    for _ in range(times - 1):
        cilent = POOL(model=model)
        try:
            rsp = await cilent.chat.completions.create(messages=message, model=model)
            if not rsp:
                raise ValueError("The Response is Null.")
            if not rsp.choices:
                raise ValueError("The Choice is Null.")
            return rsp
        except ValueError:
            pass
    return await POOL(model=model).chat.completions.create(
        messages=message, model=model
    )
