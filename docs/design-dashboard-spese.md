# Dashboard Spese & Investimenti — Documento di design

> **Versione:** 1.3 — 11 novembre 2026 (frontend: Svelte + ECharts)
> **Destinatario:** sviluppatore che implementerà il progetto
> **Stato:** tutte le decisioni architetturali sono state prese (sezione 17). Le voci marcate **[DA VERIFICARE]** richiedono un controllo tecnico prima dell'implementazione; il layout dell'Excel e dell'estratto conto Trade Republic è stato analizzato su file reali (sez. 8.1, 8.2); restano aperti I5–I7 (sezione 17).

---

## 1. Contesto

Il committente traccia oggi tutte le proprie spese **a mano in un file Excel**:

- **spese ricorrenti** (affitto, abbonamenti, ecc.);
- **spese straordinarie** (spesa alimentare, cene fuori, ecc.).

Paga quasi tutto con **Google Pay** (carta collegata a un conto bancario); alcune spese, come l'**affitto**, sono pagate con **bonifico**. Ha inoltre **investimenti su Trade Republic**.

**Conti:** **Trade Republic** è sia il conto da cui arriva la maggior parte delle spese sia il conto degli investimenti; alcune spese arrivano da **Intesa Sanpaolo**. Il PC del committente usa **Windows 11**.

## 2. Obiettivo

Un'applicazione personale (mono-utente) che:

1. importi lo storico delle spese dal file Excel esistente;
2. mostri le spese in una **dashboard divisa per categoria**, con andamento nel tempo;
3. permetta di **aggiungere spese direttamente dall'app**;
4. acquisisca **automaticamente** (o quasi) i pagamenti fatti con carta / Google Pay;
5. mostri l'**andamento degli investimenti** Trade Republic nel tempo.

---

## 3. Requisiti funzionali

### 3.1 MVP (fase 1)
- Import dello storico da Excel, con anteprima e report degli errori prima del salvataggio.
- Inserimento manuale di una spesa (data, importo, categoria, descrizione/esercente, ricorrente/straordinaria, note).
- Modifica ed eliminazione di una transazione.
- Gestione categorie (crea, rinomina, archivia, colore).
- Dashboard: totale del mese, confronto con mese precedente e media, ripartizione per categoria, andamento mensile, ricorrenti vs straordinarie.
- Elenco transazioni con filtri (periodo, categoria, tipo, sorgente, testo libero).
- Export dei dati in Excel/CSV (per non perdere mai la possibilità di tornare a un foglio).

### 3.2 Fasi successive
- Import dell'estratto conto della banca (CSV/Excel) con deduplicazione.
- Motore di regole per la categorizzazione automatica.
- Sincronizzazione automatica con la banca via Open Banking (PSD2).
- Sezione investimenti (snapshot del valore del portafoglio, poi eventuale automazione).
- Coda "Da categorizzare" per le transazioni importate senza categoria.
- Nice-to-have: budget per categoria, rilevamento automatico delle ricorrenze, avviso se una spesa ricorrente attesa non è arrivata.

## 4. Requisiti non funzionali

- **Mono-utente**, dati finanziari personali → la privacy è il requisito principale (vedi sez. 13).
- **Costo di esercizio vicino a zero.**
- **Robustezza delle sorgenti:** nessuna integrazione esterna deve poter rompere la dashboard. Se una sorgente smette di funzionare, i dati già acquisiti restano consultabili e l'inserimento manuale continua a funzionare.
- **Gira sul PC personale del committente** (D15): l'app deve avviarsi in modo semplice (un comando o un collegamento) e tollerare di restare spenta per giorni.
- **Interfaccia responsive**: usabile anche da telefono sulla rete Wi-Fi di casa (opzionale, sez. 13), e pronta per un futuro spostamento su un server sempre acceso.
- **Nessun lock-in:** export completo sempre disponibile.

---

## 5. Decisioni prese e motivazioni

| # | Decisione | Motivazione |
|---|-----------|-------------|
| D1 | **[DECISO]** Il progetto parte dalle **spese**; gli investimenti sono una fase successiva. | Le spese sono la parte solida e a più alto valore; gli investimenti dipendono da integrazioni fragili. |
| D2 | **[DECISO]** Ogni transazione ha una categoria e un tipo **ricorrente / straordinaria**. | Esplicitamente richiesto: è la distinzione che il committente usa già nel suo Excel. |
| D3 | **[DECISO]** **Google Pay non viene integrato direttamente.** Le transazioni con carta si leggono **dalla banca**. | Google Pay è solo un wallet: le transazioni vivono presso la banca emittente. Non risulta un'API pubblica di Google per leggere lo storico dei pagamenti personali. |
| D4 | **[DECISO]** **GoCardless Bank Account Data (ex Nordigen) è escluso.** Candidato principale per l'Open Banking: **Enable Banking**. | GoCardless ha chiuso le nuove registrazioni ed è in dismissione. Enable Banking permette di collegare i propri conti reali con accesso gratuito ("Restricted Production", solo per conti collegati da sé). |
| D5 | **[DECISO]** **Trade Republic non ha un'API pubblica ufficiale.** Qualunque automazione usa librerie non ufficiali (es. `pytr`) ed è considerata **opzionale e fragile**. | Le librerie usano l'API privata dell'app; possono rompersi quando Trade Republic cambia qualcosa, anche in modo silenzioso (perdita di eventi senza errori). |
| D6 | **[DECISO]** Architettura a **sorgenti multiple → database unico**. Ogni sorgente è un adapter indipendente. | Permette di aggiungere/rimuovere sorgenti senza toccare dashboard e modello dati; isola i guasti. |
| D7 | **[DECISO]** **Deduplicazione** obbligatoria in ingresso. | Le stesse spese possono arrivare da più sorgenti (Excel storico, estratto conto, sync banca, inserimento manuale). |
| D8 | **[DECISO]** **Categorizzazione a regole** (con override manuale), non AI in prima battuta. | Deterministica, spiegabile, gratuita, nessun dato inviato a terzi. Le descrizioni bancarie sono grezze (es. "PAGAMENTO POS ESSELUNGA ...") ma molto ripetitive. |
| D9 | **[DECISO]** L'**inserimento manuale** resta sempre disponibile (contanti, bonifici non coperti, correzioni). | Richiesto: l'affitto via bonifico viene inserito a mano (a meno che l'Open Banking non lo acquisisca già in automatico). |
| D10 | **[DECISO]** Un'app **con backend** (non una pagina solo-browser). | Sync bancaria, script per gli investimenti, segreti API e job pianificati richiedono un processo lato server. Questo supera la proposta iniziale "pagina HTML che legge l'Excel", valida solo per un prototipo. |
| D11 | **[DECISO]** I **trasferimenti tra conti propri** (es. versamenti verso Trade Republic, giroconti) **non sono spese**. | Altrimenti gonfierebbero i totali. Vanno marcati `is_transfer = true` ed esclusi dalle statistiche di spesa. |
| D12 | **[DECISO]** (ex DA1) **Il database dell'app è la fonte principale dei dati.** L'Excel serve solo per l'import iniziale e come formato di export. | Necessario per sync, regole e deduplicazione affidabili; l'export Excel evita il lock-in. Il committente smetterà di aggiornare l'Excel a mano. |
| D13 | **[DECISO]** (ex DA2) **Spese con carta: import dell'estratto conto CSV nell'MVP esteso (fase 2), Open Banking via Enable Banking in fase 3.** Notifiche Android escluse. | Il CSV funziona con qualsiasi banca e resta come piano B permanente; l'Open Banking arriva dopo, se la banca è coperta. |
| D14 | **[DECISO]** (ex DA3) **Investimenti: snapshot manuali.** Il job `pytr` non è in scope; resta un'estensione futura possibile. | Nessuna dipendenza fragile, nessuna credenziale affidata a script, nessuna disconnessione dell'app sul telefono. |
| D15 | **[DECISO]** (ex DA4) **L'app gira solo sul PC personale del committente.** | Costo zero, dati che non escono dal computer. Conseguenze in sez. 6.2, 8.3 e 13. |
| D16 | **[DECISO]** **Sorgenti bancarie: Trade Republic (principale) e Intesa Sanpaolo (secondaria).** Per Trade Republic si importano file esportati dall'app (D18); l'Open Banking in fase 3 riguarda con certezza solo Intesa. | Trade Republic ha introdotto nell'app un export CSV delle transazioni (aprile 2026). Intesa è supportata da Enable Banking; Trade Republic non compare nella pagina di Enable Banking dedicata all'Italia. |
| D17 | **[DECISO]** **Le operazioni di investimento su Trade Republic (acquisti, vendite, piani di accumulo) non sono spese.** | Stanno nello stesso conto delle spese: se non escluse, gonfierebbero i totali. Vanno marcate come movimenti di investimento ed escluse dalle statistiche di spesa. |
| D18 | **[DECISO]** **Trade Republic: due formati di import, PDF estratto conto (subito) ed export CSV dall'app (appena disponibile un file d'esempio).** | Scelta del committente. Il PDF è già disponibile, copre un periodo a scelta e contiene il saldo progressivo per ogni riga, che permette di validare il parsing. Il CSV è più semplice da leggere. Entrambi alimentano lo stesso conto: la deduplicazione per copertura del periodo (sez. 9) evita doppioni tra i due formati. |
| D19 | **[DECISO]** **Data di taglio tra Excel e banca, attorno ad agosto 2026** ([DA CONFERMARE] I7: banca dal 1° agosto o dal 1° settembre). Prima della data fa fede l'Excel, dopo fa fede l'estratto conto. L'inserimento manuale resta sempre possibile anche dopo la data (contanti, altre carte). | Scelta del committente. Excel (solo mese, voci raggruppate) e banca (giorno, esercente) non si possono abbinare automaticamente: un taglio netto evita doppioni e conserva le categorie già assegnate a mano. |

