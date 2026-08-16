from sqlalchemy.orm import Session 
from pgsql_models import SmallVideo

def store_small_video(
    db: Session,
    video_id: str,
    content: str
) -> SmallVideo:
    video = SmallVideo(
        video_id=video_id,
        content=content
    )

    db.add(video)
    db.flush()

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return video

