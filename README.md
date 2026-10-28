# Michele Rinaldi — portfolio personale

Portfolio statico, pubblicabile direttamente su GitHub Pages. Nato per l’Esame di Stato 2024/2025, raccoglie progetti di interaction design, grafica, identità visiva e il percorso personale di Michele.

## Struttura

- **Home:** presentazione e quattro lavori selezionati.
- **Portfolio:** otto progetti/raccolte, filtrabili per disciplina.
- **Progetti:** contesto, contributo, racconto, immagini e collegamenti.
- **Chi sono:** il percorso tra informatica, design, video e musica.
- **Percorso:** università, SYEEW e archivio scolastico.
- **Contatti:** modulo Formspree del sito originale.

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

I vecchi CSS vendor sono conservati tra gli asset, ma il nuovo sito non li carica. Non ci sono font o librerie caricati da CDN, richieste a traduzioni mancanti o script locali inesistenti.

## GitHub Pages e servizi esterni

Continua a pubblicare la radice (`/`) del ramo configurato in **Settings → Pages**. Tutti i link locali sono relativi e funzionano sotto `/website/`; non serve un dominio personalizzato.

Il modulo usa l’endpoint Formspree originale. La validazione locale è verificabile senza inviare messaggi; la consegna effettiva dipende dallo stato dell’account Formspree e va verificata con un invio consapevole del proprietario. Non sono state inviate richieste durante i test.

I collegamenti a Figma, Behance, Google Drive e altri servizi rimangono esterni. L’archivio segnala che i documenti dell’account scolastico potrebbero essere inaccessibili. Il controllo locale non verifica la disponibilità dei documenti esterni.

## Accessibilità

Navigazione e contenuti funzionano senza JavaScript. I filtri appaiono solo quando il relativo script è attivo; le immagini restano normali link. Il dialog della galleria supporta Escape, chiusura con pulsante e ritorno del focus. Le sezioni d’archivio usano `details` nativi. Sono inclusi link per saltare al contenuto, focus visibile, etichette dei campi e rispetto di `prefers-reduced-motion`.