---

## 6. Architettura

```
                ┌──────────────────────── SORGENTI (adapter) ────────────────────────┐
                │                                                                    │
  Excel storico ─┤  ExcelImporter        (una tantum + reimport)                     │
 Estratto conto ─┤  BankCsvImporter      (profilo di parsing per banca)              │
   Open Banking ─┤  EnableBankingSync    (all'avvio + giornaliero)       [fase 3]    │
  Form manuale ─┤  ManualEntry          (API REST)                                  │
Trade Republic ─┤  InvestmentSnapshots  (form manuale)                  [fase 4]    │
                └──────────────────────────────┬─────────────────────────────────────┘
                                               ▼
                      ┌────────── PIPELINE DI INGESTIONE ──────────┐
                      │ 1. normalizzazione (date, importi, testo)  │
                      │ 2. deduplicazione                          │
                      │ 3. categorizzazione (motore regole)        │
                      │ 4. salvataggio + import_batch log          │
                      └──────────────────────┬─────────────────────┘
                                             ▼
                                  ┌────────────────────┐
                                  │   DATABASE UNICO   │
                                  └─────────┬──────────┘
                                            ▼
                                  ┌────────────────────┐        ┌──────────────┐
                                  │   API REST (JSON)  │◄──────►│  Frontend    │
                                  └────────────────────┘        │  dashboard + │
                                  ┌────────────────────┐        │  form        │
                                  │ Scheduler job      │        └──────────────┘
                                  │ sync, backup       │
                                  └────────────────────┘
```

**Principi:**
- Gli adapter producono un formato intermedio comune (`RawTransaction`) e non scrivono mai direttamente sul DB: tutto passa dalla pipeline.
- La dashboard legge **solo** dal database, mai dalle sorgenti esterne.
- Ogni import crea un record `import_batch`, così ogni transazione è tracciabile e un import sbagliato si può annullare in blocco.

### 6.1 Stack proposto

Proposta, modificabile dallo sviluppatore con motivazione:

| Livello | Scelta | Perché |
|---------|--------|--------|
| Backend | **Python 3.12+ / FastAPI** | `pytr` è Python; ottime librerie per Excel (`openpyxl`, `pandas`); FastAPI è leggero e documenta l'API da solo. |
| DB | **SQLite** (via SQLAlchemy + Alembic per le migrazioni) | Mono-utente, zero manutenzione, backup = copia di un file. Migrabile a PostgreSQL se servisse. |
| Frontend | **[DECISO 11/11/2026] SPA Svelte 5 + Vite, grafici ECharts** | Dashboard interattiva e form utilizzabile da mobile; Svelte scelto per il poco boilerplate in un'app personale. |
| Job | APScheduler (in-process) | Sync banca e backup all'avvio e poi periodici finché l'app è aperta (sez. 6.2). |
| Config | file `.env` (segreti) + `config.yaml` (mapping colonne, profili banca) | Separazione segreti / configurazione. |

### 6.2 Deployment (D15: solo PC personale)

- L'app gira **in locale** sul PC del committente. Il backend serve sia l'API sia il frontend compilato, così basta **un solo processo** da avviare.
- Avvio semplice: uno script (`start.bat` / `start.sh`) o un collegamento sul desktop che avvia il server e apre il browser su `http://localhost:<porta>`. Opzionale: avvio automatico all'accensione del PC.
- Il database (`data/spese.sqlite`), i backup (`data/backups/`) e il file `.env` stanno in una cartella dati unica, fuori dal codice.
- **Nessun job "sempre acceso"**: le attività pianificate (sync bancaria in fase 3, backup) vengono eseguite **all'avvio dell'app** se sono scadute, e poi periodicamente finché resta aperta.
- **Limitazioni accettate:** niente accesso dal telefono fuori casa; nessuna sync mentre il PC è spento (i dati arrivano alla riaccensione).
- **Portabilità:** nessuna scelta deve legare l'app al PC (percorsi configurabili, niente dipendenze dal sistema operativo), così in futuro si può spostare su un mini server o un VPS senza riscritture. Fornire possibilmente anche un `Dockerfile`.
- **Sistema operativo: Windows 11.** Avvio tramite `start.bat` (o collegamento sul desktop) che lancia il server e apre il browser. Avvio automatico opzionale tramite Utilità di pianificazione di Windows o cartella Esecuzione automatica.
- Usare `pathlib` per tutti i percorsi, encoding `utf-8` esplicito in lettura/scrittura file, nessun comando shell specifico di Unix. Il codice deve restare eseguibile anche su Linux (portabilità, futuro server).

