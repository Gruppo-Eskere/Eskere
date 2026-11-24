# BenzinaChiara: guida per agenti e sviluppatori

## Architettura

- `app/main.py` espone l'app FastAPI e crea lo schema all'avvio.
- `app/config.py` carica impostazioni da `.env`; `app/database.py` centralizza engine e sessioni SQLAlchemy.
- `app/models.py` contiene le entità dichiarative; `app/schemas.py` valida input e import.
- `app/routers/` separa autenticazione, consultazione impianti/segnalazioni e operazioni amministrative.
- `app/services/mimit.py` importa e normalizza CSV MIMIT; `app/services/weather.py` interroga Open-Meteo tramite HTTPX.
- `templates/` contiene i template Jinja2 e `static/` il CSS responsive.
- `scripts/` include import e seed; `data/sample/` contiene solo esempi sintetici; `tests/` usa un database SQLite in memoria.

## Modello relazionale

- `users`: email univoca, password hash scrypt e ruolo `automobilista` o `admin`.
- `impianti`: identificativo MIMIT univoco, gestore, bandiera, tipo, nome, indirizzo, comune, provincia e coordinate.
- `prezzi`: relazione verso un impianto, carburante, prezzo, modalità self/servito e data di comunicazione.
- `segnalazioni`: relazione verso impianto e autore, testo libero, stato di moderazione e data.
- `preferiti`: tabella di associazione utente-impianto con coppia univoca.

## Route principali

- `GET /`, `GET /impianti`: ricerca per comune, provincia, bandiera, carburante e modalità; prezzi ordinati dal più conveniente.
- `GET /impianti/{id}`: dettaglio, listino, meteo Open-Meteo (se ci sono coordinate) e segnalazioni approvate o proprie.
- `GET/POST /auth/login`, `GET/POST /auth/registrazione`, `POST /auth/logout`: sessione firmata e cookie HttpOnly.
- `POST /impianti/{id}/preferiti`: aggiunge/rimuove un preferito per l'utente autenticato.
- `POST /impianti/{id}/segnalazioni`, `POST /segnalazioni/{id}/modifica`, `POST /segnalazioni/{id}/elimina`: CRUD delle segnalazioni dell'autore.
- `GET/POST /admin/impianti`, `POST /admin/impianti/{id}/modifica`, `POST /admin/impianti/{id}/elimina`: CRUD impianti.
- `POST /admin/impianti/{id}/prezzi`, `POST /admin/prezzi/{id}/modifica`, `POST /admin/prezzi/{id}/elimina`: CRUD listini.
- `GET/POST /admin/importazione`: validazione e aggiornamento massivo prezzi da CSV/JSON; `POST /admin/segnalazioni/{id}/moderazione`: moderazione.

## Comandi

```powershell
Copy-Item .env.example .env
python scripts\seed.py
python scripts\import_mimit.py
uvicorn app.main:app --reload
pytest
```

L'account admin e i due utenti dimostrativi del seed hanno email fittizie nel dominio `.invalid`. Le password vengono generate casualmente e stampate soltanto alla prima creazione degli account; non sono credenziali predefinite.

## Sicurezza e dati

- Non inserire mai password reali, token o chiavi in sorgenti o repository. Conservare configurazione locale in `.env`, escluso da Git; sostituire i segnaposto di `.env.example`.
- Le password sono hashate con scrypt; il cookie di sessione è firmato, HttpOnly e SameSite=Lax. Abilitare `COOKIE_SECURE=true` quando il sito è servito esclusivamente su HTTPS.
- La registrazione assegna sempre il ruolo `automobilista`; non consentire al client di scegliere il ruolo.
- Limitare gli upload a CSV/JSON UTF-8 fino a 2 MB; validare l'intero contenuto prima di applicare le modifiche.
- Usare solo dati di test inventati nel seed e nei CSV di esempio. Non aggiungere dati personali reali o condividere credenziali di test.
