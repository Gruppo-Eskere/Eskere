# Eskere Chiara Minardi Raffaella Laura Storelli e Leonardo Molinari
Docente: Vito Bavaro
# 1. Nome e descrizione

# BenzinaChiara

**BenzinaChiara** è un'applicazione web sviluppata per il laboratorio universitario di **Modelli e Metodi per la Qualità del Software (MMQS)** nell'ambito del tema **Trasporti - Prezzi dei carburanti MIMIT**.

L'obiettivo del progetto è fornire uno strumento semplice e trasparente per la consultazione e il confronto dei prezzi dei carburanti in Italia utilizzando i dati pubblicati dal **Ministero delle Imprese e del Made in Italy (MIMIT)**.

L'applicazione consente agli utenti di:

- consultare gli impianti di distribuzione carburante;
- confrontare i prezzi dei diversi carburanti;
- filtrare i risultati per area geografica e tipologia di carburante;
- inviare segnalazioni testuali sugli impianti;
- monitorare eventuali discrepanze tra i prezzi comunicati e quelli effettivamente praticati.

Sono previsti due ruoli principali:

- **Automobilista**: può consultare impianti e prezzi, utilizzare i filtri di ricerca e inviare segnalazioni.
- **Admin**: può gestire i dati del sistema, moderare le segnalazioni e aggiornare i prezzi tramite caricamento di file.

---

# 2. Gruppo

| Nome e Cognome | GitHub Username |
|---------------|----------------|
| Minardi Chiara | clairetex06 |
| Molinari Leonardo | leonardomol1509 |
| Storelli Raffaella Laura | RaffaLaurasto |

---

# 3. Dati

L'applicazione utilizza il dataset pubblico **"Prezzi Carburanti e Impianti"** reso disponibile dal **Ministero delle Imprese e del Made in Italy (MIMIT)**.

Fonte ufficiale:

https://www.mimit.gov.it

Dataset utilizzati:

- `anagrafica_impianti_attivi.csv`
- `prezzo_alle_8.csv`

Per consentire l'avvio immediato del progetto anche in assenza di connessione Internet o del dataset completo, il repository include dati campione nella cartella:

```text
data/sample/
```

contenente:

```text
anagrafica_impianti_attivi.csv
prezzo_alle_8.csv
```

## Import dati

Lo script:

```text
scripts/import_mimit.py
```

si occupa di:

1. leggere i file CSV MIMIT;
2. gestire il separatore ufficiale `;`;
3. applicare eventuali filtri per provincia;
4. limitare il numero di record importati;
5. aggiornare gli impianti esistenti;
6. importare i prezzi associati agli impianti.

I parametri di import sono configurabili tramite variabili d'ambiente:

```env
IMPORT_PROVINCE_FILTER
IMPORT_MAX_ROWS
```

---

# 4. Funzionalità

## Autenticazione

- Registrazione utenti
- Login
- Logout
- Gestione ruoli
- Password salvate tramite hashing sicuro

## Ricerca impianti

- Ricerca per comune
- Ricerca per provincia
- Filtri per carburante
- Ordinamento per prezzo

## Gestione segnalazioni

Gli utenti autenticati possono:

- creare segnalazioni testuali;
- modificare le proprie segnalazioni;
- eliminare le proprie segnalazioni.

Esempi:

- prezzi non aggiornati;
- colonnine fuori servizio;
- code anomale;
- servizi mancanti.

## Gestione amministrativa

Gli amministratori possono:

- creare impianti;
- modificare impianti;
- eliminare impianti;
- aggiornare i prezzi;
- moderare le segnalazioni.

## Upload aggiornamenti

L'amministratore può caricare:

```text
.csv
.json
```

contenenti aggiornamenti dei prezzi carburante.

## API esterna

L'applicazione integra il servizio:

**Open-Meteo**

per visualizzare informazioni meteorologiche associate alle coordinate geografiche degli impianti.

## Screenshot

Eventuali screenshot dell'applicazione possono essere inseriti nella cartella:

```text
docs/screenshots/
```

e referenziati in questa sezione.

---

# 5. Architettura

## Stack tecnologico

| Componente | Tecnologia |
|-----------|------------|
| Linguaggio | Python 3.11+ |
| Framework Web | FastAPI |
| Server ASGI | Uvicorn |
| ORM | SQLAlchemy |
| Database | SQLite |
| Template Engine | Jinja2 |
| Form Upload | python-multipart |
| HTTP Client | httpx |
| Testing | pytest |
| Configurazione | pydantic-settings |

## API esterna

- Open-Meteo

## Struttura del repository

```text
app/
├── config.py
├── database.py
├── dependencies.py
├── main.py
├── security.py
│
├── models/
├── routers/
├── schemas/
├── services/
├── templates/
└── static/

scripts/
├── import_mimit.py
└── seed.py

data/
└── sample/

tests/

requirements.txt
.env.example
AGENTS.md
README.md
```

