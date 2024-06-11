from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""

    openai_pool_model_config: list[str] = []
    openai_pool_key_config: list[str] = []
    openai_pool_baseurl_config: list[str] = []
