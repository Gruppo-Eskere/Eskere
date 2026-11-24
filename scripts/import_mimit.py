import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.services.mimit import import_mimit_files


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Importa i CSV Open Data MIMIT degli impianti e dei prezzi.")
    parser.add_argument("--impianti", type=Path, default=ROOT / "data/sample/anagrafica_impianti_attivi.csv")
    parser.add_argument("--prezzi", type=Path, default=ROOT / "data/sample/prezzo_alle_8.csv")
    parser.add_argument("--provincia", default=settings.import_province_filter)
    parser.add_argument("--max-rows", type=int, default=settings.import_max_rows)
    args = parser.parse_args()
    if args.max_rows < 0:
        parser.error("--max-rows deve essere maggiore o uguale a zero")
    for path in (args.impianti, args.prezzi):
        if not path.is_file():
            parser.error(f"File non trovato: {path}")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        result = import_mimit_files(
            db, args.impianti, args.prezzi,
            province_filter=args.provincia, max_rows=args.max_rows,
        )
    print(f"Import completato: {result['impianti']} impianti e {result['prezzi']} prezzi.")


if __name__ == "__main__":
    main()
