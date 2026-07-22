# Logo + Autore nel QR stampabile — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere un logo configurabile per deployment (sopra il QR) e il nome dell'autore, sia nel PNG stampabile del QR sia nella modale di anteprima che lo precede.

**Architecture:** Il backend Flask espone il logo tramite una nuova route `GET /logo` che legge il file puntato dalla env var `LOGO_PATH` (analoga a `DB_PATH`). Il frontend (tutto in `templates/index.html`, non ci sono altri file JS) carica il logo una sola volta all'avvio pagina in una Promise condivisa (`logoReady`), e sia la modale di anteprima (`openQrModal`) sia il generatore del PNG (`downloadQr`) la attendono prima di disegnare. Se il logo non è configurato/non si carica, entrambi i punti omettono silenziosamente quella sezione.

**Tech Stack:** Flask 3.0.3 (Python), vanilla JS, `qrcodejs` (CDN) per generare i QR, `<canvas>` per comporre il PNG stampabile. Nessun bundler, nessun framework di test esistente nel progetto.

## Global Constraints

- Spec di riferimento: `docs/superpowers/specs/2026-07-22-qr-print-logo-author-design.md`.
- **Nessun framework di test automatico esiste in questo progetto** (niente pytest, niente test JS) — la verifica di ogni task è **manuale**: avvio del server Flask in locale e controllo via `curl` (per il backend) e Playwright MCP in emulazione mobile (per il frontend), come fatto nelle sessioni precedenti di lavoro su questo repo. Non introdurre pytest o altri framework solo per questo task.
- Interprete Python su questa macchina: usare il percorso completo `C:\Users\stefano.mologni\AppData\Local\Programs\Python\Python313\python.exe` — il comando `python` nudo su questa macchina risolve a un altro interprete (Inkscape) privo di Flask installato.
- `LOGO_PATH` non è impostata di default: comportamento invariato rispetto a oggi se non configurata.
- Ogni modifica visibile all'utente va riportata in `changelog.md` sotto la voce di versione già in cima (`[0.2.2]`, non ancora taggata) — non creare una nuova voce di versione (vedi `CLAUDE.md`).
- Al termine di ogni task: commit con messaggio descrittivo (niente `--no-verify`).

---

### Task 1: Backend — env var `LOGO_PATH` e route `GET /logo`