---

## 7. Modello dati

Convenzioni:
- **Importi in centesimi interi** (`amount_cents`), mai float. Segno: **negativo = uscita, positivo = entrata**.
- Valuta di default `EUR`, campo `currency` presente comunque.
- Date in ISO 8601; fuso orario di riferimento `Europe/Rome`.

### `accounts`
| Campo | Tipo | Note |
|-------|------|------|
| id | int PK | |
| name | text | es. "Conto principale", "Contanti", "Trade Republic" |
| type | enum | `bank`, `card`, `cash`, `broker` |
| institution | text | nome banca |
| iban_masked | text | solo ultime cifre, mai IBAN completo in chiaro nei log |
| provider_ref | text | id dell'account presso l'aggregatore Open Banking |

### `categories`
| Campo | Tipo | Note |
|-------|------|------|
| id | int PK | |
| name | text unique | |
| parent_id | int FK nullable | sottocategorie (es. Casa → Affitto) |
| default_kind | enum | `recurring` / `extraordinary` — default ereditato dalle transazioni |
| color, icon | text | per la dashboard |
| archived | bool | non si cancella una categoria usata, si archivia |

Categorie iniziali: **da derivare dall'Excel del committente** (sez. 8.1). Se mancano, proposta: Casa, Bollette, Abbonamenti, Spesa, Ristoranti, Trasporti, Salute, Svago, Shopping, Viaggi, Regali, Altro.

### `transactions`
| Campo | Tipo | Note |
|-------|------|------|
| id | int PK | |
| account_id | FK | |
| booking_date | date | data dell'operazione |
| date_precision | enum | `day` (default) / `month` (storico Excel senza giorno) |
| raw_type | text nullable | tipo di movimento originale della sorgente (es. "Transazione con carta", "Commercio"): base della classificazione e del rilevamento di tipi sconosciuti |
| balance_after_cents | int nullable | saldo dopo il movimento, quando la sorgente lo fornisce (PDF Trade Republic): usato per la validazione |
| value_date | date nullable | |
| amount_cents | int | negativo = uscita |
| currency | text | default EUR |
| description_raw | text | testo originale della sorgente, mai modificato |
| merchant | text nullable | esercente normalizzato (es. "Esselunga") |
| category_id | FK nullable | null = "Da categorizzare" |
| kind | enum nullable | `recurring` / `extraordinary`; null = eredita dalla categoria |
| is_transfer | bool | giroconti / versamenti a broker: esclusi dalle statistiche di spesa |
| status | enum | `booked` / `pending` |
| source | enum | `excel_import`, `bank_pdf`, `bank_csv`, `open_banking`, `manual` |
| external_id | text nullable | id fornito dalla sorgente |
| dedup_hash | text | vedi sez. 9 |
| category_locked | bool | true se l'utente ha scelto a mano la categoria: le regole non la sovrascrivono |
| notes | text | |
| import_batch_id | FK nullable | |
| created_at, updated_at | timestamp | |

Vincoli: `UNIQUE(source, external_id)` quando `external_id` non è null; indice su `booking_date`, `category_id`, `dedup_hash`.

### `categorization_rules`
| Campo | Tipo | Note |
|-------|------|------|
| id | int PK | |
| priority | int | ordine di valutazione (la prima che matcha vince) |
| field | enum | `merchant`, `description_raw` |
| match_type | enum | `contains`, `equals`, `regex` (case-insensitive) |
| pattern | text | |
| amount_min_cents, amount_max_cents | int nullable | per distinguere es. lo stesso esercente con importi diversi |
| account_id | FK nullable | regola valida solo per un conto |
| set_category_id | FK | |
| set_kind | enum nullable | |
| set_is_transfer | bool nullable | |
| set_merchant | text nullable | normalizzazione del nome esercente |
| enabled | bool | |

### `import_batches`
`id, source, account_id, filename, file_sha256, period_start, period_end, started_at, finished_at, rows_read, rows_imported, rows_duplicate, rows_skipped, rows_error, error_log (json)`.
`period_start/period_end` indicano i giorni coperti da un estratto conto (dal PDF o dal minimo/massimo delle date del CSV): servono alla deduplicazione per copertura (sez. 9). `file_sha256` rileva il reimport dello stesso file.
Deve essere possibile **annullare un batch** (cancella le transazioni create da quel batch).

### `bank_connections` (fase 3)
`id, provider ("enable_banking"), aspsp_name, session_id, account_uid, consent_valid_until, last_sync_at, last_sync_cursor, last_error`.

### `investment_snapshots` (fase 4)
| Campo | Tipo | Note |
|-------|------|------|
| id | int PK | |
| account_id | FK | conto broker |
| snapshot_date | date | `UNIQUE(account_id, snapshot_date)` |
| market_value_cents | int | valore di mercato del portafoglio |
| invested_cents | int | capitale netto versato cumulato (versamenti − prelievi) |
| cash_cents | int nullable | liquidità sul conto broker |
| source | enum | `manual`, `pytr` |
| notes | text | |

### `investment_transactions` (fase 4, opzionale)
`id, account_id, date, type (buy/sell/dividend/interest/deposit/withdrawal/fee/savings_plan), isin, instrument_name, quantity, amount_cents, external_id, raw_type`.
`raw_type` conserva il tipo di evento originale: serve a rilevare tipi sconosciuti (vedi sez. 8.6).

---

## 8. Sorgenti dati: dettaglio

### 8.1 Excel storico — [DECISO], fase 1

**Layout reale (analizzato sul file del committente il 10/11/2026):**
- **Un solo foglio**, con i **12 mesi affiancati orizzontalmente**: un blocco di **10 colonne per mese** (8 di dati + 2 di spazio/totale), il primo blocco parte dalla colonna A (Gennaio = A, Febbraio = K, Marzo = U, …, Dicembre = DG).
- **Riga 1:** nome del mese in italiano, senza anno (celle unite sulle 8 colonne di dati).
- **Riga 2:** intestazioni delle 4 sezioni, ciascuna su 2 colonne unite: **Spesa**, **Affitto**, **Abbonamenti**, **Varie**.
- **Riga 3:** sotto ogni sezione, le colonne **Importo** e **Motivo**.
- **Righe 4–13:** le voci (10 righe disponibili per sezione). Importi positivi, numerici (interi o decimali) con formato valuta €; il "Motivo" è un testo breve.
- **Riga 14:** totale per sezione (`=SUM(...)` sulle righe dati) e, nella 9ª colonna del blocco, totale del mese (etichetta "Totale" nella riga 13).
- **Righe 19–20:** "Totale annuale" (somma dei 12 totali mensili).
- L'**anno non è scritto** nel file.

