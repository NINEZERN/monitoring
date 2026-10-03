import hashlib
import json
import tarfile
from pathlib import Path, PurePosixPath
from datetime import datetime
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from app.main import auth, row, require
from app.db import session
from app.config import settings
from app.models import Scan, Deployment, Service, uid, now
from app.analysis import utc

router = APIRouter(prefix="/api", dependencies=[Depends(auth)])

def validate_archive(path):
    # Inspect metadata only; never extract or execute user content.
    with tarfile.open(path, mode="r:") as archive:
        manifest = None
        names = set()
        count = 0
        for member in archive:
            count += 1
            p = PurePosixPath(member.name)
            if count > 100000 or p.is_absolute() or ".." in p.parts or member.issym() or member.islnk():
                raise ValueError("Небезопасная структура архива")
            names.add(member.name)
            if member.name == "manifest.json":
                if member.size > 1024 * 1024:
                    raise ValueError("Слишком большой manifest")
                manifest = json.load(archive.extractfile(member))
        if not isinstance(manifest, list) or not manifest:
            raise ValueError("Требуется несжатый архив docker save с manifest.json")
        for item in manifest:
            if not isinstance(item, dict) or item.get("Config") not in names or not isinstance(item.get("Layers"), list) or any(layer not in names for layer in item["Layers"]):
                raise ValueError("Неполный manifest docker save")

@router.post("/scans")
async def upload_image(file: UploadFile = File(...), db=Depends(session)):
    id = uid()
    folder = Path(settings.data_dir) / "images"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{id}.tar"
    size = 0
    digest = hashlib.sha256()
    try:
        with path.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_image_bytes:
                    raise HTTPException(413, "Максимальный размер образа: 512 MiB")
                out.write(chunk)
                digest.update(chunk)
        try:
            validate_archive(path)
        except (tarfile.TarError, ValueError, KeyError, TypeError, OSError):
            raise HTTPException(422, "Некорректный или небезопасный архив docker save")
        obj = Scan(id=id, filename=(file.filename or "image.tar")[:200], digest=digest.hexdigest())
        db.add(obj)
        db.commit()
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return row(obj)

@router.get("/scans")
def scans(db=Depends(session)):
    result = []
    for s in db.scalars(select(Scan).order_by(Scan.created_at.desc()).limit(100)):
        value = row(s)
        report = value.pop("result") or {}
        value["summary"] = report.get("summary")
        result.append(value)
    return result

@router.get("/scans/{id}")
def scan(id: str, db=Depends(session)):
    return row(require(db, Scan, id))

@router.post("/scans/{id}/retry")
def retry(id: str, db=Depends(session)):
    obj = require(db, Scan, id)
    if obj.status != "failed":
        raise HTTPException(409, "Повтор доступен для завершившегося ошибкой сканирования")
    obj.status, obj.error, obj.updated_at = "pending", None, now()
    db.commit()
    return row(obj)

class DeploymentInput(BaseModel):
    service_id: str
    scan_id: str
    started_at: datetime
    ended_at: datetime | None = None
    confirmation: Literal["unverified", "operator_confirmed"]
    evidence: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def check(self):
        if self.started_at.tzinfo is None or (self.ended_at and self.ended_at.tzinfo is None):
            raise ValueError("Укажите часовой пояс")
        if self.ended_at and self.ended_at <= self.started_at:
            raise ValueError("Конец периода должен быть позже начала")
        if self.confirmation == "operator_confirmed" and not self.evidence.strip():
            raise ValueError("Подтверждение требует обоснования: digest или ссылка на deployment")
        return self

@router.get("/deployments")
def deployments(db=Depends(session)):
    return [row(x) for x in db.scalars(select(Deployment).order_by(Deployment.started_at.desc()))]

@router.post("/deployments")
def create_deployment(data: DeploymentInput, db=Depends(session)):
    require(db, Service, data.service_id)
    require(db, Scan, data.scan_id)
    values = data.model_dump()
    values["started_at"] = utc(data.started_at)
    values["ended_at"] = utc(data.ended_at) if data.ended_at else None
    obj = Deployment(**values)
    db.add(obj)
    db.commit()
    return row(obj)