**Files:**
- Modify: `app.py:1-13` (import e variabili di modulo), aggiungere nuova route dopo `favicon()` (dopo la riga 96 dell'attuale `app.py`)

**Interfaces:**
- Produces: endpoint HTTP `GET /logo` → `200` + body immagine se `LOGO_PATH` è impostata e il file esiste, `404` + `{"error": "not_found"}` altrimenti. Consumato dal frontend nel Task 2.

- [ ] **Step 1: Aggiungere l'import di `send_file` e la variabile `LOGO_PATH`**

In `app.py`, riga 5, sostituire:

```python
from flask import Flask, jsonify, request, g, render_template
```

con:

```python
from flask import Flask, jsonify, request, g, render_template, send_file
```

Riga 8, dopo `BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")`, aggiungere:

```python
LOGO_PATH = os.environ.get("LOGO_PATH", "")
```

- [ ] **Step 2: Aggiungere la route `/logo`**

Subito dopo la funzione `favicon()` (righe 94-96 attuali):

```python
@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")
```

aggiungere:

```python
@app.route("/logo")
def logo():
    if not LOGO_PATH or not os.path.isfile(LOGO_PATH):
        return jsonify({"error": "not_found"}), 404
    return send_file(LOGO_PATH)
```

- [ ] **Step 3: Verifica manuale — senza `LOGO_PATH` (comportamento di default)**

Avviare l'app senza la variabile impostata:

```bash
cd "c:/Users/stefano.mologni/OneDrive - COMELIT GROUP SPA/Documenti/Sviluppo/Git/Personale/bookshelf-tracker"
DB_PATH="$(pwd)/scratch_logo_test.db" "C:\Users\stefano.mologni\AppData\Local\Programs\Python\Python313\python.exe" app.py
```

In un altro terminale:

```bash
curl -i http://127.0.0.1:5000/logo
```

Expected: `HTTP/1.1 404 NOT FOUND` e body `{"error":"not_found"}`.

- [ ] **Step 4: Verifica manuale — con `LOGO_PATH` impostata**

Fermare il processo precedente (`taskkill //F //IM python.exe`), poi riavviare puntando `LOGO_PATH` a un'immagine già presente nel repo (`static/apple-touch-icon.png`, usata solo come file di test):

```bash
LOGO_PATH="$(pwd)/static/apple-touch-icon.png" DB_PATH="$(pwd)/scratch_logo_test.db" "C:\Users\stefano.mologni\AppData\Local\Programs\Python\Python313\python.exe" app.py
```

```bash
curl -i http://127.0.0.1:5000/logo | head -5
```

Expected: `HTTP/1.1 200 OK` e header `Content-Type: image/png`.

Fermare il server (`taskkill //F //IM python.exe`) e rimuovere `scratch_logo_test.db` al termine del task.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "Add /logo route backed by LOGO_PATH env var"
```

---

### Task 2: Frontend — caricamento condiviso del logo e aggiornamento della modale di anteprima

**Files:**
- Modify: `templates/index.html` — CSS (dopo la riga 72, blocco `.qr-large`), markup della modale (righe 139-149), script (dopo la costante `BASE_URL` a riga 152, e la funzione `openQrModal` righe 261-271)

**Interfaces:**
- Consumes: route `GET /logo` (Task 1).
- Produces: Promise globale `logoReady` (risolve con `HTMLImageElement` se il logo è caricabile, `null` altrimenti) — consumata dal Task 3.

- [ ] **Step 1: Aggiungere la regola CSS per il logo nella modale**

Dopo la riga 72 (`.qr-large{...}`), aggiungere:

```css
  .modal-logo{display:block;max-width:70%;max-height:70px;margin:0 auto 8px;}
```

- [ ] **Step 2: Aggiungere l'elemento logo e la riga autore al markup della modale**

Sostituire (righe 139-149):

```html
<div class="modal-overlay" id="qrModal" style="display:none;">
  <div class="modal">
    <h2 id="qrModalTitle"></h2>
    <p class="callno" id="qrModalId"></p>
    <div class="qr-large" id="qrModalBox"></div>
    <div class="panel-actions">
      <button class="ghost" id="qrModalClose">Chiudi</button>
      <button class="primary" id="qrModalDownload">Scarica per la stampa</button>
    </div>
  </div>
</div>
```

con:

```html
<div class="modal-overlay" id="qrModal" style="display:none;">
  <div class="modal">
    <img class="modal-logo" id="qrModalLogo" style="display:none;">
    <h2 id="qrModalTitle"></h2>
    <p class="callno" id="qrModalId"></p>
    <p class="author" id="qrModalAuthor"></p>
    <div class="qr-large" id="qrModalBox"></div>
    <div class="panel-actions">
      <button class="ghost" id="qrModalClose">Chiudi</button>
      <button class="primary" id="qrModalDownload">Scarica per la stampa</button>
    </div>
  </div>
</div>
```

- [ ] **Step 3: Aggiungere il caricamento condiviso del logo**

Dopo la riga `const BASE_URL = {{ base_url|tojson }} || window.location.origin;` (riga 152), aggiungere:

```js

function loadLogo(){
  return new Promise(resolve => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => resolve(null);
    img.src = '/logo';
  });
}
const logoReady = loadLogo();
```

- [ ] **Step 4: Aggiornare `openQrModal` per mostrare logo e autore**

Sostituire (righe 261-271):

```js
function openQrModal(id){
  const book = books.find(b => b.id === id);
  if(!book) return;
  modalBookId = id;
  document.getElementById('qrModalTitle').textContent = book.title;
  document.getElementById('qrModalId').textContent = id;
  const box = document.getElementById('qrModalBox');
  box.innerHTML = '';
  new QRCode(box, {text: bookPermalink(id), width: 220, height: 220, colorDark: '#22282A', colorLight: '#ffffff', correctLevel: QRCode.CorrectLevel.M});
  document.getElementById('qrModal').style.display = 'flex';
}
```

con:

```js
async function openQrModal(id){
  const book = books.find(b => b.id === id);
  if(!book) return;
  modalBookId = id;
  document.getElementById('qrModalTitle').textContent = book.title;
  document.getElementById('qrModalId').textContent = id;
  document.getElementById('qrModalAuthor').textContent = book.author || '';
  const logoImg = document.getElementById('qrModalLogo');
  const logo = await logoReady;
  logoImg.style.display = logo ? 'block' : 'none';
  if(logo) logoImg.src = logo.src;
  const box = document.getElementById('qrModalBox');
  box.innerHTML = '';
  new QRCode(box, {text: bookPermalink(id), width: 220, height: 220, colorDark: '#22282A', colorLight: '#ffffff', correctLevel: QRCode.CorrectLevel.M});
  document.getElementById('qrModal').style.display = 'flex';
}
```

`openQrModal` è già invocata solo da `onclick="openQrModal('${b.id}')"` (riga 245): renderla `async` non richiede altre modifiche, esattamente come già fatto per `confirmCheckout`/`confirmReturn` in questo stesso file.

- [ ] **Step 5: Verifica manuale — modale senza logo configurato**

Avviare l'app senza `LOGO_PATH` (come Step 3 del Task 1), poi con Playwright MCP:
1. `browser_navigate` su `http://127.0.0.1:5000/`, `browser_resize` a 390x844.
2. `browser_click` sul box QR di un libro qualsiasi (apre la modale).
3. `browser_take_screenshot`: verificare che NON compaia alcun logo/spazio vuoto sopra il titolo, e che sotto il codice libro compaia la riga con il nome dell'autore.

