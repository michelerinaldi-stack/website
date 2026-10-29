# Michele Rinaldi — portfolio personale

Portfolio statico, pubblicabile direttamente su GitHub Pages. Nato per l’Esame di Stato 2024/2025, raccoglie progetti di interaction design, grafica, identità visiva e il percorso personale di Michele.

## Struttura

- **Home:** presentazione e quattro lavori selezionati.
- **Portfolio:** composizione asimmetrica con otto progetti/raccolte, filtri, dettagli espandibili e gallerie di loghi e manifesti.
- **Progetti:** contesto, contributo, racconto, immagini e collegamenti.
- **Chi sono:** il percorso tra informatica, design, video e musica.
- **Percorso:** università, SYEEW e archivio scolastico.
- **Contatti:** modulo FormSubmit indirizzato a `michelerinaldi.info@gmail.com`.

Le pagine scolastiche mantengono i nomi originali. Anche `pcto.html` rimane raggiungibile, come caso studio SYEEW. I testi del 2025 sono dichiarati storici; i programmi di allora non sono presentati come programmi futuri attuali.

## Aggiornare i contenuti

1. Modifica `data/projects.json` per aggiungere o aggiornare progetti. L’ordine determina la sequenza nel portfolio; i primi quattro compaiono in home.
2. Modifica `templates/base.html` per header, navigazione, footer e metadati condivisi.
3. Gli altri contenuti e le strutture delle pagine sono in `scripts/build.py`. L’archivio estratto dal sito originale è in `data/archive.json`.
4. Gli stili sono in **un solo file**, `assets/css/site.css`; le interazioni in `assets/js/site.js`.
5. Rigenera e controlla con Python 3, senza pacchetti aggiuntivi:

```sh
python3 scripts/build.py
python3 scripts/check.py
```

Gli HTML nella radice sono generati e già inclusi nel repository: GitHub Pages non deve eseguire Python. Non modificarli direttamente, perché la rigenerazione li sovrascrive.

## Anteprima locale

```sh
python3 -m http.server 8000
```

Apri `http://localhost:8000`. Non servono Node, npm, framework o compilazione JavaScript.

## Immagini

Gli asset originali rimangono nei loro percorsi e non sono stati modificati. Le anteprime WebP in `assets/images/previews/` riducono il peso delle pagine; la galleria apre gli originali. Le dimensioni delle anteprime sono in `data/image-sizes.json`.

Per aggiungere un’immagine, conserva l’originale in `assets/images/`, crea un’anteprima WebP con lato massimo 1440 px, registrane larghezza e altezza in `data/image-sizes.json` e usa i percorsi nella scheda del progetto. Non assegnare lo stesso nome base a immagini diverse.

La tipografia usa Manrope e Instrument Serif, ospitati in `assets/fonts/` con le rispettive licenze OFL. CSS e JavaScript includono nel loro URL una firma del contenuto per aggiornare la cache dopo ogni pubblicazione.

I vecchi CSS vendor sono conservati tra gli asset, ma il nuovo sito non li carica. Non ci sono font o librerie caricati da CDN, richieste a traduzioni mancanti o script locali inesistenti.

## GitHub Pages e servizi esterni

Continua a pubblicare la radice (`/`) del ramo configurato in **Settings → Pages**. Tutti i link locali sono relativi e funzionano sotto `/website/`; non serve un dominio personalizzato.

Il modulo usa `https://formsubmit.co/michelerinaldi.info@gmail.com`. Nome, email del visitatore e messaggio sono inoltrati a questo indirizzo. Il campo `email` consente di rispondere direttamente al mittente; `_subject` specifica l’oggetto e `_next` riporta esattamente a `https://michelerinaldi-stack.github.io/website/contatti.html`, come richiesto. Il reCAPTCHA di FormSubmit rimane attivo e un honeypot aggiunge un controllo contro gli invii automatici.

**Attivazione necessaria:** il proprietario deve confermare l’indirizzo cliccando l’email di attivazione inviata da FormSubmit al primo invio. Fino a quel momento il destinatario è configurato, ma la consegna non è verificata. Il servizio può trattenere gli invii in attesa di conferma. Controllare anche Spam e Promozioni. Il collegamento `mailto:` nella pagina Contatti permette di scrivere direttamente dalla propria applicazione email.

I test automatici intercettano gli invii prima della rete per controllare destinatario, campi e redirect. La ricezione effettiva deve essere verificata nella casella del proprietario dopo l’attivazione.

I collegamenti a Figma, Behance, Google Drive e altri servizi rimangono esterni. L’archivio segnala che i documenti dell’account scolastico potrebbero essere inaccessibili. Il controllo locale non verifica la disponibilità dei documenti esterni.

## Accessibilità

Navigazione e contenuti funzionano senza JavaScript. I filtri appaiono solo quando il relativo script è attivo; le immagini restano normali link. Il dialog della galleria supporta Escape, chiusura con pulsante e ritorno del focus. Le sezioni d’archivio usano `details` nativi. Sono inclusi link per saltare al contenuto, focus visibile, etichette dei campi e rispetto di `prefers-reduced-motion`.

## Microinterazioni

Le interazioni sono in `assets/js/site.js` e nella sezione finale di `assets/css/site.css`:

