from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_user
from app.models import Impianto, ReportStatus, Segnalazione, User


router = APIRouter(tags=["segnalazioni"])


@router.post("/impianti/{impianto_id}/segnalazioni")
def create_report(
    impianto_id: int,
    testo_libero: str = Form(min_length=5, max_length=2000),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    station = db.get(Impianto, impianto_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Impianto non trovato")
    db.add(Segnalazione(
        id_impianto=impianto_id,
        id_utente=user.id,
        testo_libero=testo_libero.strip(),
    ))
    db.commit()
    return RedirectResponse(f"/impianti/{impianto_id}", status_code=303)


@router.post("/segnalazioni/{report_id}/modifica")
def edit_report(
    report_id: int,
    testo_libero: str = Form(min_length=5, max_length=2000),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    report = db.get(Segnalazione, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Segnalazione non trovata")
    if report.id_utente != user.id:
        raise HTTPException(status_code=403, detail="Puoi modificare solo le tue segnalazioni")
    report.testo_libero = testo_libero.strip()
    report.stato = ReportStatus.PENDING
    db.commit()
    return RedirectResponse(f"/impianti/{report.id_impianto}", status_code=303)


@router.post("/segnalazioni/{report_id}/elimina")
def delete_report(
    report_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    report = db.get(Segnalazione, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Segnalazione non trovata")
    if report.id_utente != user.id:
        raise HTTPException(status_code=403, detail="Puoi eliminare solo le tue segnalazioni")
    station_id = report.id_impianto
    db.delete(report)
    db.commit()
    return RedirectResponse(f"/impianti/{station_id}", status_code=303)
