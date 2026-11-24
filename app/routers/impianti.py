from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies import require_user
from app.models import Impianto, Preferito, ReportStatus, Segnalazione, User
from app.services.weather import current_weather

router = APIRouter(tags=["impianti"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    return search_impianti(request, db=db)


@router.get("/impianti", response_class=HTMLResponse)
def search_impianti(
    request: Request,
    comune: str = "",
    provincia: str = "",
    bandiera: str = "",
    carburante: str = "",
    modalita: str = "",
    db: Session = Depends(get_db),
):
    statement = select(Impianto).options(selectinload(Impianto.prices))
    if comune:
        statement = statement.where(Impianto.comune.ilike(f"%{comune.strip()}%"))
    if provincia:
        statement = statement.where(Impianto.provincia.ilike(provincia.strip()))
    if bandiera:
        statement = statement.where(Impianto.bandiera.ilike(f"%{bandiera.strip()}%"))
    stations = list(db.scalars(statement).unique())
    if carburante:
        stations = [
            station for station in stations
            if any(price.carburante.casefold() == carburante.casefold() for price in station.prices)
        ]
    if modalita:
        self_service = modalita.lower() == "self"
        stations = [
            station for station in stations
            if any(price.is_self == self_service and (not carburante or price.carburante.casefold() == carburante.casefold())
                   for price in station.prices)
        ]
    def best_price(station: Impianto) -> float:
        matching = [
            float(price.prezzo) for price in station.prices
            if (not carburante or price.carburante.casefold() == carburante.casefold())
            and (not modalita or price.is_self == (modalita.lower() == "self"))
        ]
        return min(matching, default=float("inf"))
    stations.sort(key=best_price)
    return request.app.state.templates.TemplateResponse(
        request,
        "index.html",
        {
            "impianti": stations,
            "filters": {
                "comune": comune, "provincia": provincia, "bandiera": bandiera,
                "carburante": carburante, "modalita": modalita,
            },
        },
    )


@router.get("/impianti/{impianto_id}", response_class=HTMLResponse)
async def impianto_detail(request: Request, impianto_id: int, db: Session = Depends(get_db)):
    station = db.scalar(
        select(Impianto)
        .options(selectinload(Impianto.prices), selectinload(Impianto.reports).selectinload(Segnalazione.user))
        .where(Impianto.id == impianto_id)
    )
    if station is None:
        raise HTTPException(status_code=404, detail="Impianto non trovato")
    reports = [
        report for report in station.reports
        if report.stato == ReportStatus.APPROVED
        or (request.session.get("user_id") == report.id_utente)
    ]
    weather = None
    weather_error = None
    if station.latitudine is not None and station.longitudine is not None:
        try:
            weather = await current_weather(station.latitudine, station.longitudine)
        except (httpx.HTTPError, ValueError) as exc:
            request.app.state.logger.warning("Servizio meteo non disponibile: %s", exc)
            weather_error = "Meteo temporaneamente non disponibile"
    return request.app.state.templates.TemplateResponse(
        request, "detail.html", {"impianto": station, "segnalazioni": reports, "weather": weather, "weather_error": weather_error}
    )


@router.post("/impianti/{impianto_id}/preferiti")
def toggle_favorite(
    impianto_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    station = db.get(Impianto, impianto_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Impianto non trovato")
    favorite = db.scalar(
        select(Preferito).where(Preferito.id_utente == user.id, Preferito.id_impianto == impianto_id)
    )
    if favorite:
        db.delete(favorite)
    else:
        db.add(Preferito(id_utente=user.id, id_impianto=impianto_id))
    db.commit()
    return RedirectResponse(f"/impianti/{impianto_id}", status_code=303)

