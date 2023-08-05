from typing import Optional

from pydantic.class_validators import root_validator
from pydantic.fields import Field

from .base import BaseModelORM


class TikTokUserModel(BaseModelORM):
    id: str = Field(..., alias="uid")
    avatar_link: str = Field(..., alias="avatar_larger")
    name: str = Field(..., alias="nickname")
    username: str = Field(..., alias="unique_id")
    description: Optional[str] = Field(None, alias="signature")
    description_url: Optional[str] = Field(None, alias="bio_url")
    following_count: Optional[int] = Field(None, alias="following_count")
    followers_count: Optional[int] = Field(None, alias="follower_count")
    likes_count: Optional[int] = Field(None, alias="total_favorited")
    verified: Optional[int] = Field(0, alias="verification_type")

    @root_validator(pre=True)
    def convert_data(cls, values):
        values["avatar_larger"] = values.get("avatar_larger", {}).get("url_list", [""])[-1]

        return values
