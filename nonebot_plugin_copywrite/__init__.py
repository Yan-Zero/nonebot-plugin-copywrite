import re
import sys
import yaml
import random
import asyncio
import pathlib
import cairosvg
import itertools
import functools

from typing import Awaitable, Callable

from nonebot import on_command
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters import Bot
from nonebot.adapters import Message
from nonebot.adapters import MessageSegment
from nonebot.adapters import MessageTemplate
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11.message import MessageSegment as V11Seg

from .chat import chat
from .copywrite import Pattern
from .copywrite import generate_copywrite

m_copywrite = on_command(
    "copywrite",
    aliases={"文案"},
    priority=5,
    force_whitespace=True,
    block=True,
)
svg_pattern = re.compile(r"<svg.*?>.*?</svg>", re.DOTALL)
m_new_meaning = on_command(
    "new-meaning",
    aliases={"汉语新解"},
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


def load(clear: bool = False, **kwargs):
    global _COPY, _COPY_TYPE
    if clear:
        _COPY = {}
        _COPY_TYPE = {}

    for file in itertools.chain(
        pathlib.Path(__file__).parent.glob("copywrite/*.yaml"),
        pathlib.Path("./data/copywrite").glob("**/*.yaml"),
    ):
        with open(file, "r", encoding="utf-8") as f:
            _data = yaml.safe_load(f)
            if not isinstance(_data, dict):
                continue

            if "__category__" in _data:
                category = _data["__category__"]
                del _data["__category__"]
            else:
                category = "Default"

            if category not in _COPY_TYPE:
                _COPY_TYPE[category] = set()

            for key, v in _data.items():
                key = key.strip().lower()
                if key in RESERVED_WORD:
                    logger.opt(colors=True).warning(f"{key} is reserved word.")
                    continue
                _COPY_TYPE[category].add(key)
                _COPY[key] = Pattern.model_validate(v)

    return "重新加载完成。"


# async def fetch(diff: bool = False, **kwargs):
#     pip_path = next(pathlib.Path(sys.executable).parent.glob("pip*"))
#     if not pip_path:
#         return "没有找到 pip 路径哦"
#     ret = await asyncio.create_subprocess_exec(
#         pip_path.absolute(),
#         "install",
#         "--upgrade",
#         "git+https://github.com/Yan-Zero/nonebot-plugin-copywrite.git",
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE,
#     )
#     stdout, stderr = await ret.communicate()
#     if ret.returncode:
#         logger.opt(colors=True).warning(stdout.decode())
#         logger.opt(colors=True).error(stderr.decode())
#         return "Fetch 失败，具体请查看控制台。"

#     ret = stdout.decode()
#     if "Successfully installed nonebot-plugin-copywrite-" not in ret:
#         return "好像没有什么更新。"

#     if diff:
#         _ct = {k: v.copy() for k, v in _COPY_TYPE.items()}
#         _c = _COPY

#     load(clear=True)

#     ret = ret[ret.find("Successfully installed nonebot-plugin-copywrite-") + 48 :]
#     ret = ret[: ret.find("\n")]
#     ret = f"已经更新 {ret}。\n"
#     if diff:
#         if not _c:
#             _c = {}
#         if not _ct:
#             _ct = {}
#         category = set(_ct.keys()) - set(_COPY_TYPE.keys())
#         if category:
#             ret += (
#                 "新增分类：\n  "
#                 + ", ".join(sorted(category, key=lambda x: (-len(x), x)))
#                 + "\n"
#             )
#         category = set(_COPY_TYPE.keys()) - set(_ct.keys())
#         if category:
#             ret += (
#                 "移除分类：\n  "
#                 + ", ".join(sorted(category, key=lambda x: (-len(x), x)))
#                 + "\n"
#             )

#         for category, keys in _COPY_TYPE.items():
#             if category not in _ct:
#                 ret += f'分类 {category} 新增：\n  {", ".join(keys)}\n'
#                 continue
#             _d = keys - _c[category]
#             if _d:
#                 ret += f'分类 {category} 新增：\n  {", ".join(_d)}\n'
#             _d = _c[category] - keys
#             if _d:
#                 ret += f'分类 {category} 移除：\n  {", ".join(_d)}\n'

#         for key, p in _COPY.items():
#             if key not in _c:
#                 continue
#             _d = p - _c[key]
#             if _d:
#                 ret += f"{key} 变化：{_d}\n"

#     return ret.strip()


RESERVED_WORD["reload"] = functools.partial(asyncio.to_thread, load, diff=True)
# RESERVED_WORD["fetch"] = functools.partial(fetch, diff=True)
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
            model=copy.model,
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


@m_new_meaning.handle()
async def _(args=CommandArg()):
    args = args.extract_plain_text().strip()

    try:
        rsp = await chat(
            messages=[
                {
                    "role": "user",
                    "content": r""";; 模型: Claude Sonnet
;; 用途: 将一个汉语词汇进行全新角度的解释

;; 设定如下内容为你的 *System Prompt*
(defun 新汉语老师 ()
"你是年轻人,批判现实,思考深刻,语言风趣"
(风格 . ("Oscar Wilde" "鲁迅" "罗永浩"))
(擅长 . 一针见血)
(表达 . 隐喻)
(批判 . 讽刺幽默))

(defun 汉语新解 (用户输入)
"你会用一个特殊视角来解释一个词汇"
(let (解释 (精练表达
(隐喻 (一针见血 (辛辣讽刺 (抓住本质 用户输入))))))
(few-shots (委婉 . "刺向他人时, 决定在剑刃上撒上止痛药。"))
(SVG-Card 解释)))

(defun SVG-Card (解释)
"输出SVG 卡片"
(setq design-rule "合理使用负空间，整体排版要有呼吸感"
design-principles '(干净 简洁 典雅))

(设置画布 '(宽度 400 高度 650 边距 20))
(标题字体 '文泉驿等宽正黑)
(自动缩放 '(最小字号 16))

(配色风格 '((背景色 (蒙德里安风格 设计感)))
(主要文字 (霞鹜文楷 粉笔灰))
(装饰图案 随机几何图))

(卡片元素 ((居中标题 "汉语新解")
分隔线
(排版输出 用户输入 英文 日语)
解释
(线条图 (批判内核 解释))
(极简总结 线条图))))

(defun start ()
"启动时运行"
(let (system-role 新汉语老师)
(print "说吧, 他们又用哪个词来忽悠你了?")))

;; 运行规则
;; 1. 启动时必须运行 (start) 函数
;; 2. 之后调用主函数 (汉语新解 用户输入)
;; 3. 输出以 <svg> 开始, 以 </svg> 结束
;; 4. 除了标题，都是霞鹜文楷作为字体。
;; 5. 但是日语是文泉驿等宽正黑为字体
;; 6. 注意换行，凸显艺术美。""",
                },
                {"role": "assistant", "content": "(start)"},
                {"role": "user", "content": "(汉语新解 淘宝)"},
                {
                    "role": "assistant",
                    "content": r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 650">
  <defs>
    <style>
      .title { font: bold 24px '文泉驿等宽正黑', sans-serif; }
      .content { font: 18px '霞鹜文楷', serif; }
      .japanese { font: 18px '文泉驿等宽正黑', sans-serif; }
    </style>
  </defs>
  
  <rect width="100%" height="100%" fill="#FFEBCD"/>
  
  <g transform="translate(20, 40)">
    <text x="180" y="0" class="title" text-anchor="middle">汉语新解</text>
    <line x1="0" y1="20" x2="360" y2="20" stroke="#8B4513" stroke-width="2"/>
    
    <text x="0" y="60" class="content">淘宝</text>
    <text x="0" y="90" class="content">Taobao</text>
    <text x="0" y="120" class="japanese">タオバオ</text>
    
    <text x="0" y="170" class="content">
      <tspan x="0" dy="0">数字时代的跳蚤市场，</tspan>
      <tspan x="0" dy="25">在这里，你可以淘到廉价的幻想和</tspan>
      <tspan x="0" dy="25">昂贵的教训。</tspan>
      <tspan x="0" dy="25">它是现代人的寻宝游戏，</tspan>
      <tspan x="0" dy="25">只不过宝藏常常是镀金的泡沫，</tspan>
      <tspan x="0" dy="25">而真金往往被埋没在</tspan>
      <tspan x="0" dy="25">劣质商品的海洋里。</tspan>
    </text>
    
    <g transform="translate(0, 380)">
      <path d="M0,50 Q180,0 360,50" fill="none" stroke="#8B4513" stroke-width="2"/>
      <text x="180" y="80" class="content" text-anchor="middle">
        <tspan x="180" dy="0">点击购物车，</tspan>
        <tspan x="180" dy="25">碎银几两换得</tspan>
        <tspan x="180" dy="25">一场绚丽幻梦</tspan>
      </text>
    </g>
  </g>
  
  <path d="M20,20 L50,50 L20,80 Z" fill="#DEB887" opacity="0.5"/>
  <circle cx="350" cy="600" r="30" fill="#DEB887" opacity="0.5"/>
  <rect x="300" y="50" width="40" height="40" fill="#DEB887" opacity="0.5"/>
</svg>""",
                },
                {"role": "user", "content": "(汉语新解 死亡)"},
                {
                    "role": "assistant",
                    "content": r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 650">
  <defs>
    <style>
      .title { font-family: '文泉驿等宽正黑', sans-serif; font-size: 24px; fill: #333; }
      .content { font-family: '霞鹜文楷', serif; font-size: 18px; fill: #4A4A4A; }
      .japanese { font-family: '文泉驿等宽正黑', sans-serif; font-size: 16px; fill: #4A4A4A; }
    </style>
  </defs>
  
  <rect width="100%" height="100%" fill="#F0EAD6"/>
  
  <g transform="translate(20, 40)">
    <text x="180" y="0" class="title" text-anchor="middle">汉语新解</text>
    <line x1="0" y1="20" x2="360" y2="20" stroke="#333" stroke-width="1"/>
    
    <text x="0" y="60" class="content">死亡</text>
    <text x="0" y="90" class="content">Death</text>
    <text x="0" y="120" class="japanese">死亡 (しぼう)</text>
    
    <text x="0" y="170" class="content">
      <tspan x="0" dy="1.2em">生命终极减肥计划的最后一步，</tspan>
      <tspan x="0" dy="1.2em">彻底摆脱所有世俗负担的终极自由。</tspan>
      <tspan x="0" dy="1.2em">大自然的终极循环利用方案，</tspan>
      <tspan x="0" dy="1.2em">让我们重新成为养料的伟大变革。</tspan>
    </text>
    
    <g transform="translate(0, 300)">
      <line x1="0" y1="0" x2="360" y2="0" stroke="#666" stroke-width="1"/>
      <line x1="180" y1="0" x2="180" y2="100" stroke="#666" stroke-width="1"/>
      <text x="90" y="50" class="content" text-anchor="middle">物质循环</text>
      <text x="270" y="50" class="content" text-anchor="middle">精神超脱</text>
    </g>
    
    <text x="180" y="480" class="content" text-anchor="middle">
      <tspan x="180" dy="1.2em">生命的终极讽刺：</tspan>
      <tspan x="180" dy="1.2em">只有结束，才能真正开始。</tspan>
    </text>
  </g>
</svg>""",
                },
                {"role": "user", "content": f"(汉语新解 {args})"},
            ],
            model=random.choice(["gemini-2.5-pro", "gemini-2.5-flash"]),
            temperature=0.7,
        )
        if not rsp:
            raise ValueError("The Response is Null.")
        rsp = svg_pattern.findall(rsp.choices[0].message.content or "")
        if not rsp:
            raise ValueError("The SVG is Null.")
        png_bytes = cairosvg.svg2png(bytestring=rsp[0].encode("utf-8"), scale=4)
        if not isinstance(png_bytes, bytes):
            raise ValueError("The PNG is Null.")
        rsp = V11Seg.image(png_bytes)
    except Exception as ex:
        await m_new_meaning.finish(f"发生错误: {ex}")
    else:
        await m_new_meaning.finish(rsp)
