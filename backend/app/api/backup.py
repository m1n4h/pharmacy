from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.db.db import get_db
from app.services.backup_service import BackupService

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.post("/create")
def create_backup(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result, err = BackupService.create_backup()
    if err:
        return {"success": False, "message": "Backup failed", "error": err}
    return {"success": True, "message": "Backup created", "data": result}


@router.get("/list")
def list_backups(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return {"success": True, "message": "Backups", "data": BackupService.list_backups()}


@router.post("/restore")
def restore_backup(
    payload: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    filename = payload.get("filename")
    if not filename:
        return {"success": False, "message": "Filename required"}
    ok, msg = BackupService.restore_backup(filename)
    return {"success": ok, "message": "Restore complete" if ok else "Restore failed", "error": msg}
