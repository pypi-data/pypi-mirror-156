from datetime import datetime
from typing import Optional

from pydantic.class_validators import root_validator
from pydantic.fields import Field

from .base import BaseModelORM


class TikTokVideoModel(BaseModelORM):
    id: str = Field(..., alias="aweme_id")
    created_time: datetime = Field(..., alias="create_time")  # -Дата и время поста
    description: str = Field(..., alias="desc")  # -Описание поста (включая эмодзи) (описание поста)
    play_count: int = Field(..., alias="play_count")  # -Кол-во просмотров клипа/поста
    share_count: int = Field(..., alias="share_count")  # - Количество репостов клипа
    likes_count: int = Field(..., alias="digg_count")  # -Количество лайков поста
    comment_count: Optional[int] = Field(None, alias="comment_count")  # -Количество комментариев поста
    user_id: str = Field(..., alias="user_id")
    share_url: Optional[str] = Field(None, alias="share_url")

    @root_validator(pre=True)
    def convert_data(cls, values):
        values.update(values.get("statistics", {}))
        values["user_id"] = values["author"]["uid"]

        return values
