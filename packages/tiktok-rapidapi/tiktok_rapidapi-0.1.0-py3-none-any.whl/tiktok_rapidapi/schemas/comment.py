from pydantic.class_validators import root_validator
from pydantic.fields import Field

from .base import BaseModelORM
from . import TikTokUserModel


class TikTokCommentModel(BaseModelORM):
    id: str = Field(..., alias="cid")

    text: str = Field(..., alias="text")
    likes_count: int = Field(..., alias="digg_count")

    user_id: str = Field(..., alias="user_id")
    video_id: str = Field(..., alias="aweme_id")

    user: TikTokUserModel = Field(..., alias="user")

    @root_validator(pre=True)
    def convert_data(cls, values):
        values["user_id"] = values["user"]["uid"]

        return values