**Casi particolari trovati:**
- Alcune sezioni sono **piene fino all'ultima riga disponibile**: il parser non deve dare per scontato che restino righe libere, e deve trovare la riga dei totali cercando le formule `SUM`, non contando le righe.
- Alcune voci hanno un **importo senza motivo**: si importano con descrizione vuota e un avviso nel dry run.
- Alcuni motivi hanno **spazi finali**: `description_raw` resta com'è, il confronto con le regole usa il testo normalizzato (trim, minuscole).
- I **mesi futuri possono essere già precompilati** (es. affitto e abbonamenti inseriti in anticipo): le voci di mesi successivi alla data di taglio (D19) o futuri non si importano automaticamente.
- La sezione **"Spesa" contiene cibo in generale**, inclusi pasti fuori; anche "Varie" contiene voci di cibo, oltre a molto altro. Le stesse descrizioni possono comparire in sezioni diverse.

**Comportamento dell'importer:**
- Parser a **blocchi orizzontali**. In `config.yaml`: colonna di partenza, larghezza del blocco (10), riga del mese (1), riga delle sezioni (2), riga delle intestazioni (3), prima riga dati (4), nomi delle sezioni e loro mapping. Il parser **verifica** che le intestazioni trovate corrispondano alla configurazione e si ferma con un errore chiaro se il layout è cambiato.
- **Anno:** chiesto nella schermata di import (default: anno di creazione del file letto dalle proprietà del documento, altrimenti anno corrente). Ogni anno sarà presumibilmente un file separato con lo stesso layout.
- **Date:** `booking_date` = primo giorno del mese, `date_precision = 'month'`. Le statistiche mensili restano corrette; le viste per giorno mostrano "data non specificata".
- **Segno:** gli importi del file sono positivi ma sono uscite → salvati negativi.
- **Data di taglio (D19):** si importano solo i mesi **prima** della data di taglio. Le voci dei mesi successivi vengono mostrate nell'anteprima come "escluse (coperte dall'estratto conto)"; l'utente può selezionarne singole voci da importare comunque, per esempio spese in contanti che la banca non vede (importate come `source = manual`, conto "Contanti").
- **Controllo dei totali:** per ogni sezione e mese, la somma importata deve coincidere con il totale calcolato dal file (valori in cache delle celle di riga 14). Una differenza blocca il commit e viene mostrata nel dry run.
- **Mapping iniziale delle categorie e del tipo** (modificabile nella schermata di import):

| Sezione Excel | Categoria app | Tipo |
|---|---|---|
| Spesa | Cibo | straordinaria |
| Affitto | Affitto (sotto Casa) | ricorrente |
| Abbonamenti | Abbonamenti | ricorrente |
| Varie | Varie | straordinaria |

  Dopo l'import l'utente può ricategorizzare le voci di "Varie" (es. pasti fuori, trasporti, salute) e creare regole basate sul motivo; le regole si applicano anche allo storico importato, con anteprima.
- **Dry run obbligatorio**: anteprima + report (voci lette, importate, escluse per data di taglio, avvisi) prima del commit.

### 8.2 Estratti conto banca — fase 2 (D16, D18)

#### 8.2.1 Trade Republic — PDF estratto conto (primo da implementare)

**Layout reale (analizzato su un estratto del committente il 10/11/2026):**
- PDF generato dall'app, A4, più pagine. Si genera per un **periodo a scelta** (intestazione "DATA gg mmm aaaa - gg mmm aaaa").
- **Riepilogo** iniziale: prodotto "Conto corrente" con **saldo iniziale, totale in entrata, totale in uscita, saldo finale**.
- **Tabella "TRANSAZIONI SUL CONTO"** con colonne **DATA, TIPO, DESCRIZIONE, IN ENTRATA, IN USCITA, SALDO**. L'intestazione della tabella si ripete a ogni pagina; ogni pagina ha un piè di pagina con dati legali e "Pagina X da Y".
- Ogni movimento occupa **più righe di testo**: la data è spezzata (giorno + mese abbreviato in italiano, es. "06 ott", sopra; anno sotto), il tipo può essere spezzato (es. "Transazione" / "con carta"), la descrizione può andare a capo su 2 righe.
- Importi in formato italiano con simbolo (`1.234,56 €`), in una sola delle due colonne entrata/uscita; il **saldo progressivo** è sempre presente.
- In fondo: "PANORAMICA DEL SALDO" (liquidità ed eventuali fondi monetari) e note legali, da ignorare. **Il valore dei titoli non è riportato**, quindi gli snapshot degli investimenti restano manuali (D14).

**Tipi di movimento osservati e classificazione (D17):**

| TIPO nel PDF | Esempi di descrizione | Classificazione |
|---|---|---|
| Transazione con carta | nome esercente (anche pagamenti Google Pay) | spesa; categoria dalle regole sull'esercente |
| Commercio | "Buy trade <ISIN> <strumento>, quantity: …", "Savings plan execution <ISIN> …" (presumibilmente anche "Sell trade") | investimento: `is_transfer = true`, categoria di sistema "Investimenti"; ISIN e quantità estratti in `notes`/metadati per la fase 4 |
| Bonifico | "Incoming transfer from <nome> (<IBAN>)", "Outgoing transfer for <nome> (<IBAN>)" | in entrata → entrata; in uscita → spesa. Se il nome coincide con l'intestatario → giroconto, `is_transfer = true`. Regole per beneficiario (es. il padrone di casa → Affitto) |
| Interessi | "Interest payment" | entrata (categoria "Interessi") |
| Premio | "Saveback cash reward" | entrata (categoria "Premi e cashback") |
| Imposte | "Stamp Duty Tax (Portfolio)" | spesa, categoria "Imposte e costi investimento" (modificabile) |
| altro / sconosciuto | — | importato come "Da categorizzare" con avviso; **mai scartato in silenzio** |

**Implementazione del parser:**
- Usare **`pdfplumber`** (estrazione di parole con coordinate) e assegnare i valori alle colonne in base alla **posizione orizzontale** delle intestazioni della tabella, rilevata per ogni pagina. Non basarsi su `pdftotext -layout` o sulla posizione dei caratteri nel testo.
- Ricostruire ogni movimento raggruppando le righe tra due date; la data è valida quando giorno + mese + anno sono completi (mesi: gen, feb, mar, apr, mag, giu, lug, ago, set, ott, nov, dic).
- Scartare intestazioni ripetute, piè di pagina e sezioni finali.
- **Validazione forte (bloccante nel dry run):**
  1. per ogni riga, `saldo precedente ± importo = saldo riportato`; la prima riga parte dal saldo iniziale del riepilogo;
  2. somma delle entrate e delle uscite = totali del riepilogo;
  3. ultimo saldo = saldo finale.
  Se un controllo fallisce, l'import non si salva e il report indica la riga problematica. Così un cambio di layout del PDF non può produrre dati sbagliati in silenzio.
