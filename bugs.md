## Defect BOOK-001 [FIXED]

** Description **
In the book reservation/availability card, the optional name input field ("Nome facoltativo") located in the bottom-left corner is severely misaligned or truncated. The input box is rendered as a very narrow, vertical rectangle, making it impossible for users to see or properly review the text string they type into it.

** Steps to Reproduce **
Navigate to the book availability/reservation screen.

Locate the card for "Se questo è un uomo" by "Primo Levi" (ID: NAR-01).

Observe the input field located directly below the "Nome facoltativo" label in the bottom-left corner.

Click inside the input field and attempt to type a name.

** Expected Result **
The input field under the "Nome facoltativo" label should be horizontally wide enough to accommodate standard text entry comfortably, ensuring that any entered text string remains fully visible and readable to the user.

---

## Defect BOOK-002

** Descrizione **

Il nome dell'utente che ha preso in prestito il libro, se inserito da smartphone, viene salvato con le lettere al contrario.

** Steps per riprodurre **

1. Cliccare su "Segna come preso"
2. Inserire il proprio nome nella casella di testo (es. Stefano)
3. Cliccare su "Conferma"
4. Verificare il nome presente nella colonna "UTENTE" del log: da cellulare viene presentato il nome al contratio (es. onafetS)

---

## Defect BOOK-003 [FIXED]

** Descrizione **

Una volta avviata la procedura di prestito non è possibile interromperla se non aggiornando la pagina

** Steps per riprodurre **

1. Cliccare su "Segna come preso"
2. Il sistema presenta il tasto "CONFERMA" in verde ma nessun pulsante per annullare

** Soluzione **

Introdurre un pulsante di annullamento, rosso con una X grande, che riporti allo stato precedente