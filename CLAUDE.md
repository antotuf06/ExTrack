# Dashboard Spese & Investimenti

App personale mono-utente che importa lo storico spese da Excel, acquisisce le transazioni bancarie e mostra spese per categoria e andamento degli investimenti in una dashboard locale.

## Documento di design (fonte di verità)

Il design completo è in `docs/design-dashboard-spese.md`; la panoramica con diagrammi (in inglese) è in `docs/ARCHITECTURE.md` e va aggiornata insieme al design. **Non è importato qui per non occupare contesto: leggi la sezione pertinente prima di lavorare su un'area.**

| Lavoro su… | Leggi la sezione |
|---|---|
| Decisioni prese e motivazioni | 5 e 17 |
| Architettura, stack, deployment | 6 |
| Schema del database | 7 |
| Import Excel / CSV / Open Banking / manuale / investimenti | 8 |
| Deduplicazione | 9 |
| Regole di categorizzazione | 10 |
| Viste della dashboard | 11 |
| Endpoint API | 12 |
| Sicurezza | 13 |
| Fasi e ordine di lavoro | 15 |

Se un'implementazione richiede di discostarsi dal design, **fermati e chiedi**. Se una decisione cambia, aggiorna il documento di design nello stesso lavoro.

## Stato attuale

<!-- Aggiornare a ogni cambio di fase. -->
- Fase corrente: **1 — MVP** (DB, import Excel, inserimento manuale, categorie, dashboard base, export, backup, script di avvio).
- Ambiente del committente: **Windows 11**. Usa `pathlib` per i percorsi, encoding `utf-8` esplicito, niente comandi solo-Unix; avvio con `start.bat`.
- Conti: **Trade Republic** (principale: spese con carta e investimenti) e **Intesa Sanpaolo** (secondario).
- Excel storico: **un foglio, 12 mesi affiancati** in blocchi di 10 colonne; sezioni **Spesa / Affitto / Abbonamenti / Varie** con colonne Importo + Motivo; niente giorno né anno (→ `date_precision = 'month'`, anno chiesto all'import). Layout esatto: design sez. 8.1.
- Trade Republic: import da **PDF estratto conto** (layout in design sez. 8.2.1, con validazione bloccante sul saldo progressivo) e, quando arriverà un esempio, da **CSV**.
- **Data di taglio** Excel/banca attorno ad agosto 2026 (`CUTOFF_DATE` in configurazione, valore esatto da confermare): prima fa fede l'Excel, dopo l'estratto conto. L'inserimento manuale resta possibile per qualsiasi data.
- Ancora aperti: esempi dell'export CSV Trade Republic e dell'export Intesa (I5). Non inventare quei formati: chiedi un file d'esempio con dati finti.
- Non lavorare su fasi successive a quella corrente se non richiesto.

## Stack

- Backend: Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic, SQLite.
- Frontend: SPA Svelte 5 + Vite in `frontend/`, grafici ECharts; compilata e servita dal backend.
- Job: APScheduler in-process (sync e backup all'avvio, poi periodici).
- Config: `data/.env` per segreti e percorsi (modello: `.env.example`), `config.yaml` (in git, senza dati personali) per mapping colonne e profili banca.

## Struttura

<!-- Aggiornare quando il progetto esiste. -->
```
backend/app/
  api/          # router FastAPI, solo HTTP: niente logica di business
  models/       # modelli SQLAlchemy
  ingestion/    # adapter delle sorgenti + pipeline (normalizza → dedup → categorizza → salva)
  services/     # statistiche, regole, export, backup
  jobs/         # job pianificati
backend/migrations/  # Alembic
backend/tests/  # pytest, fixture con dati finti in tests/fixtures/
frontend/
docs/           # documento di design
data/           # DB, backup, .env — MAI in git
```

## Comandi

<!-- Verificare e aggiornare quando il progetto esiste. -->
- Installa: `uv sync` (backend), `npm install` in `frontend/`
- Avvio sviluppo: `uv run fastapi dev backend/app/main.py` e `npm run dev` in `frontend/`
- Test: `uv run pytest`
- Lint e formattazione: `uv run ruff check . && uv run ruff format .`
- Migrazioni: `uv run alembic revision --autogenerate -m "<descrizione>"` poi `uv run alembic upgrade head`

Prima di dichiarare finito un lavoro: test e lint devono passare.

## Regole di dominio (non negoziabili)

- **Importi in centesimi interi** (`amount_cents: int`), mai float. Negativo = uscita, positivo = entrata.
- Date ISO 8601, fuso `Europe/Rome`. Parsing input in formato italiano: `gg/mm/aaaa`, `1.234,56`, `€`.
- `description_raw` conserva il testo originale della sorgente e non va mai modificato.
- Gli adapter producono `RawTransaction` e **non scrivono mai direttamente sul DB**: tutto passa dalla pipeline di ingestione.
- La dashboard legge solo dal DB, mai dalle sorgenti esterne.
- Ogni import crea un `import_batch` annullabile e supporta `dry_run`.
- I trasferimenti tra conti propri e le operazioni di investimento su Trade Republic (acquisti, vendite, piani di accumulo) hanno `is_transfer = true` e sono **esclusi** dalle statistiche di spesa. Classificali dal tipo di movimento del CSV, non dalla descrizione.
- Le regole di categorizzazione non sovrascrivono mai transazioni con `category_locked = true`.
- I duplicati tra sorgenti diverse si **propongono** all'utente, non si fondono in automatico.

## Sicurezza e privacy

- Il server ascolta su `127.0.0.1` di default. L'accesso LAN (`LISTEN_LAN=true`) richiede login obbligatorio.
- Segreti solo in `.env` / file chiave in `data/`. Mai nel codice, nei log, nel frontend o in git.
- Niente dati finanziari reali nei test, nelle fixture, negli esempi o nei commit. Le fixture Excel e PDF si **generano da script** con dati inventati, riproducendo il layout del design. I file reali del committente (Excel, estratti conto) non vanno mai copiati nel repository.
- Nei log niente IBAN completi né descrizioni di transazioni (salvo livello debug).
- Prima di aggiungere una dipendenza che fa chiamate di rete, chiedi.

## Fuori scope (non implementare)

- Integrazione diretta con Google Pay (non esiste un'API: i dati arrivano dalla banca).
- `pytr` o altre API non ufficiali di Trade Republic: gli investimenti sono snapshot manuali.
- Notifiche Android / webhook.
- GoCardless / Nordigen (chiuso a nuove registrazioni): per l'Open Banking si usa Enable Banking, in fase 3.
- Deployment cloud: l'app gira sul PC personale, ma il codice resta portabile (percorsi configurabili, niente dipendenze dal sistema operativo).

## Convenzioni

- Codice, nomi e commenti in inglese; testi dell'interfaccia in italiano.
- Type hint ovunque; schemi Pydantic per input/output dell'API.
- Logica di business nei `services/` e in `ingestion/`, testabile senza FastAPI.
- Ogni parser (Excel, profilo CSV) ha test con casi limite: celle vuote, righe di totale, formati misti, file reimportato due volte.
- Modifiche allo schema sempre tramite migrazione Alembic, mai `create_all` in produzione.