- Il segno dell'importo si ricava dalla colonna e si conferma con la variazione del saldo.
- `booking_date` dalla colonna DATA, `date_precision = 'day'`, `raw_type` = TIPO, `description_raw` = descrizione completa su una riga, `balance_after_cents` = SALDO.
- `period_start/period_end` del batch = periodo nell'intestazione del PDF.
- **Dati personali:** il PDF contiene nome, indirizzo e IBAN dell'intestatario e IBAN di terzi nei bonifici. Il parser non salva l'intestazione; gli IBAN nelle descrizioni restano in `description_raw` (dato locale) ma non vanno mai nei log. I nomi dell'intestatario per riconoscere i giroconti stanno in `.env` (`ACCOUNT_HOLDER_NAMES`), non nel codice né in `config.yaml`.

#### 8.2.2 Trade Republic — export CSV dall'app
- Disponibile nell'app da aprile 2026. [DA VERIFICARE] (I5) colonne, tipi di movimento e presenza del saldo su un file d'esempio.
- Stessa classificazione della tabella sopra, mappando i tipi del CSV su quelli del PDF tramite `config.yaml`.
- Alimenta lo stesso conto del PDF: i doppioni tra i due formati si evitano con la deduplicazione per copertura (sez. 9).

#### 8.2.3 Intesa Sanpaolo
- Export movimenti dall'home banking. [DA VERIFICARE] (I5) formato (CSV o Excel) su un file d'esempio. Il profilo di parsing va in `config.yaml` (separatore, encoding, colonne, formato data, segno).

#### Regole comuni
- Descrizione grezza salvata in `description_raw`; merchant estratto tramite regole.
- Si importano solo i movimenti **dalla data di taglio in poi** (D19); quelli precedenti sono mostrati come esclusi nel dry run.
- Reimportare lo stesso file, o un estratto che si sovrappone a uno già importato, non deve creare doppioni (sez. 9).
- Anche con l'Open Banking attivo, l'import da file resta come **piano B** e per lo storico oltre il limite temporale dell'API.

### 8.3 Open Banking via Enable Banking — [DECISO] fase 3 (D13)
Flusso (dalla documentazione pubblica di Enable Banking):
1. Registrazione dell'applicazione sul portale Enable Banking; l'autenticazione verso la loro API usa un **JWT** firmato con la chiave dell'applicazione.
2. `POST /auth` con banca (`aspsp`), permessi (`balances`, `transactions`), scadenza del consenso (`valid_until`), `psu_type: personal` e `redirect_url`.
3. L'utente si autentica presso la propria banca (SCA) e viene rediretto con un `code`.
4. `POST /sessions` con il `code` → ottiene `session_id` e l'elenco dei conti (`uid`).
5. `GET /accounts/{uid}/transactions` (paginazione con `continuation_key`) e `GET /accounts/{uid}/balances`.

Note implementative:
- Sync **all'avvio dell'app** (recuperando tutti i giorni dall'ultima sync riuscita, usando `last_sync_at` con qualche giorno di margine), poi una volta al giorno se l'app resta aperta, più un pulsante "Sincronizza ora". Necessario perché l'app gira sul PC personale (D15).
- [DA VERIFICARE] Quanti giorni di storico restituisce la banca via API: se il PC resta spento a lungo, la sync deve comunque coprire il buco; in caso contrario, l'import CSV copre il periodo mancante.
- Importare le transazioni `BOOK` come `booked`. Le `PDNG` (pending), se si importano, vanno aggiornate o sostituite quando diventano definitive.
- Usare `entry_reference` / id transazione come `external_id` quando disponibile.
- Il **consenso scade** e va rinnovato con una nuova autenticazione bancaria. L'app deve mostrare un avviso prima della scadenza (`consent_valid_until`). [DA VERIFICARE] la durata massima per la banca del committente.
- **Intesa Sanpaolo: supportata** da Enable Banking, con flusso redirect e SCA nell'app Intesa Sanpaolo Mobile. Note dalla documentazione Enable Banking per l'Italia: molte banche italiane permettono **un solo consenso attivo per fornitore e utente** (un nuovo consenso invalida il precedente); le banche su CBI Globe, tra cui Intesa, richiedono una **SCA aggiuntiva per lo storico oltre 90 giorni**.
- **Trade Republic: copertura non confermata.** Non compare nella pagina di Enable Banking dedicata all'Italia. [DA VERIFICARE] nell'elenco completo delle banche di Enable Banking. Se non è coperta, per Trade Republic resta l'import da file (PDF o CSV, sez. 8.2), che è comunque la sorgente principale.
- [DA VERIFICARE] Il `redirect_url` per un'app personale: verificare se è accettato `localhost` o se serve un dominio raggiungibile.
- Con l'Open Banking arrivano automaticamente anche i **bonifici** (affitto) dei conti coperti: l'inserimento manuale si riduce a contanti ed eccezioni.
- Segreti (chiave privata, id applicazione) solo in `.env` / file chiave fuori dal repository.

### 8.4 Notifiche Android → webhook — ESCLUSO (D13)

> Non va implementato. Descrizione conservata solo come riferimento per eventuali sviluppi futuri; richiederebbe comunque un server sempre acceso, incompatibile con D15.
- Un'app di automazione (Tasker, MacroDroid o simili) legge la notifica di Google Wallet dopo il pagamento (importo, esercente) e fa `POST /api/webhooks/notification` con un **token segreto**.
- Le transazioni da notifica nascono come `status = pending, source = notification` e vanno **riconciliate** con la transazione bancaria definitiva quando arriva (sez. 9), per non contarle due volte.
- Fragile: dipende dal formato della notifica e dal telefono acceso e connesso. Funziona solo su Android.

### 8.5 Inserimento manuale — [DECISO], fase 1
- Form rapido ottimizzato per mobile: importo (tastiera numerica), categoria (ultime usate in cima), data (default oggi), descrizione, ricorrente/straordinaria (default dalla categoria), conto (default "Contanti" o ultimo usato).
- Disponibile per **qualsiasi data, anche dopo la data di taglio** (D19): serve per contanti e per carte o conti che non vengono importati. Conti predefiniti: "Contanti", "Altra carta".
- Se si inserisce a mano una spesa su un conto che viene importato (es. Trade Republic), la deduplicazione la proporrà come possibile doppione quando arriva l'estratto (sez. 9).
- Obiettivo: inserire una spesa in meno di 10 secondi.

### 8.6 Investimenti Trade Republic — fase 4 (D14)
**[DECISO] Snapshot manuale.** Form per inserire, a data X, valore del portafoglio e capitale versato. La dashboard mostra valore nel tempo, capitale versato e guadagno/perdita assoluto e percentuale.
- Promemoria nella dashboard se l'ultimo snapshot è più vecchio di 31 giorni.
- Il form propone in automatico il capitale investito: quello dello snapshot precedente + gli acquisti netti (acquisti e piani di accumulo − vendite) importati dagli estratti Trade Republic nel frattempo (D17), così l'utente deve inserire solo il valore di mercato. Il valore dei titoli non è negli estratti, quindi va inserito a mano.
- **Evoluzione futura possibile (fuori scope ora):** i movimenti "Commercio" degli estratti contengono ISIN e quantità, quindi in futuro si potrebbe popolare `investment_transactions` da lì, senza `pytr`.

**Fuori scope — estensione futura possibile: job con `pytr`.** Da non implementare ora; il modello dati (`investment_transactions`, `source = pytr`) la lascia possibile.
- `pytr` (progetto community `pytr-org/pytr`, installabile con pipx) offre comandi come `portfolio` ed `export_transactions`.
- Il job gira **separato** dall'app: legge da Trade Republic e scrive snapshot/transazioni nel DB tramite la pipeline. Se si rompe, la dashboard continua a funzionare con i dati già presenti.
- **Avvertenze da comunicare al committente:**
  - Il login di `pytr` esegue un "device reset" che **disconnette l'app di Trade Republic sul telefono**.
  - Richiede numero di telefono e PIN, da conservare solo in locale (`~/.pytr/credentials` o `.env`), mai nel repository né nei log.
  - Uso di un'API privata non autorizzata ufficialmente: verificare i termini di servizio.
  - Rischio di **perdita silenziosa di dati** se Trade Republic rinomina i tipi di evento: il job deve contare gli eventi con `raw_type` sconosciuto e **segnalare un avviso** nella dashboard invece di scartarli in silenzio.
- **Storico:** con i soli snapshot l'andamento parte da quando si inizia a registrarli. Lo storico passato si ricostruisce solo dalle transazioni (export o `pytr`).
- Le operazioni di investimento e i bonifici tra conti propri sono `is_transfer = true` lato spese (D11, D17).

---

## 9. Deduplicazione e riconciliazione

In ordine di applicazione:
1. **Match esatto su `(source, external_id)`** → la transazione esiste già: si aggiorna (es. da pending a booked) o si ignora.
2. **`dedup_hash`** = hash di `(account_id, booking_date, amount_cents, description_raw normalizzata)` → duplicato certo all'interno della stessa sorgente (es. stesso CSV reimportato).
3. **Match approssimato tra sorgenti diverse** (es. spesa inserita a mano o da notifica vs. transazione bancaria): stesso importo, data ±3 giorni, stesso conto → **non si fonde in automatico**. Si propone all'utente come "possibile duplicato" con le azioni *unisci* / *sono diverse*. Unendo, si tiene la transazione bancaria e si conservano categoria e note scelte a mano.
4. **Excel vs banca:** nessun abbinamento automatico. Vale la **data di taglio** (D19): Excel solo prima, estratti conto solo dopo.
5. **Estratti conto sovrapposti dello stesso conto** (stesso PDF reimportato, due PDF con periodi sovrapposti, PDF e CSV dello stesso periodo): il PDF non fornisce un id per movimento e le descrizioni possono differire tra PDF e CSV, quindi si usa la **copertura del periodo**:
   - lo stesso file (`file_sha256` uguale) viene rifiutato subito;
   - per i giorni del nuovo file già coperti da un batch precedente dello stesso conto (`period_start`–`period_end`), i movimenti si confrontano per **(data, importo)** come multinsieme: quelli che trovano corrispondenza sono doppioni e si saltano; quelli senza corrispondenza vengono mostrati nel dry run per conferma;
   - i giorni non ancora coperti si importano normalmente.

## 10. Categorizzazione

- Alla creazione di ogni transazione non manuale si valutano le regole in ordine di `priority`; la prima che corrisponde imposta categoria, tipo, merchant, `is_transfer`.
- Nessuna regola → `category_id = null` → la transazione finisce nella coda **"Da categorizzare"** (con badge con il conteggio nella dashboard).
- Quando l'utente assegna una categoria a mano: `category_locked = true` e l'app propone **"Applicare sempre a «ESSELUNGA»?"** → crea la regola in un clic.
- "Riapplica regole allo storico" con **anteprima** delle modifiche; non tocca le transazioni `category_locked`.
- **Ricorrente/straordinaria:** default dalla categoria (`default_kind`), con override per singola transazione.
- Fase 5: rilevamento delle ricorrenze (stesso merchant, importo simile, cadenza mensile) proposto come suggerimento, mai applicato in automatico.

## 11. Dashboard e interfaccia

**Viste principali:**
1. **Panoramica (mese corrente, selettore periodo)**
   - Totale spese del mese; differenza rispetto al mese precedente e alla media degli ultimi 12 mesi.
   - Ripartizione per categoria (barre orizzontali o ciambella), cliccabile → elenco filtrato.
   - Ricorrenti vs straordinarie (totali e percentuale).
   - Andamento mensile (barre impilate per categoria, ultimi 12 mesi).
   - Badge "Da categorizzare" e "Possibili duplicati"; avvisi (consenso bancario in scadenza, sync fallita, eventi Trade Republic sconosciuti).
2. **Transazioni**: tabella con filtri (periodo, categoria, tipo, conto, sorgente, testo), modifica inline della categoria, azioni in blocco.
3. **Aggiungi spesa**: form rapido (sez. 8.5), raggiungibile con un pulsante sempre visibile su mobile.
4. **Categorie e regole**: gestione e test di una regola su testo di esempio.
5. **Import**: upload Excel/CSV, anteprima, storico dei batch con annullamento.
6. **Investimenti** (fase 4): valore del portafoglio nel tempo vs capitale versato, guadagno assoluto e %, ultimo aggiornamento e sorgente.
7. **Impostazioni**: conti, connessioni bancarie, export, backup.

Le statistiche di spesa escludono sempre `is_transfer = true` e, per default, le entrate.

## 12. API REST (bozza)

```
GET    /api/transactions?from=&to=&category=&kind=&account=&source=&q=&uncategorized=
POST   /api/transactions
PATCH  /api/transactions/{id}
DELETE /api/transactions/{id}
GET    /api/transactions/duplicates          # possibili duplicati da confermare
POST   /api/transactions/duplicates/{id}/resolve

GET|POST|PATCH /api/categories
GET|POST|PATCH|DELETE /api/rules
POST   /api/rules/apply?dry_run=true

POST   /api/import/excel?dry_run=true        # multipart upload
POST   /api/import/bank-statement?account=&format=pdf|csv&profile=&dry_run=true
GET    /api/import/batches
DELETE /api/import/batches/{id}              # annulla un import

GET    /api/stats/summary?month=YYYY-MM
GET    /api/stats/by-category?from=&to=
GET    /api/stats/trend?from=&to=&granularity=month
GET    /api/stats/kind-split?from=&to=

GET|POST /api/investments/snapshots
GET    /api/investments/performance?from=&to=

POST   /api/sync/bank                        # sync manuale (fase 3)
GET    /api/sync/status

GET    /api/export?format=xlsx|csv&from=&to=
```

## 13. Sicurezza e privacy

- Dati finanziari personali: l'app **non deve mai essere esposta su Internet**.
- **Default: il server ascolta solo su `127.0.0.1`** (accessibile solo dal PC stesso). In questa modalità il login è opzionale.
- **Opzionale: accesso dal telefono sulla Wi-Fi di casa**, attivabile esplicitamente da configurazione (`LISTEN_LAN=true`, bind su `0.0.0.0`). In questo caso il **login diventa obbligatorio**: password con hash (argon2/bcrypt), sessione con cookie `HttpOnly`, rate limiting sul login.
- Se in futuro l'app viene spostata su un server: VPN (es. Tailscale), HTTPS, login obbligatorio.
- Segreti (chiavi Enable Banking, password di login) solo in `.env` o file con permessi ristretti; **mai** nel repository, nei log o nel frontend.
- HTTPS se l'app è raggiungibile fuori dal computer locale.
- Log senza dati sensibili (niente IBAN completi, importi e descrizioni solo a livello debug disattivato in produzione).
- **Backup** automatico del file SQLite all'avvio e una volta al giorno, con rotazione (es. ultimi 30). Poiché tutto vive su un solo PC, il percorso dei backup deve essere configurabile per poterlo puntare a un disco esterno o a una cartella sincronizzata; se esce dalla macchina, preferibilmente cifrato.
- I dati reali non vanno mai usati nei test né committati: usare fixture con dati finti.

## 14. Qualità e test

- Test unitari: parsing di importi e date in formato italiano, profili CSV, motore regole, deduplicazione, calcolo statistiche (inclusa esclusione dei trasferimenti).
- Test di integrazione dell'import Excel e del parser PDF Trade Republic su **file sintetici** che riproducono il layout descritto in sez. 8.1 e 8.2.1, generati da script nei test (es. `openpyxl` per l'Excel, `reportlab` per il PDF) con dati inventati. **I file reali del committente non vanno mai copiati nel repository né usati come fixture.**
- Casi da coprire per il PDF: movimento a cavallo di due pagine, descrizione su due righe, importi con separatore delle migliaia, tipo sconosciuto, saldo che non torna (deve bloccare).
- Per Enable Banking: usare la sandbox per lo sviluppo, poi il conto reale.
- Definizione di "fatto" per l'MVP: storico Excel importato senza perdite (totali per mese identici all'Excel), inserimento manuale da telefono funzionante, dashboard con le viste 1–3, export funzionante, backup attivo.

## 15. Roadmap

| Fase | Contenuto | Dipende da |
|------|-----------|------------|
| 0 | Raccolta info: struttura Excel (I1), banca (I2), sistema operativo del PC (I3). Decisioni D12–D15 ✅ prese | committente |
| 1 — MVP | DB, import Excel, inserimento manuale, categorie, dashboard base, export, backup, script di avvio locale | Fase 0 |
| 2 | Import estratti conto (prima PDF Trade Republic, poi CSV Trade Republic e Intesa), motore regole, coda "Da categorizzare", deduplicazione completa | Fase 1 |
| 3 | Sync automatica Open Banking (Enable Banking), eseguita all'avvio | copertura banca verificata |
| 4 | Investimenti: snapshot manuali con promemoria | Fase 1 |
| 5 | Budget, rilevamento ricorrenze, avvisi spese ricorrenti mancanti | Fasi 2–3 |
| Futuro (fuori scope) | Job `pytr`; spostamento su mini server/VPS con VPN; notifiche Android | — |

## 16. Rischi e mitigazioni

| Rischio | Mitigazione |
|---------|-------------|
| Investimenti non aggiornati (snapshot dimenticati) | Promemoria in dashboard dopo 31 giorni; `pytr` fuori scope evita il rischio di integrazioni fragili |
| La banca non è coperta da Enable Banking o la connessione è instabile | Import CSV come piano B permanente |
| Consenso Open Banking scaduto → buchi nei dati | Avviso anticipato, sync che recupera i giorni mancanti al rinnovo |
| Doppioni tra sorgenti | Data di taglio Excel/banca, deduplicazione per copertura del periodo, fusione tra sorgenti solo con conferma |
| Trade Republic cambia il layout del PDF | Validazione bloccante con saldo progressivo e totali del riepilogo; export CSV come alternativa |
| Categorizzazione errata | Regole con anteprima, `category_locked`, coda "Da categorizzare" |
| Perdita del database | Backup giornaliero con rotazione, export Excel |
| Esposizione dei dati | Bind su localhost di default, login obbligatorio se aperto alla LAN, segreti fuori dal codice |
| Guasto o furto del PC (unica copia dei dati) | Backup verso disco esterno o cartella sincronizzata configurabile |
| PC spento a lungo → buchi nella sync bancaria | Sync di recupero all'avvio; import CSV per i periodi non più disponibili via API |

---

## 17. Decisioni della fase 0 (alternative valutate)

> Tutte le decisioni (DA1–DA6) sono state prese dal committente il 10/11/2026. Le tabelle restano come traccia delle alternative considerate. ✅ = scelta del committente, ⭐ = raccomandazione iniziale.

### DA1 — Dove vivono i dati

| Opzione | Pro | Contro |
|---------|-----|--------|
| **A. Database dell'app come fonte principale, Excel solo per import/export** ⭐ ✅ | Inserimento e sync semplici e affidabili; deduplicazione e regole facili; nessun conflitto di scrittura; si può sempre esportare un Excel | Si smette di aggiornare l'Excel a mano: si usa l'app |
| B. Google Sheets come database | Il foglio resta modificabile a mano da ovunque; l'app legge e scrive sullo stesso foglio | Configurazione OAuth Google; lento e con limiti di quota; dati facili da "rompere" a mano (colonne spostate); dedup e regole più fragili; dati su Google |
| C. Il file Excel resta il master, il backend ci scrive dentro | Nessun cambio di abitudini | Conflitti se il file è aperto in Excel; formattazioni e formule a rischio; impossibile se il backend non gira sul PC dove sta il file; fragile |
| D. Solo pagina web che legge l'Excel (nessun backend) | Velocissima da fare; zero infrastruttura | Incompatibile con sync bancaria, investimenti automatici e job; per aggiungere spese bisogna riscaricare il file |

**Scelta: A** (→ D12). Con sync bancaria e investimenti nel progetto, serve un database vero; l'export garantisce comunque di non perdere l'Excel.

### DA2 — Come acquisire le spese con carta / Google Pay

| Opzione | Pro | Contro |
|---------|-----|--------|
| **A. Import estratto conto CSV subito, Open Banking in un secondo momento** ⭐ ✅ | Funziona con qualsiasi banca; zero dipendenze esterne; fa da piano B permanente | Non automatico (un import ogni tanto, es. mensile) finché non arriva l'Open Banking |
| B. Open Banking (Enable Banking) subito | Completamente automatico; acquisisce anche i bonifici (affitto) | Più complesso (registrazione app, JWT, redirect, consenso da rinnovare); dipende dalla copertura della banca; rallenta l'MVP |
| C. Notifiche Android → webhook | Quasi in tempo reale; indipendente dalla banca | Fragile (formato notifiche, telefono acceso); solo Android; nessun bonifico; serve riconciliazione con la banca |
| D. Solo inserimento manuale | Semplicissimo | Nessuna automazione: è ciò che il committente vuole superare |

**Scelta: A, con B come obiettivo di fase 3** se la banca è coperta (→ D13). C esclusa.

### DA3 — Investimenti Trade Republic

| Opzione | Pro | Contro |
|---------|-----|--------|
| **A. Snapshot manuali mensili, `pytr` come aggiunta opzionale dopo** ⭐ ✅ | Non si rompe mai; nessuna credenziale da affidare a uno script; nessuna disconnessione del telefono | Un minuto di inserimento al mese; l'andamento parte da quando si inizia |
| B. Job `pytr` automatico subito | Automatico; ricostruisce lo storico dalle transazioni | API privata non ufficiale, fragile e con possibili perdite silenziose; disconnette l'app sul telefono al login; credenziali in uno script; possibili problemi con i termini di servizio |
| C. Import manuale di export/documenti di Trade Republic | Dati ufficiali, storico completo | Lavoro manuale e parser da mantenere; il formato dei documenti può cambiare |

**Scelta: A** (→ D14). Il valore principale (vedere l'andamento) si ottiene subito e senza rischi; `pytr` resta fuori scope.

### DA4 — Dove gira l'app

| Opzione | Pro | Contro |
|---------|-----|--------|
| **A. Solo sul PC personale** ✅ | Nessun costo; dati che non escono di casa | Non raggiungibile dal telefono fuori casa; nessuna sync se il PC è spento |
| **B. Mini server sempre acceso in casa (Raspberry Pi, NAS, vecchio PC) + VPN (es. Tailscale)** ⭐ | Sempre acceso per sync e job; raggiungibile dal telefono ovunque; dati in casa; nessuna esposizione pubblica | Serve l'hardware (spesa una tantum) e un minimo di configurazione |
| C. VPS in cloud + VPN | Sempre acceso, affidabile, nessun hardware | Pochi euro al mese; dati finanziari su un server di terzi; va messo in sicurezza |
| D. Piattaforma gestita (PaaS) | Deploy semplicissimo | Esposta su Internet per default; persistenza di SQLite spesso problematica; costi variabili |

**Scelta del committente: A** (→ D15); la raccomandazione iniziale era B. Conseguenze gestite nel design: sync e backup eseguiti all'avvio (sez. 6.2, 8.3), bind su localhost con accesso LAN opzionale (sez. 13), backup su percorso esterno configurabile, codice portabile per un futuro passaggio a B o C.

### Informazioni dal committente
- **I1** ✅ — Excel diviso per mese, con sezioni Spesa, Affitto, Abbonamenti, Varie; ogni voce ha importo e descrizione (sez. 8.1).
- **I2** ✅ — Trade Republic (principale, anche investimenti) e Intesa Sanpaolo (secondaria) (D16).
- **I3** ✅ — Windows 11 (sez. 6.2).

### Dettagli ancora aperti
- **I4** ✅ — Layout dell'Excel analizzato (sez. 8.1).
- **I5** — In parte risolto: layout del **PDF Trade Republic** analizzato (sez. 8.2.1). Mancano file d'esempio dell'**export CSV Trade Republic** e dell'**export Intesa Sanpaolo** (anche solo intestazioni e un paio di righe inventate). Blocca solo quei due profili.
- **I6** — Copertura di Trade Republic su Enable Banking (da verificare prima della fase 3).
- **I7** — Data di taglio esatta (D19): il committente ha indicato "fino ad agosto / da agosto in poi". Da confermare se l'estratto conto fa fede **dal 1° agosto** (Excel gennaio–luglio) o **dal 1° settembre** (Excel gennaio–agosto). È un valore di configurazione, modificabile anche dopo.

### DA5 — Formato di import Trade Republic (deciso il 10/11/2026)

| Opzione | Pro | Contro |
|---|---|---|
| A. PDF estratto conto ⭐ | Già disponibile; periodo a scelta; saldo progressivo per validare ogni riga | Parsing di un PDF più complesso e legato al layout |
| B. Export CSV dall'app | Più semplice da leggere | Formato ancora sconosciuto; saldo non garantito |
| **C. Entrambi** ✅ | Massima flessibilità | Due parser da scrivere e mantenere |

**Scelta: C** (→ D18). Si implementa prima il PDF, poi il CSV quando arriva un file d'esempio.

### DA6 — Sovrapposizione Excel / estratti conto (deciso il 10/11/2026)

| Opzione | Pro | Contro |
|---|---|---|
| **A. Data di taglio** ⭐ ✅ | Nessun doppione; si tengono le categorie già assegnate | I mesi da Excel restano senza giorno |
| B. Banca per tutto il 2026 | Date ed esercenti precisi | Si perdono contanti e altre carte; tutto da ricategorizzare |
| C. Importare entrambi | Nessun dato scartato | Doppioni non abbinabili (l'Excel non ha i giorni) |

**Scelta: A** con data di taglio attorno ad agosto 2026 (→ D19, I7), mantenendo sempre possibile l'inserimento manuale.

---

## 18. Fonti (verificate novembre 2026)

- Enable Banking — Accounts API: https://enablebanking.com/accounts-api e https://enablebanking.com/tilisy-api/
- Open Banking Tracker — Free & Indie Open Banking APIs (stato di GoCardless/Nordigen ed Enable Banking): https://openbankingtracker.com/guides/free-open-banking-apis
- Open Banking Tracker — aggregatori con copertura in Italia: https://openbankingtracker.com/api-aggregators?country=IT
- `pytr` (client non ufficiale Trade Republic): https://github.com/pytr-org/pytr
- `pytrpp2` (export verso Portfolio Performance, controllo tipi di evento non gestiti): https://pypi.org/project/pytrpp2/0.1.4/
- Trade_Republic_Connector (note sui cambiamenti 2026 dell'API privata): https://github.com/cdamken/Trade_Republic_Connector
- Enable Banking — Open Banking Specifics in Italy: https://enablebanking.com/docs/markets/it/
- mobiflip.de — export CSV delle transazioni nell'app Trade Republic (17/04/2026): https://www.mobiflip.de/trade-republic-bekommt-neue-export-funktion-und-outbank-zieht-sofort-nach/
