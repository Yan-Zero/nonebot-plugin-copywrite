"""定型文可选的模型档位。

四档（小 / 中 / 大 / 超大杯），每档有两个代号，任一代号都指向同一档：

======  ==============  =========================
档位    代号            配置项
======  ==============  =========================
小杯    luna / haiku    copywrite_model_luna
中杯    terra / sonnet  copywrite_model_terra
大杯    sol / opus      copywrite_model_sol
超大杯  astra / fable   copywrite_model_astra
======  ==============  =========================

YAML 里写的只是代号，真正调用的模型由配置决定。
"""

from enum import StrEnum


class Model(StrEnum):
    LUNA = "luna"
    HAIKU = "haiku"
    TERRA = "terra"
    SONNET = "sonnet"
    SOL = "sol"
    OPUS = "opus"
    ASTRA = "astra"
    FABLE = "fable"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            value = value.strip().lower()
            for member in cls:
                if member.value == value:
                    return member
        return None

    @property
    def tier(self) -> str:
        """所属档位，即配置项 copywrite_model_<tier> 的后缀。"""
        return TIER[self]


TIER: dict[Model, str] = {
    Model.LUNA: "luna",
    Model.HAIKU: "luna",
    Model.TERRA: "terra",
    Model.SONNET: "terra",
    Model.SOL: "sol",
    Model.OPUS: "sol",
    Model.ASTRA: "astra",
    Model.FABLE: "astra",
}


def resolve_model(model: Model) -> str:
    """把代号换成配置里填写的模型名。"""
    from .config import copywrite_config

    return getattr(copywrite_config, f"copywrite_model_{model.tier}")
