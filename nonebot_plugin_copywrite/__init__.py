import asyncio
import itertools
from typing import Awaitable, Callable

import yaml
from nonebot import on_command
from nonebot.adapters import Bot, Message, MessageSegment, MessageTemplate
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from .chat import chat
from .copywrite import DEFAULT_MODEL, Pattern, generate_copywrite
from .models import Model
from .remote import USER_DIR, builtin_dir, download
from .version import PLUGIN_VERSION, satisfies

m_copywrite = on_command(
    "copywrite",
    aliases={"文案"},
    priority=5,
    force_whitespace=True,
    block=True,
)


RESERVED_WORD: dict[
    str,
    Callable[..., Awaitable[str | Message | MessageSegment | MessageTemplate | None]],
] = {}
_COPY: dict[str, Pattern] = {}
_COPY_TYPE: dict[str, set] = {}


def _parse_model(value: object, fallback: Model, where: object) -> Model:
    if value is None:
        return fallback
    try:
        return Model(value)
    except ValueError:
        logger.opt(colors=True).warning(f"{where} 的 model 无效，使用 {fallback}。")
        return fallback


def load(clear: bool = False, **kwargs) -> list[str]:
    """加载全部文案，返回因 `__min_version__` 被跳过的文件说明。"""
    global _COPY, _COPY_TYPE
    if clear:
        _COPY = {}
        _COPY_TYPE = {}

    skipped = []
    for file in itertools.chain(
        builtin_dir().glob("*.yaml"),
        USER_DIR.glob("**/*.yaml"),
    ):
        with open(file, "r", encoding="utf-8") as f:
            _data = yaml.safe_load(f)
            if not isinstance(_data, dict):
                continue

            min_version = _data.pop("__min_version__", None)
            if min_version is not None and not satisfies(min_version):
                logger.opt(colors=True).warning(
                    f"{file} 需要插件 >= {min_version}，当前 {PLUGIN_VERSION}，已跳过。"
                )
                skipped.append(f"{file.name}（需要 >= {min_version}）")
                continue

            if "__category__" in _data:
                category = _data["__category__"]
                del _data["__category__"]
            else:
                category = "Default"

            if category not in _COPY_TYPE:
                _COPY_TYPE[category] = set()

            default_model = _parse_model(
                _data.pop("__model__", None), DEFAULT_MODEL, file
            )

            for key, v in _data.items():
                key = key.strip().lower()
                if key in RESERVED_WORD:
                    logger.opt(colors=True).warning(f"{key} is reserved word.")
                    continue
                if not isinstance(v, dict):
                    logger.opt(colors=True).warning(f"{key} 的配置无效。")
                    continue
                v["model"] = _parse_model(v.get("model"), default_model, key)
                try:
                    pattern = Pattern.model_validate(v)
                except Exception as ex:
                    logger.opt(colors=True).warning(f"{key} 的配置无效: {ex}")
                    continue
                _COPY_TYPE[category].add(key)
                _COPY[key] = pattern

    return skipped


def _join(keys) -> str:
    return ", ".join(sorted(map(str, keys), key=lambda x: (-len(x), x)))


def _diff(old_type: dict[str, set], old_copy: dict[str, Pattern]) -> str:
    """对比重新加载前后的文案。"""
    ret = []
    if category := _COPY_TYPE.keys() - old_type.keys():
        ret.append(f"新增分类：\n  {_join(category)}")
    if category := old_type.keys() - _COPY_TYPE.keys():
        ret.append(f"移除分类：\n  {_join(category)}")
    for category, keys in _COPY_TYPE.items():
        old = old_type.get(category, set())
        if added := keys - old:
            ret.append(f"分类 {category} 新增：\n  {_join(added)}")
        if removed := old - keys:
            ret.append(f"分类 {category} 移除：\n  {_join(removed)}")
    for key, p in _COPY.items():
        if key in old_copy and (changed := p - old_copy[key]):
            ret.append(f"{key} 变化：{changed}")
    return "\n".join(ret)


async def reload(**kwargs) -> str:
    old_type, old_copy = _COPY_TYPE, _COPY
    skipped = await asyncio.to_thread(load, clear=True)
    ret = ["重新加载完成。"]
    if diff := _diff(old_type, old_copy):
        ret.append(diff)
    if skipped:
        ret.append("以下文件需要更新插件：\n  " + "\n  ".join(skipped))
    return "\n".join(ret)


async def fetch(**kwargs) -> str:
    try:
        count = await download()
    except Exception as ex:
        logger.warning(f"Fetch 失败: {ex}")
        return f"Fetch 失败: {ex}"
    return f"已下载 {count} 个文案文件。\n" + await reload()


RESERVED_WORD["reload"] = reload
RESERVED_WORD["fetch"] = fetch
load()


@m_copywrite.handle()
async def _(bot: Bot, event: MessageEvent, args=CommandArg()):
    args = args.extract_plain_text().strip()
    if not args:
        if True:
            ret = ""
            for category, keys in _COPY_TYPE.items():
                ret += (
                    f"{category}:\n  "
                    + ", ".join(sorted(keys, key=lambda x: (-len(x), x)))
                    + "\n"
                )
        if not ret:
            ret = "好像一片空白？"
        await m_copywrite.finish(ret)

    args = args.split(maxsplit=1)
    args[0] = args[0].lower()
    if args[0] in RESERVED_WORD:
        if not await SUPERUSER(bot=bot, event=event):
            await m_copywrite.finish("没有权限哦。")
        await m_copywrite.finish(
            await RESERVED_WORD[args[0]](
                bot=bot,
                args=args[1:],
                event=event,
            )
        )

    if args[0] not in _COPY:
        await m_copywrite.finish("没有找到该文案")
    copy = _COPY[args[0]]
    if len(args) == 1:
        await m_copywrite.finish(copy.help or "主题呢？")

    args = args[1].split(maxsplit=copy.keywords - 1)
    if len(args) < copy.keywords:
        await m_copywrite.finish(
            f"需要有{copy.keywords - len(args)}个关键词。" + ("\n\n" + copy.help)
            if copy.help
            else ""
        )

    try:
        rsp = await chat(
            messages=[
                {
                    "role": "user",
                    "content": generate_copywrite(
                        copy=copy,
                        topic=args[-1],
                        keywords=args[:-1],
                    ),
                }
            ],
            model=copy.resolve_model(),
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