### Layer applicativi

**Models**
- Entità SQLAlchemy.

**Schemas**
- Modelli Pydantic per validazione e serializzazione.

**Routers**
- Endpoint FastAPI.

**Services**
- Logica applicativa e integrazione con servizi esterni.

**Templates**
- Interfaccia HTML server-side mediante Jinja2.

---

# 6. Come avviarla

## Requisiti

- Python 3.11 o superiore
- pip
- Git

## Installazione

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Variabili d'ambiente

| Variabile | Descrizione |
|-----------|------------|
| SECRET_KEY | Chiave utilizzata per sessioni e sicurezza |
| DATABASE_URL | URL del database SQLite |
| EXTERNAL_API_BASE_URL | URL dell'API Open-Meteo |
| IMPORT_PROVINCE_FILTER | Filtro opzionale provincia |
| IMPORT_MAX_ROWS | Numero massimo di righe da importare |

## Import dati MIMIT

```powershell
python scripts\import_mimit.py
```

Esempio avanzato:

```powershell
python scripts\import_mimit.py --impianti percorso\anagrafica_impianti_attivi.csv --prezzi percorso\prezzo_alle_8.csv --provincia TO --max-rows 500
```

## Seeding dati

```powershell
python scripts\seed.py
```

## Avvio applicazione

```powershell
uvicorn app.main:app --reload
```

Applicazione disponibile all'indirizzo:

```text
http://127.0.0.1:8000
```

## Utenti dimostrativi

Gli utenti di esempio vengono creati dallo script:

```powershell
python scripts\seed.py
```

Le credenziali generate vengono mostrate nel terminale al momento della creazione.

| Ruolo | Username/Email |
|---------|---------|
| Admin | generato dal seed |
| Automobilista | generato dal seed |
| Automobilista | generato dal seed |

Tutti gli account utilizzano dati fittizi e indirizzi con dominio `.invalid`.

## Test automatici

```powershell
pytest
```

---

# 7. Sviluppo con i coding agent

Durante lo sviluppo sono stati utilizzati strumenti di assistenza basati su intelligenza artificiale.

## Coding agent utilizzati

- GitHub Copilot
- GitHub Copilot Agent Mode
- Microsoft Copilot

## Approccio adottato

Lo sviluppo è stato organizzato nelle seguenti fasi:

1. Pianificazione iniziale dell'architettura.
2. Definizione dello schema relazionale.
3. Implementazione modulare di:
   - autenticazione;
   - gestione impianti;
   - import dati;
   - segnalazioni;
   - upload file.
4. Scrittura e verifica dei test automatici.
5. Correzione delle dipendenze e dei problemi di configurazione.

## AGENTS.md

Il file:

```text
AGENTS.md
```

descrive:

- struttura del progetto;
- convenzioni di sviluppo;
- comandi di avvio;
- procedure di import;
- regole di sicurezza;
- organizzazione del codice.

## Skill utilizzate

Non sono state utilizzate skill personalizzate esterne al repository.

---

# 8. Lavoro di gruppo

## Minardi Chiara (clairetex06)

- Setup repository e ambiente di sviluppo.
- Verifica dell'avvio dell'applicazione.
- Test dell'import dati e della configurazione locale.
- Validazione finale del funzionamento.

## Molinari Leonardo (leonardomol1509)

- Definizione dei requisiti funzionali.
- Progettazione dell'architettura generale.
- Supporto alla progettazione del modello dati.

## Storelli Raffaella Laura (RaffaLaurasto)

- Analisi dei dati.
- Supporto ai test funzionali.
- Revisione della documentazione.

## Branch

Durante lo sviluppo sono stati utilizzati branch Git dedicati alle attività del gruppo.

Esempi:

```text
main
conflitto-chiara
```

Ulteriori branch e merge possono essere consultati direttamente nella cronologia Git del repository.

---

# 9. Limiti noti

L'applicazione rappresenta un MVP universitario e presenta alcune limitazioni:

- utilizza SQLite e non un database destinato ad ambienti ad alta concorrenza;
- il dataset incluso nel repository è un estratto ridotto rispetto ai dati ufficiali MIMIT;
- non è presente una visualizzazione cartografica degli impianti;
- non è stato implementato un sistema di notifiche;
- non è presente un sistema avanzato di moderazione delle segnalazioni;
- le informazioni meteorologiche dipendono dalla disponibilità del servizio Open-Meteo;
- l'applicazione non è stata progettata per il deployment in produzione su larga scala.

Tutti i dati di esempio e gli account creati tramite `seed.py` sono fittizi e utilizzati esclusivamente a fini didattici.