- [ ] **Step 6: Verifica manuale — modale con logo configurato**

Riavviare l'app con `LOGO_PATH` puntata a `static/apple-touch-icon.png` (come Step 4 del Task 1), ripetere gli stessi passi Playwright.

Expected: il logo compare centrato sopra il titolo, il resto invariato.

Fermare il server e rimuovere `scratch_logo_test.db` al termine del task.

- [ ] **Step 7: Commit**

```bash
git add templates/index.html
git commit -m "Show configurable logo and author in QR preview modal"
```

---

### Task 3: Frontend — logo, QR ridimensionato e autore nel PNG stampabile

**Files:**
- Modify: `templates/index.html` — funzione `downloadQr` (righe 295-323) e aggiunta di un helper vicino a `wrapText` (dopo la riga 293)

**Interfaces:**
- Consumes: Promise `logoReady` (Task 2).

- [ ] **Step 1: Aggiungere l'helper `fitContain` per il letterboxing del logo**

Dopo la riga 293 (chiusura di `wrapText`), aggiungere:

```js

function fitContain(imgW, imgH, boxW, boxH){
  const scale = Math.min(boxW / imgW, boxH / imgH);
  return {w: imgW * scale, h: imgH * scale};
}
```

- [ ] **Step 2: Riscrivere `downloadQr` per includere logo (se presente), QR a 520×520 e riga autore**

Sostituire l'intera funzione (righe 295-323):

```js
function downloadQr(){
  if(!modalBookId) return;
  const book = books.find(b => b.id === modalBookId);
  const tmp = document.createElement('div');
  new QRCode(tmp, {text: bookPermalink(modalBookId), width: 600, height: 600, colorDark: '#000000', colorLight: '#ffffff', correctLevel: QRCode.CorrectLevel.H});
  const qrCanvas = tmp.querySelector('canvas');
  const W = 800;
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = 980;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, W, canvas.height);
  ctx.drawImage(qrCanvas, 100, 60, 600, 600);
  ctx.fillStyle = '#000000';
  ctx.textAlign = 'center';
  ctx.font = '600 34px Georgia, serif';
  let y = 740;
  wrapText(ctx, book ? book.title : modalBookId, W - 120).slice(0, 3).forEach(line => {
    ctx.fillText(line, W / 2, y);
    y += 44;
  });
  ctx.font = '28px "IBM Plex Mono", monospace';
  ctx.fillText(modalBookId, W / 2, y + 14);
  const a = document.createElement('a');
  a.download = 'qr-' + modalBookId + '.png';
  a.href = canvas.toDataURL('image/png');
  a.click();
}
```

con:

```js
async function downloadQr(){
  if(!modalBookId) return;
  const book = books.find(b => b.id === modalBookId);
  const logo = await logoReady;

  const QR_SIZE = 520;
  const tmp = document.createElement('div');
  new QRCode(tmp, {text: bookPermalink(modalBookId), width: QR_SIZE, height: QR_SIZE, colorDark: '#000000', colorLight: '#ffffff', correctLevel: QRCode.CorrectLevel.H});
  const qrCanvas = tmp.querySelector('canvas');

  const W = 800;
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = 980;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, W, canvas.height);

  let y = 60;
  if(logo){
    const LOGO_BOX_W = 500, LOGO_BOX_H = 140, LOGO_TOP = 40;
    const {w, h} = fitContain(logo.naturalWidth, logo.naturalHeight, LOGO_BOX_W, LOGO_BOX_H);
    ctx.drawImage(logo, (W - w) / 2, LOGO_TOP + (LOGO_BOX_H - h) / 2, w, h);
    y = LOGO_TOP + LOGO_BOX_H + 20;
  }

  ctx.drawImage(qrCanvas, (W - QR_SIZE) / 2, y, QR_SIZE, QR_SIZE);
  y += QR_SIZE + 40;

  ctx.fillStyle = '#000000';
  ctx.textAlign = 'center';
  ctx.font = '600 34px Georgia, serif';
  wrapText(ctx, book ? book.title : modalBookId, W - 120).slice(0, 2).forEach(line => {
    ctx.fillText(line, W / 2, y);
    y += 44;
  });

  if(book && book.author){
    ctx.font = 'italic 22px Georgia, serif';
    ctx.fillStyle = '#555555';
    ctx.fillText(book.author, W / 2, y + 6);
    y += 34;
    ctx.fillStyle = '#000000';
  }

  ctx.font = '28px "IBM Plex Mono", monospace';
  ctx.fillText(modalBookId, W / 2, y + 14);

  const a = document.createElement('a');
  a.download = 'qr-' + modalBookId + '.png';
  a.href = canvas.toDataURL('image/png');
  a.click();
}
```

