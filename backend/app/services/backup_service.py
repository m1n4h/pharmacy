import os
import subprocess
import datetime
from pathlib import Path

BACKUP_DIR = Path("/home/egovridc25/Documents/PT_final/software_development/person/pharmarcy/backend/backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

DB_NAME = "pharmacy_db"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PASS = "egovridc"


class BackupService:

    @staticmethod
    def create_backup():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"pharmacy_backup_{ts}.sql"
        path = BACKUP_DIR / fname
        env = dict(os.environ)
        env["PGPASSWORD"] = DB_PASS
        result = subprocess.run(
            ["pg_dump", "-h", DB_HOST, "-U", DB_USER, "-F", "c", "-f", str(path), DB_NAME],
            env=env, capture_output=True, text=True
        )
        if result.returncode != 0:
            return None, result.stderr
        # size
        size = path.stat().st_size
        return {"filename": fname, "path": str(path), "size": size}, None

    @staticmethod
    def list_backups():
        files = sorted(BACKUP_DIR.glob("*.sql"), key=lambda p: p.stat().st_mtime, reverse=True)
        return [
            {
                "filename": f.name,
                "size": f.stat().st_size,
                "created_at": datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            for f in files
        ]

    @staticmethod
    def restore_backup(filename):
        path = BACKUP_DIR / filename
        if not path.exists():
            return False, "File not found"
        env = dict(os.environ)
        env["PGPASSWORD"] = DB_PASS
        # terminate + drop + recreate then restore
        subprocess.run(
            ["psql", "-h", DB_HOST, "-U", DB_USER, "-c", f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{DB_NAME}' AND pid<>pg_backend_pid();"],
            env=env, capture_output=True, text=True
        )
        subprocess.run(
            ["dropdb", "-h", DB_HOST, "-U", DB_USER, DB_NAME],
            env=env, capture_output=True, text=True
        )
        subprocess.run(
            ["createdb", "-h", DB_HOST, "-U", DB_USER, DB_NAME],
            env=env, capture_output=True, text=True
        )
        result = subprocess.run(
            ["pg_restore", "-h", DB_HOST, "-U", DB_USER, "-d", DB_NAME, "--no-owner", str(path)],
            env=env, capture_output=True, text=True
        )
        return True, result.stderr
