# BenzinaChiara

MVP didattico per consultare e confrontare prezzi carburante e impianti. Il progetto usa FastAPI, SQLAlchemy/SQLite, Jinja2 e dataset MIMIT; i dati in `data/sample/` e gli account creati dal seed sono esclusivamente dimostrativi.

## Avvio rapido

Richiede Python 3.11 o superiore.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Prima di esporre l'app oltre il computer locale, imposta in `.env` un `SECRET_KEY` casuale e `COOKIE_SECURE=true` quando usi HTTPS. In locale, se `SECRET_KEY` è omesso, viene generata una chiave temporanea per il processo.

```powershell
python scripts\seed.py
uvicorn app.main:app --reload
```

Apri <http://127.0.0.1:8000>. Il seed stampa le password casuali degli account demo appena creati; gli indirizzi usano il dominio riservato `.invalid`.

## Import dati MIMIT

Per l'avvio offline sono disponibili CSV sintetici in `data/sample/`. L'import usa il separatore `;`, riconosce le intestazioni MIMIT, aggiorna i record già presenti e accetta filtri impostabili con `IMPORT_PROVINCE_FILTER` e `IMPORT_MAX_ROWS` nel file `.env`.

```powershell
python scripts\import_mimit.py
python scripts\import_mimit.py --impianti percorso\anagrafica_impianti_attivi.csv --prezzi percorso\prezzo_alle_8.csv --provincia TO --max-rows 500
```

## Test

```powershell
pytest
```

Le route e le relazioni principali sono descritte in [AGENTS.md](AGENTS.md).
