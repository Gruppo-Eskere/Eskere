import csv
import re
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TextIO

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Impianto, Prezzo
from app.schemas import ImpiantoInput, PriceInput


def _key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in normalized if not unicodedata.combining(c)))


def _value(row: dict[str, str], *names: str, default: str = "") -> str:
    fields = {_key(key): (value or "").strip() for key, value in row.items() if key}
    for name in names:
        if _key(name) in fields:
            return fields[_key(name)]
    return default


def _number(value: str) -> float | None:
    if not value:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def parse_impianto(row: dict[str, str]) -> ImpiantoInput:
    return ImpiantoInput(
        id_impianto=_value(row, "idImpianto", "id_impianto", "id"),
        gestore=_value(row, "Gestore", "gestore"),
        bandiera=_value(row, "Bandiera", "bandiera"),
        tipo_impianto=_value(row, "Tipo Impianto", "tipo_impianto", "Tipo"),
        nome=_value(row, "Nome Impianto", "nomeImpianto", "nome"),
        indirizzo=_value(row, "Indirizzo", "indirizzo"),
        comune=_value(row, "Comune", "comune"),
        provincia=_value(row, "Provincia", "provincia").upper(),
        latitudine=_number(_value(row, "Latitudine", "latitudine")),
        longitudine=_number(_value(row, "Longitudine", "longitudine")),
    )


def parse_price(row: dict[str, str]) -> PriceInput:
    raw_price = _value(row, "prezzo", "Prezzo")
    try:
        price = Decimal(raw_price.replace(",", "."))
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError(f"Prezzo non valido: {raw_price}") from exc
    raw_self = _value(row, "isSelf", "is_self", "self", default="true").lower()
    is_self = raw_self in {"true", "1", "si", "sì", "yes"}
    date_text = _value(row, "dtComu", "data_comunicazione", "dataComunicazione", "data")
    communicated_at = None
    if date_text:
        try:
            communicated_at = datetime.fromisoformat(date_text.replace("Z", "+00:00"))
        except ValueError:
            communicated_at = None
    return PriceInput(
        id_impianto=_value(row, "idImpianto", "id_impianto", "id"),
        carburante=_value(row, "descCarburante", "carburante", "prodotto", "descrizione"),
        prezzo=price,
        is_self=is_self,
        data_comunicazione=communicated_at,
    )


def import_mimit_files(
    db: Session,
    impianti_path: Path,
    prezzi_path: Path,
    province_filter: str = "",
    max_rows: int = 0,
) -> dict[str, int]:
    station_rows = read_csv(impianti_path)
    if max_rows > 0:
        station_rows = station_rows[:max_rows]

    imported_stations = 0
    station_ids: set[str] = set()
    for row in station_rows:
        try:
            item = parse_impianto(row)
        except ValidationError:
            continue
        if province_filter and item.provincia.upper() != province_filter.upper():
            continue
        station_ids.add(item.id_impianto)
        station = db.scalar(select(Impianto).where(Impianto.id_impianto == item.id_impianto))
        if station is None:
            station = Impianto(**item.model_dump())
            db.add(station)
        else:
            for key, value in item.model_dump().items():
                setattr(station, key, value)
        imported_stations += 1
    db.flush()

    price_rows = read_csv(prezzi_path)
    if max_rows > 0:
        price_rows = price_rows[:max_rows]
    imported_prices = 0
    for row in price_rows:
        try:
            item = parse_price(row)
            validated = PriceInput.model_validate(item)
        except (ValidationError, ValueError):
            continue
        if validated.id_impianto not in station_ids:
            continue
        station = db.scalar(select(Impianto).where(Impianto.id_impianto == validated.id_impianto))
        if station is None:
            continue
        communicated_at = validated.data_comunicazione or datetime.now(timezone.utc)
        price = db.scalar(
            select(Prezzo).where(
                Prezzo.id_impianto == station.id,
                Prezzo.carburante == validated.carburante,
                Prezzo.is_self == validated.is_self,
            )
        )
        values = {
            "prezzo": validated.prezzo,
            "data_comunicazione": communicated_at,
        }
        if price is None:
            db.add(Prezzo(id_impianto=station.id, carburante=validated.carburante, is_self=validated.is_self, **values))
        else:
            for key, value in values.items():
                setattr(price, key, value)
        imported_prices += 1
    db.commit()
    return {"impianti": imported_stations, "prezzi": imported_prices}
