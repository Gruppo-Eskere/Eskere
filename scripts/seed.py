import secrets
from datetime import datetime, timezone
from decimal import Decimal
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Impianto, Prezzo, ReportStatus, Segnalazione, User, UserRole
from app.security import hash_password


def main() -> None:
    Base.metadata.create_all(bind=engine)
    demo_accounts = [
        ("Amministrazione Demo", "admin@benzina.example.invalid", UserRole.ADMIN),
        ("Alex Demo", "alex@benzina.example.invalid", UserRole.AUTOMOBILISTA),
        ("Sam Demo", "sam@benzina.example.invalid", UserRole.AUTOMOBILISTA),
    ]
    with SessionLocal() as db:
        credentials = {}
        users = {}
        for display_name, email, role in demo_accounts:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                password = secrets.token_urlsafe(15)
                user = User(
                    display_name=display_name,
                    email=email,
                    role=role,
                    password_hash=hash_password(password),
                )
                db.add(user)
                db.flush()
                credentials[email] = password
            users[email] = user

        sample_station_data = [
            ("DEMO-TO-001", "Stazione Demo Dora", "Demo Fuel", "Torino", "TO", "Corso Esempio 10", 45.08, 7.68),
            ("DEMO-CN-002", "Stazione Demo Langhe", "Carburanti Test", "Alba", "CN", "Via Fittizia 22", 44.70, 8.03),
        ]
        stations = []
        for external_id, name, brand, city, province, address, lat, lon in sample_station_data:
            station = db.scalar(select(Impianto).where(Impianto.id_impianto == external_id))
            if station is None:
                station = Impianto(
                    id_impianto=external_id, nome=name, gestore="Gestione Demo",
                    bandiera=brand, tipo_impianto="Stradale", indirizzo=address,
                    comune=city, provincia=province, latitudine=lat, longitudine=lon,
                )
                db.add(station)
                db.flush()
                for fuel, amount, is_self in (
                    ("Benzina", "1.789", True), ("Gasolio", "1.699", True), ("GPL", "0.729", False)
                ):
                    db.add(Prezzo(
                        id_impianto=station.id, carburante=fuel, prezzo=Decimal(amount),
                        is_self=is_self, data_comunicazione=datetime.now(timezone.utc),
                    ))
            stations.append(station)

        if stations and not db.scalar(select(Segnalazione.id).limit(1)):
            db.add_all([
                Segnalazione(
                    id_impianto=stations[0].id, id_utente=users["alex@benzina.example.invalid"].id,
                    testo_libero="Esempio fittizio: area self-service pulita e accessibile.",
                    stato=ReportStatus.APPROVED,
                ),
                Segnalazione(
                    id_impianto=stations[1].id, id_utente=users["sam@benzina.example.invalid"].id,
                    testo_libero="Esempio fittizio: verificare il prezzo esposto prima del rifornimento.",
                    stato=ReportStatus.PENDING,
                ),
            ])
        db.commit()
    print("Account dimostrativi (dati completamente fittizi):")
    for email, password in credentials.items():
        print(f"  {email} / {password}")
    if not credentials:
        print("Gli account demo esistono già; nessuna password è stata rigenerata.")


if __name__ == "__main__":
    main()
