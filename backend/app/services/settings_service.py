from sqlalchemy.orm import Session
from app.models.settings import Settings
from app.utils.helpers import to_dict


class SettingsService:

    @staticmethod
    def get_settings(db: Session):
        return db.query(Settings).filter(Settings.id == 1).first()

    @staticmethod
    def update_settings(db: Session, data):
        settings = db.query(Settings).filter(Settings.id == 1).first()
        if not settings:
            settings = Settings(id=1)
            db.add(settings)
        d = to_dict(data)
        for key, value in d.items():
            if value is not None:
                setattr(settings, key, value)
        db.commit()
        db.refresh(settings)
        return settings
