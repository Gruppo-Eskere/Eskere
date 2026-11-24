import csv
import io
import json
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies import require_admin
from app.models import Impianto, Prezzo, ReportStatus, Segnalazione, User
from app.schemas import ImpiantoInput, PriceInput
from app.services.mimit import parse_price

router = APIRouter(prefix="/admin", tags=["amministrazione"], dependencies=[Depends(require_admin)])


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    stations = db.scalars(select(Impianto).options(selectinload(Impianto.prices)).order_by(Impianto.comune)).all()
    reports = db.scalars(
        select(Segnalazione).options(selectinload(Segnalazione.user), selectinload(Segnalazione.impianto))
        .order_by(Segnalazione.created_at.desc())
    ).all()
    return request.app.state.templates.TemplateResponse(
        request, "admin.html", {"impianti": stations, "segnalazioni": reports}
    )


@router.post("/impianti")
def create_station(
    id_impianto: str = Form(), gestore: str = Form(""), bandiera: str = Form(""),
    tipo_impianto: str = Form(""), nome: str = Form(""), indirizzo: str = Form(""),
    comune: str = Form(), provincia: str = Form(), latitudine: float | None = Form(None),
    longitudine: float | None = Form(None), user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        station = Impianto(**ImpiantoInput(
            id_impianto=id_impianto, gestore=gestore, bandiera=bandiera, tipo_impianto=tipo_impianto,
            nome=nome, indirizzo=indirizzo, comune=comune, provincia=provincia,
            latitudine=latitudine, longitudine=longitudine,
        ).model_dump())
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    if db.scalar(select(Impianto).where(Impianto.id_impianto == station.id_impianto)):
        raise HTTPException(status_code=409, detail="ID impianto già presente")
    db.add(station)
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.post("/impianti/{station_id}/modifica")
def update_station(
    station_id: int, gestore: str = Form(""), bandiera: str = Form(""),
    tipo_impianto: str = Form(""), nome: str = Form(""), indirizzo: str = Form(""),
    comune: str = Form(), provincia: str = Form(), latitudine: float | None = Form(None),
    longitudine: float | None = Form(None), db: Session = Depends(get_db),
):
    station = db.get(Impianto, station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Impianto non trovato")
    values = ImpiantoInput(
        id_impianto=station.id_impianto, gestore=gestore, bandiera=bandiera, tipo_impianto=tipo_impianto,
        nome=nome, indirizzo=indirizzo, comune=comune, provincia=provincia,
        latitudine=latitudine, longitudine=longitudine,
    )
    for key, value in values.model_dump().items():
        setattr(station, key, value)
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.post("/impianti/{station_id}/elimina")
def delete_station(station_id: int, db: Session = Depends(get_db)):
    station = db.get(Impianto, station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Impianto non trovato")
    db.delete(station)
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.post("/impianti/{station_id}/prezzi")
def create_price(
    station_id: int,
    carburante: str = Form(), prezzo: Decimal = Form(gt=0), is_self: bool = Form(False),
    db: Session = Depends(get_db),
):
    if db.get(Impianto, station_id) is None:
        raise HTTPException(status_code=404, detail="Impianto non trovato")
    price = PriceInput(id_impianto=str(station_id), carburante=carburante, prezzo=prezzo, is_self=is_self)
    db.add(Prezzo(
        id_impianto=station_id, carburante=price.carburante, prezzo=price.prezzo,
        is_self=price.is_self, data_comunicazione=datetime.now(timezone.utc),
    ))
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.post("/prezzi/{price_id}/modifica")
def update_price(
    price_id: int, carburante: str = Form(), prezzo: Decimal = Form(gt=0),
    is_self: bool = Form(False), db: Session = Depends(get_db),
):
    price = db.get(Prezzo, price_id)
    if price is None:
        raise HTTPException(status_code=404, detail="Prezzo non trovato")
    validated = PriceInput(
        id_impianto=str(price.id_impianto), carburante=carburante, prezzo=prezzo, is_self=is_self
    )
    price.carburante = validated.carburante
    price.prezzo = validated.prezzo
    price.is_self = validated.is_self
    price.data_comunicazione = datetime.now(timezone.utc)
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.post("/prezzi/{price_id}/elimina")
def delete_price(price_id: int, db: Session = Depends(get_db)):
    price = db.get(Prezzo, price_id)
    if price is None:
        raise HTTPException(status_code=404, detail="Prezzo non trovato")
    db.delete(price)
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.post("/segnalazioni/{report_id}/moderazione")
def moderate_report(report_id: int, stato: str = Form(), db: Session = Depends(get_db)):
    try:
        report_status = ReportStatus(stato)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Stato di moderazione non valido") from exc
    report = db.get(Segnalazione, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Segnalazione non trovata")
    report.stato = report_status
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.get("/importazione", response_class=HTMLResponse)
def import_page(request: Request):
    return request.app.state.templates.TemplateResponse(request, "upload.html", {"result": None, "error": None})


@router.post("/importazione", response_class=HTMLResponse)
async def upload_prices(
    request: Request,
    file: UploadFile = File(),
    db: Session = Depends(get_db),
):
    template = request.app.state.templates
    if not file.filename or not file.filename.lower().endswith((".csv", ".json")):
        return template.TemplateResponse(request, "upload.html", {"result": None, "error": "Carica un file CSV o JSON"}, status_code=400)
    raw_content = await file.read(2_000_001)
    if len(raw_content) > 2_000_000:
        return template.TemplateResponse(request, "upload.html", {"result": None, "error": "File oltre il limite di 2 MB"}, status_code=413)
    try:
        content = raw_content.decode("utf-8-sig")
        if file.filename.lower().endswith(".json"):
            rows = json.loads(content)
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ValueError("Il JSON deve contenere un array di oggetti")
        else:
            rows = list(csv.DictReader(io.StringIO(content), delimiter=";"))
        validated_rows = [parse_price(row) for row in rows]
        validated_rows = [PriceInput.model_validate(row) for row in validated_rows]
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, ValidationError, TypeError) as exc:
        return template.TemplateResponse(
            request, "upload.html", {"result": None, "error": f"File non valido: {exc}"}, status_code=400
        )
    stations = {
        station.id_impianto: station
        for station in db.scalars(
            select(Impianto).where(Impianto.id_impianto.in_({row.id_impianto for row in validated_rows}))
        )
    }
    missing = sorted({row.id_impianto for row in validated_rows} - stations.keys())
    if missing:
        return template.TemplateResponse(
            request, "upload.html",
            {"result": None, "error": f"Impianti non trovati: {', '.join(missing[:10])}"}, status_code=400,
        )
    for row in validated_rows:
        station = stations[row.id_impianto]
        price = db.scalar(
            select(Prezzo).where(
                Prezzo.id_impianto == station.id,
                Prezzo.carburante == row.carburante,
                Prezzo.is_self == row.is_self,
            )
        )
        timestamp = row.data_comunicazione or datetime.now(timezone.utc)
        if price is None:
            db.add(Prezzo(
                id_impianto=station.id, carburante=row.carburante, prezzo=row.prezzo,
                is_self=row.is_self, data_comunicazione=timestamp,
            ))
        else:
            price.prezzo = row.prezzo
            price.data_comunicazione = timestamp
    db.commit()
    return template.TemplateResponse(
        request, "upload.html", {"result": f"Aggiornati {len(validated_rows)} prezzi", "error": None}
    )
