"""从 GitHub 拉取最新的内置文案，只更新 yaml，不动 Python 环境。

下载的文案缓存在 `./data/copywrite_builtin/`，并记录下载时的插件版本。
插件升级后版本对不上，缓存作废，回退到包内自带的文案，避免旧缓存盖住新包。
"""

import io
import shutil
import tarfile
import pathlib

import httpx

from .config import copywrite_config
from .version import PLUGIN_VERSION

PACKAGE_DIR = pathlib.Path(__file__).parent / "copywrite"
CACHE_DIR = pathlib.Path("./data/copywrite_builtin")
USER_DIR = pathlib.Path("./data/copywrite")
STAMP = ".plugin_version"
MEMBER_PREFIX = "nonebot_plugin_copywrite/copywrite/"


def builtin_dir() -> pathlib.Path:
    """内置文案所在目录：缓存有效时用缓存，否则用包内自带的。"""
    try:
        if (CACHE_DIR / STAMP).read_text(encoding="utf-8").strip() == PLUGIN_VERSION:
            return CACHE_DIR
    except OSError:
        pass
    return PACKAGE_DIR


async def download() -> int:
    """下载并替换缓存，返回文案文件数。失败时抛异常，旧缓存保持不变。"""
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        rsp = await client.get(copywrite_config.copywrite_fetch_url)
        rsp.raise_for_status()

    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(rsp.content), mode="r:gz") as tar:
        for member in tar.getmembers():
            # 归档内路径形如 <repo>-<branch>/nonebot_plugin_copywrite/copywrite/x.yaml
            _, _, path = member.name.partition("/")
            if not member.isfile() or not path.startswith(MEMBER_PREFIX):
                continue
            name = path.removeprefix(MEMBER_PREFIX)
            if "/" in name or not name.endswith(".yaml"):
                continue
            if f := tar.extractfile(member):
                files[name] = f.read()
    if not files:
        raise ValueError("归档里没有找到文案。")

    tmp = CACHE_DIR.with_name(CACHE_DIR.name + ".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    for name, data in files.items():
        (tmp / name).write_bytes(data)
    (tmp / STAMP).write_text(PLUGIN_VERSION, encoding="utf-8")

    shutil.rmtree(CACHE_DIR, ignore_errors=True)
    tmp.rename(CACHE_DIR)
    return len(files)
