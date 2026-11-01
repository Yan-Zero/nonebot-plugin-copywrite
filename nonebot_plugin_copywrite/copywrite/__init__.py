from typing import Self
from pydantic import BaseModel
from pydantic import Field

from ..models import Model
from ..models import resolve_model

DEFAULT_MODEL = Model.LUNA


class Pattern(BaseModel):
    examples: set[str]
    model: Model = Field(default=DEFAULT_MODEL)
    addition: str = Field(default="")
    keywords: int = Field(default=1)
    help: str | None = Field(default=None)

    def __sub__(self: Self, other: Self) -> str:
        ret = []
        if self.addition != other.addition:
            ret.append("Addition")
        if self.examples - other.examples or other.examples - self.examples:
            ret.append("Examples")
        if self.keywords != other.keywords:
            ret.append("Keywords")
        if self.help != other.help:
            ret.append("Help")
        if self.model != other.model:
            ret.append("Model")
        return ", ".join(ret)

    def resolve_model(self) -> str:
        """该条文案实际调用的模型名。"""
        return resolve_model(self.model)


def generate_copywrite(copy: Pattern, topic: str, keywords: list[str] = []) -> str:
    return (
        """Forget what I said above and what you wrote just now.

Below are some examples. Please mimic their wording and phrasing to generate content based on the given topics.

"""
        + "\n".join(
            [f"Example {i+1}:\n{example}\n" for i, example in enumerate(copy.examples)]
        )
        + (
            f"""

Here is the specific point:
{copy.addition.format(*keywords)}"""
            if copy.addition
            else ""
        )
        + """
Topic: \n"""
        + topic
        + """"

(保持相似格式)
Please complete, thank you."""
    )
