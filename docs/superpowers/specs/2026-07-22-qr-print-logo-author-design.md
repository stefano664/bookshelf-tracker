# Logo e autore nell'immagine stampabile del QR

## Contesto

L'app bookshelf-tracker genera, per ogni libro, un'immagine PNG stampabile (funzione `downloadQr()` in [templates/index.html](../../../templates/index.html)) contenente QR code, titolo e codice del libro. Prima del download, l'utente vede un'anteprima nella modale (`#qrModal`).

Vogliamo arricchire sia il PNG stampabile sia la modale di anteprima con:
1. Un **logo** configurabile per deployment, sopra il QR code.
2. Il **nome dell'autore** del libro, oltre al titolo già presente.

## Scope

- Modifica sia il PNG scaricabile (`downloadQr()`) sia la modale di anteprima (`openQrModal()` / markup `#qrModal`).
- Non tocca il piccolo QR box (72×72px) mostrato nella card di ogni libro nella griglia principale — troppo piccolo per ospitare logo/autore leggibili.
- Il logo è opzionale per deployment: se non configurato, tutto funziona come oggi (nessuno spazio vuoto residuo).

## Backend

- Nuova variabile d'ambiente **`LOGO_PATH`** (stesso pattern di `DB_PATH` in [app.py](../../../app.py)): percorso a un file immagine sul filesystem del container/server. Non impostata di default.
- Nuova route **`GET /logo`**:
  - Se `LOGO_PATH` è impostata e il file esiste, la route lo serve con `send_file`, mimetype dedotto dall'estensione.
  - Altrimenti risponde **404**.
- `docker-compose.yml`: aggiungere un esempio commentato che mostra come impostare `LOGO_PATH` insieme a un volume mount per il file del logo, per rendere la funzione scopribile senza attivarla di default.

## Frontend

### Caricamento e cache del logo

Al caricamento della pagina, si tenta una sola volta `new Image(); img.src = '/logo'`, esposta come Promise condivisa `logoReady` che risolve con l'`HTMLImageElement` se il caricamento ha successo, o `null` se fallisce (404, errore di rete, file non decodificabile). Sia `openQrModal()` sia `downloadQr()` attendono questa Promise (già risolta dopo il primo tentativo, quindi istantanea nelle chiamate successive) prima di disegnare/renderizzare, evitando race condition se l'utente interagisce subito dopo il caricamento della pagina.

### Layout — opzione scelta: "logo banner in alto"

Ordine (sia nel PNG che nella modale): **logo → QR → titolo → autore → codice libro**.

**PNG stampabile** (canvas 800×980, invariato nelle dimensioni complessive):
- Banner logo: riquadro max 500×140px, centrato orizzontalmente, margine superiore ~40px. L'immagine sorgente viene scalata mantenendo le proporzioni e centrata nel riquadro (letterboxing se le proporzioni non corrispondono a 500:140).
- QR code: ridotto da 600×600 a **520×520** per fare spazio al banner, centrato.
- Titolo: font invariato, ma limitato a **2 righe** (era 3) per lasciare spazio alla riga autore.
- Autore: nuova riga sotto il titolo, font più piccolo e colore più tenue (stile secondario, coerente con `.author` nella UI), una sola riga (troncata se troppo lunga).
- Codice libro (call number): invariato, sotto l'autore.
- Se il logo non è disponibile (`logoReady` risolve `null`): il banner viene omesso e il QR torna a partire dal margine superiore originale (nessuno spazio vuoto lasciato).

**Modale di anteprima** (`#qrModal`): stesso ordine logico — il logo viene inserito sopra il titolo esistente (`#qrModalTitle`), e viene aggiunta una riga autore tra il codice libro (`#qrModalId`) e il box QR (`#qrModalBox`). Se il logo manca, l'elemento immagine non viene renderizzato (nessuno spazio vuoto).

## Gestione errori

- Logo assente, path non configurato, file non esistente/non leggibile, formato non decodificabile dal browser → fallback silenzioso al layout senza logo. Nessun errore mostrato all'utente, nessun log lato server oltre al normale 404.
- Titolo o autore troppo lunghi → troncamento/wrap coerente con la logica già esistente (`wrapText`), adattata al numero di righe disponibili.

## Testing

Verifica manuale in locale (avvio Flask + Playwright in emulazione mobile, come nelle sessioni precedenti):
1. Senza `LOGO_PATH` impostata: comportamento identico a oggi (nessuna regressione visiva), sia in modale che nel PNG scaricato.
2. Con `LOGO_PATH` impostata su un file immagine di test: logo visibile in cima sia nella modale sia nel PNG scaricato, autore visibile, layout non sovrapposto/tagliato.
3. Verifica che il download PNG (`downloadQr()`) produca un file valido apribile, con il layout atteso.

## Fuori scope

- Nessuna UI di amministrazione per caricare/cambiare il logo: resta una configurazione di deployment (env var + file montato).
- Nessuna modifica al contenuto codificato nel QR (resta il permalink al libro).
- Nessuna modifica al QR box piccolo nella griglia principale.