Nota: senza logo, il QR parte da `y = 60` (come nel layout originale) invece di lasciare vuoto lo spazio del banner; la dimensione del QR resta comunque 520×520 in entrambi i casi, per coerenza visiva tra le due varianti (con/senza logo) — non torna a 600×600.

- [ ] **Step 3: Verifica manuale — download senza logo**

Con l'app avviata senza `LOGO_PATH` (vedi Task 2 Step 5), via Playwright MCP:
1. Aprire la modale di un libro con autore valorizzato (es. "Se questo è un uomo" / Primo Levi).
2. `browser_evaluate` per intercettare il click di download e leggere il `dataURL` generato, oppure semplicemente cliccare "Scarica per la stampa" e verificare via `browser_evaluate` che `canvas.toDataURL` sia stato invocato senza eccezioni (nessun errore in console).
3. Aprire manualmente il PNG scaricato (cartella Download) e controllare a occhio: QR presente, titolo, autore "Primo Levi", codice "NAR-01", nessuno spazio vuoto anomalo in alto.

- [ ] **Step 4: Verifica manuale — download con logo**

Riavviare con `LOGO_PATH` puntata a `static/apple-touch-icon.png`, ripetere il download, controllare a occhio il PNG: logo in alto, poi QR, titolo, autore, codice, senza sovrapposizioni.

Fermare il server e rimuovere `scratch_logo_test.db` al termine del task.

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "Add logo banner and author line to printable QR image"
```

---

### Task 4: Documentazione — esempio in docker-compose.yml e voce di changelog

**Files:**
- Modify: `docker-compose.yml:1-13`
- Modify: `changelog.md:5-6`

- [ ] **Step 1: Aggiungere un esempio commentato di `LOGO_PATH` in `docker-compose.yml`**

Sostituire il contenuto attuale:

```yaml
services:
  bookshelf:
    build: .
    image: ghcr.io/stefano664/bookshelf-tracker:0.2.2
    ports:
      - "5000:5000"
    environment:
      - BASE_URL=https://books.stefano664.duckdns.org
    volumes:
      - ./data:/data
    restart: unless-stopped
```

con:

```yaml
services:
  bookshelf:
    build: .
    image: ghcr.io/stefano664/bookshelf-tracker:0.2.2
    ports:
      - "5000:5000"
    environment:
      - BASE_URL=https://books.stefano664.duckdns.org
      # - LOGO_PATH=/data/logo.png   # opzionale: logo sopra il QR nel PNG stampabile e nella sua anteprima
    volumes:
      - ./data:/data
      # - ./logo.png:/data/logo.png:ro   # monta qui il file del logo se LOGO_PATH è impostata
    restart: unless-stopped
```

- [ ] **Step 2: Aggiungere la voce di changelog**

In `changelog.md`, sostituire (righe 5-6):

```markdown
### Aggiunto
- Nella procedura di prestito, un pulsante rosso "×" accanto a "Conferma" permette di annullare l'operazione senza aggiornare la pagina (BOOK-003).
```

con:

```markdown
### Aggiunto
- Nella procedura di prestito, un pulsante rosso "×" accanto a "Conferma" permette di annullare l'operazione senza aggiornare la pagina (BOOK-003).
- Il PNG stampabile del QR (e la relativa anteprima) mostrano ora il nome dell'autore e, se configurato tramite la variabile d'ambiente `LOGO_PATH`, un logo sopra il QR.
```

- [ ] **Step 3: Verifica**

```bash
cd "c:/Users/stefano.mologni/OneDrive - COMELIT GROUP SPA/Documenti/Sviluppo/Git/Personale/bookshelf-tracker"
git diff docker-compose.yml changelog.md
```

Expected: il diff mostra esattamente le due aggiunte sopra, nessun'altra riga toccata.

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml changelog.md
git commit -m "Document LOGO_PATH in docker-compose example and changelog"
```
