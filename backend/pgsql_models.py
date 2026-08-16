from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class SmallVideo(Base):

    __tablename__ = "small_videos"

    video_id: Mapped[str] = mapped_column(
        String(11),
        primary_key=True
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )


