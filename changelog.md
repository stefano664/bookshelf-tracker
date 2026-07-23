# Changelog

## [0.2.3] — 2026-07-23

### Modificato
- Nel PNG stampabile del QR il logo (se configurato) è stato spostato sotto il QR code, così l'ordine degli elementi (titolo, autore, codice libro, QR, logo) è lo stesso sia nell'anteprima nella modale sia nel PNG scaricato.

## [0.2.2] — 2026-07-22

### Aggiunto
- Nella procedura di prestito, un pulsante rosso "×" accanto a "Conferma" permette di annullare l'operazione senza aggiornare la pagina (BOOK-003).
- Il PNG stampabile del QR (e la relativa anteprima) mostrano ora il nome dell'autore e, se configurato tramite la variabile d'ambiente `LOGO_PATH`, un logo sotto il QR.

### Modificato
- Il container Docker avvia il servizio con Gunicorn invece del server di sviluppo di Flask, rimuovendo il relativo warning ed essendo adatto alla produzione.

### Corretto
- Gunicorn era configurato con un solo worker: una connessione inattiva o lenta poteva bloccare l'intero servizio per fino a 30 secondi (log "WORKER TIMEOUT") prima che il worker venisse riavviato automaticamente. Ora sono configurati 2 worker, così una connessione bloccata non ferma le altre richieste.
- Corretta una race condition nel seeding iniziale del database: con più worker Gunicorn avviati in parallelo, due processi potevano tentare di inserire i libri di esempio contemporaneamente e andare in errore (violazione della chiave primaria). L'inserimento ora usa `INSERT OR IGNORE`.

## [0.2.1] — 2026-07-22

### Aggiunto
- Il nome inserito al momento del prestito viene ricordato sul dispositivo (localStorage) e proposto automaticamente nei prestiti successivi; il campo ha anche `autocomplete="name"` per sfruttare l'autofill nativo del browser.

### Corretto
- Il campo "Nome facoltativo" nella card di prestito era ridotto a un rettangolo strettissimo a causa di una regola CSS troppo generica; ora occupa correttamente lo spazio disponibile (BOOK-001).

## [0.2.0] — 2026-07-03

### Aggiunto
- I QR code nella pagina principale sono cliccabili: si apre una modale con il QR ingrandito, da cui è possibile scaricarlo come PNG ad alta risoluzione in formato stampabile (con titolo e codice del libro).
- Il numero di versione del servizio è visibile nella pagina principale, accanto al titolo.
- Vista "libro in evidenza": scansionando il QR code si apre la pagina principale con il solo libro interessato, evidenziato e pronto per il prestito o la restituzione; gli altri libri sono nascosti. Un pulsante "Mostra tutto lo scaffale" riporta alla vista completa.

### Modificato
- Nel registro attività le colonne "Quando" e "Chi" sono state rinominate in "Data" e "Utente".
- Anche la scansione da foto ("Scansiona QR") porta alla vista "libro in evidenza" quando il libro viene trovato.

## [0.1.1] — 2026-07-03

### Aggiunto
- Icona del servizio (favicon e icona per dispositivi mobili).
- I QR code contengono un permalink al libro invece del solo codice.

## [0.1.0] — 2026-07-03

### Aggiunto
- Prima versione: catalogo libri con QR code, prestito e restituzione, registro attività su database SQLite.
