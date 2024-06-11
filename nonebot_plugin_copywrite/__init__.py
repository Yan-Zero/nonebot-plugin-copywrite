import yaml
import pathlib
from .copywrite import generate_copywrite
from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me

from .chat import chat

m_copywrite = on_command(
    "copywrite",
    aliases={"文案"},
    priority=5,
    force_whitespace=True,
    block=True,
)

_copy: dict[str, dict] = {}
for file in pathlib.Path("./data/copywrite").glob("**/*.yaml"):
    with open(file, "r", encoding="utf-8") as f:
        _data = yaml.safe_load(f)
        if isinstance(_data, dict):
            _copy.update(_data)
for file in pathlib.Path(__file__).parent.glob("copywrite/*.yaml"):
    with open(file, "r", encoding="utf-8") as f:
        _data = yaml.safe_load(f)
        if isinstance(_data, dict):
            _copy.update(_data)


@m_copywrite.handle()
async def _(event: MessageEvent, args=CommandArg()):
    args = args.extract_plain_text().strip()
    if not args:
        ret = "请输入要仿写的文案名字"
        if True:
            ret = "目前的可用文案有：\n" + ", ".join(_copy.keys())
        await m_copywrite.finish(ret)

    args = args.split(maxsplit=1)
    args[0] = args[0].lower()
    if args[0] not in _copy:
        await m_copywrite.finish("没有找到该文案")

    copy = _copy[args[0]]
    if len(args) == 1:
        await m_copywrite.finish(copy.get("help", "主题呢？"))

    args = args[1].split(maxsplit=copy.get("keywords", 0))
    if len(args) < copy.get("keywords", 0):
        await m_copywrite.finish(
            copy.get("help", f'需要有{copy.get("keywords", 0)}个关键词')
        )

    try:
        rsp = await chat(
            message=[
                {
                    "role": "user",
                    "content": generate_copywrite(
                        copy=copy,
                        topic=args[-1],
                        keywords=args[:-1],
                    ),
                }
            ],
            model=copy.get("model", "gpt-3.5-turbo"),
        )
        if not rsp:
            raise ValueError("The Response is Null.")
        if not rsp.choices:
            raise ValueError("The Choice is Null.")
        rsp = rsp.choices[0].message.content
    except Exception as ex:
        await m_copywrite.finish(f"发生错误: {ex}")
    else:
        await m_copywrite.finish(rsp)