- Le anteprime seguono leggermente il puntatore; l’area cliccabile rimane ferma.
- I titoli reagiscono al puntatore e al tocco, conservando le legature dei font.
- I filtri animano l’ingresso e il riposizionamento dei lavori, senza ritardare i risultati.
- Le sezioni `details` si aprono e chiudono con animazioni interrompibili.
- La galleria mantiene Escape e ritorno del focus, con frecce, contatore e swipe orizzontale.
- Entrata dei contenuti allo scorrimento, indicatore di lettura e ritorno all’inizio.

`prefers-reduced-motion` disattiva i movimenti, anche quando la preferenza cambia durante la visita. Gli effetti al puntatore sono attivi soltanto su dispositivi con puntatore preciso. Non ci sono animazioni continue o dipendenze aggiuntive; senza JavaScript rimangono contenuti, link alle immagini e controlli nativi.

## Storia personale, playground e immagini responsive

`data/story.json` contiene il racconto personale, presentato in Chi sono come un articolo continuo. I testi sono stati rivisti per usare un tono diretto, conservando episodi e dettagli personali ed evitando contrapposizioni retoriche, slogan e conclusioni generiche. Il capitolo sulla scelta universitaria è contestualizzato nel 2025 e mantiene il racconto del test e delle due graduatorie. Il ritorno in SYEEW come Interaction Designer è riportato in home, Percorso e nella scheda del progetto; gli aggiornamenti lavorativi restano fuori dal racconto di Chi sono. Il mese di marzo è indicato senza aggiungere un anno non confermato.

Il Portfolio offre una vista editoriale e un tavolo di lavoro opzionale. Le immagini si trascinano dall’area dedicata, anche su touch; le frecce e R permettono lo stesso uso da tastiera. I pulsanti Spariglia e Rimetti in ordine agiscono soltanto sulla disposizione temporanea. Il laboratorio tipografico permette di cambiare testo, carattere, spaziatura e colori. Tutto rimane locale alla pagina e non cambia i contenuti del portfolio.

Le immagini raster hanno copie WebP responsive a 480, 960 e fino a 1440 px, oltre a una copia per la galleria con lato massimo di 2560 px. Il manifest è `data/images.json`; i numeri della conversione sono in `data/image-optimization.json`. La foto principale resta nel formato PNG originale trasparente, come richiesto. SVG e JSON di animazione non vengono convertiti. Il collegamento File originale nella galleria conserva l’accesso al materiale originale.

Per rigenerare i derivati dopo l’aggiunta di un’immagine, installa Pillow nell’ambiente di lavoro ed esegui `python3 scripts/optimize_images.py`, quindi `python3 scripts/build.py`. Gli originali non vengono sovrascritti. Per la sola rigenerazione HTML continua a bastare Python senza pacchetti aggiuntivi.

Il selettore del tavolo sperimentale è nascosto nella navigazione normale. Per mostrarlo aprire `portfolio.html?play=1`. Il laboratorio tipografico rimane disponibile nella pagina.

## Aggiornamenti frequenti del portfolio

Il portfolio è in una fase di aggiornamento frequente: saranno aggiunti, sostituiti e rimossi molti lavori. Mantenere i contenuti in `data/projects.json`, preservare i file originali e preferire la rimozione dalla pubblicazione quando una modifica è temporanea.

- Per nascondere un intero progetto: `"published": false`; per ripristinarlo: `true`.
- Per nascondere una sola immagine: aggiungere il suo percorso a `hidden_images` nel progetto. Rimane nell’elenco `images` e sul disco, ma scompare da tutte le gallerie pubbliche. Per ripristinarla, rimuoverla da `hidden_images`.
- Per cambiare l’ordine: riordinare `images` o i progetti nel JSON. I primi quattro progetti pubblicati sono quelli mostrati in home.
- Per aggiungere un’immagine: aggiungere l’originale e il percorso a `images`, poi rigenerare con `scripts/optimize_images.py` e `scripts/build.py`.
- Per sostituire un file esistente: usare `scripts/optimize_images.py --refresh percorso/immagine.jpg` prima di rigenerare, così viene aggiornata anche la cache delle immagini.

Al momento `manifesti_7.jpg`, `manifesti_8.jpg` e `manifesti_9.jpg` sono conservati ma nascosti; la raccolta pubblica contiene i primi sei manifesti.

In Chi sono, 22 dettagli sono legati a episodi precisi del racconto e configurati con `data-spark` in `data/story.json`. Ogni effetto ha un solo punto di attivazione: registrazione YouTube, conteggio dei 213 video, timeline di montaggio, codice, parentesi, pennello Photoshop (anche sulla foto), riavvio, volume 3D, selezione Figma, pacchetto tra nodi di rete, voto, podio, equalizzatore, onde dal vivo, quattro colpi di batteria, metronomo, lettere che si uniscono, puntatore, attesa, salto, quiete e costruzione. Non aggiungere una decorazione a una parola senza un legame con ciò che racconta.

Non ci sono popup, controlli aggiuntivi o informazioni da aprire. Mouse e tocchi brevi attivano effetti finiti; lo scorrimento touch resta nativo. Un secondo passaggio riparte subito e annulla l’effetto precedente. Le righe riservano lo spazio del peso maggiore; testi e punteggiatura rimangono integri per screen reader e senza JavaScript. La riduzione del movimento conserva solo i dettagli statici.
