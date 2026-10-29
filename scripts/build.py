#!/usr/bin/env python3
"""Generate GitHub Pages HTML from shared templates and JSON. Python stdlib only."""
import argparse
import html
import hashlib
import json
from pathlib import Path
from string import Template
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
ALL_PROJECTS = json.loads((ROOT / 'data/projects.json').read_text())
PROJECTS = [
    {**project, 'images': [image for image in project['images']
                          if image not in project.get('hidden_images', [])]}
    for project in ALL_PROJECTS if project.get('published', True)
]
ARCHIVE = json.loads((ROOT / 'data/archive.json').read_text())
IMAGES = json.loads((ROOT / 'data/images.json').read_text())
BASE = Template((ROOT / 'templates/base.html').read_text())
ASSET_VERSIONS = {kind: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:12]
                  for kind, path in [('css', 'assets/css/site.css'), ('js', 'assets/js/site.js'), ('play', 'assets/js/play.js')]}
OUTPUT = {}


def esc(value):
    return html.escape(str(value), quote=True)


def project_url(project):
    return project.get('url', project['slug'] + '.html')


def page(filename, title, description, content, active=''):
    navigation = []
    for url, label, key in [('portfolio.html', 'Portfolio', 'portfolio'),
                            ('chi-sono.html', 'Chi sono', 'about'),
                            ('percorso.html', 'Percorso', 'journey'),
                            ('contatti.html', 'Contatti ↗', 'contact')]:
        current = ' aria-current="page"' if active == key else ''
        navigation.append(f'<a href="{url}"{current}>{label}</a>')
    OUTPUT[filename] = BASE.substitute(title=esc(title), description=esc(description), logo_image=media_attributes('logo.png', '36px'),
                                       navigation=''.join(navigation), content=content,
                                       page_class='page-' + Path(filename).stem,
                                       css_version=ASSET_VERSIONS['css'], js_version=ASSET_VERSIONS['js'],
                                       extra_scripts=(f'<script src="assets/js/play.js?v={ASSET_VERSIONS["play"]}" defer></script>'
                                                      if filename == 'portfolio.html' else ''))


def heading(kicker, title, description=''):
    text = f'<p>{description}</p>' if description else ''
    return f'<header class="page-heading"><span class="eyebrow">{kicker}</span><h1>{title}</h1>{text}</header>'


def image_url(media, path):
    suffix = f'?v={media["version"]}' if media.get('version') else ''
    return quote(path, safe='/') + suffix


def media_attributes(original, sizes='(max-width: 540px) calc(100vw - 48px), 55vw'):
    media = IMAGES[original]
    preview = media['preview']
    srcset = ', '.join(f'{image_url(media, v["url"])} {v["width"]}w' for v in media['variants'])
    return f'src="{esc(image_url(media, preview["url"]))}" srcset="{esc(srcset)}" sizes="{esc(sizes)}" width="{preview["width"]}" height="{preview["height"]}"'


def picture(original, alt, cover=False, eager=False, sizes=None):
    media = IMAGES[original]
    sizes = sizes or ('(min-width: 1600px) 1440px, calc(100vw - 48px)' if cover else '(max-width: 540px) calc(100vw - 48px), 55vw')
    loading = 'eager' if cover or eager else 'lazy'
    return (f'<a class="cover-link" href="{esc(image_url(media, media["full"]["url"]))}" '
            f'data-lightbox data-original="{esc(image_url(media, "assets/images/" + original))}">'
            f'<img class="{"cover-image" if cover else "gallery-image"}" '
            f'{media_attributes(original, sizes)} alt="{esc(alt)}" loading="{loading}" decoding="async"></a>')


def resources(links):
    return '<div class="resource-links">' + ''.join(
        f'<a href="{esc(link["url"])}" target="_blank" rel="noopener noreferrer">{esc(link["label"])} ↗</a>'
        for link in links) + '</div>' if links else ''


def cards(projects, home=False):
    items = []
    for i, project in enumerate(projects):
        level = 'h3' if home else 'h2'
        loading = 'eager' if i < 2 else 'lazy'
        dims = IMAGE_SIZES[project['cover']]
        legacy_ids = {'night-train-ride': 'uiux', 'oscilloscope': 'arte', 'identita-visive': 'branding', 'manifesti': 'manifesti'}
        anchor = f' id="{legacy_ids[project["slug"]]}"' if not home and project['slug'] in legacy_ids else ''
        items.append(f'''<article class="project-card" data-category="{project['category']}"{anchor}>
  <a href="{project_url(project)}">
    <div class="project-visual" data-tone="{project['tone']}">
      <img {media_attributes(project['cover_original'])} alt="{esc(project['title'])} — {esc(project['discipline'])}" loading="{loading}" decoding="async">
      <span class="project-arrow" aria-hidden="true">↗</span>
    </div>
    <div class="project-meta"><{level}>{esc(project['title'])}</{level}><span>{esc(project['discipline'])}</span></div>
    <p>{esc(project['summary'])}</p>
  </a>
</article>''')
    return '<div class="projects-grid">' + '\n'.join(items) + '</div>'


def contact_band():
    return '''<section class="contact-band"><div><span class="eyebrow">Contatti</span><h2>Scrivimi<em>.</em></h2></div><a class="round-link" href="contatti.html" aria-label="Vai ai contatti">↗</a></section>'''


def home():
    content = '''<div class="wrap">
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero-copy">
      <span class="eyebrow">Portfolio personale</span>
      <h1 id="hero-title">Michele<br><em>Rinaldi</em><span class="hero-period">.</span></h1>
      <p class="hero-intro">Sono Michele, vengo da Cupramontana e studio Interaction Design al Politecnico di Milano. Da marzo lavoro di nuovo con SYEEW, questa volta come Interaction Designer. Qui raccolgo i progetti che ho realizzato all’università, per lavoro e per conto mio.</p>
      <a class="text-link" href="#lavori">I miei progetti <span aria-hidden="true">↓</span></a>
    </div>
    <figure class="hero-portrait"><img src="assets/images/foto_RinaldiMichele_1.png" alt="Michele Rinaldi" width="2015" height="2442" fetchpriority="high" decoding="async"></figure>
    <div class="hero-footer"><span>Interaction Design</span><span>Grafica e identità visiva</span><span>Cupramontana / Lecco</span></div>
  </section>
  <section id="lavori" aria-labelledby="selected-title">
    <div class="section-heading"><h2 id="selected-title"><span class="index">01 /</span>Progetti selezionati</h2><p>Interaction design e comunicazione visiva</p></div>'''
    content += cards(PROJECTS[:4], home=True)
    content += '''<div class="section-end"><a class="text-link" href="portfolio.html">Vai al portfolio <span aria-hidden="true">↗</span></a></div></section>
  <section class="about-strip"><div><span class="eyebrow">Chi sono</span><h2>La mia<br><em>storia.</em></h2></div><div><p>Sono nato e cresciuto a Cupramontana. A nove anni ho pubblicato il mio primo video: registravo, montavo e mi occupavo delle grafiche, imparando con i mezzi che avevo. È stato il primo progetto a cui ho lavorato con continuità, molto prima di scegliere informatica e poi Interaction Design. Nel frattempo la musica è sempre rimasta con me: suono la batteria da quando avevo sei anni.</p><a class="text-link" href="chi-sono.html">La mia storia <span aria-hidden="true">↗</span></a></div></section>'''
    content += contact_band() + '</div>'
    page('index.html', 'Portfolio', 'Michele Rinaldi. Progetti di interaction design, identità visiva e grafica.', content)


def portfolio():
    content = '''<div class="wrap portfolio-list">
      <header class="portfolio-heading">
        <div class="portfolio-kicker"><span>Design e comunicazione visiva</span><span>Selezione / 01—08</span></div>
        <div class="portfolio-masthead"><h1>Port<em>folio</em><span class="masthead-arrow" aria-hidden="true">↗</span></h1><p>Interfacce, identità visive<br>e progetti personali.</p></div>
      </header>
      <div class="portfolio-modes" data-portfolio-modes hidden aria-label="Vista del portfolio">
        <button type="button" data-mode="editorial" aria-pressed="true">Vista editoriale</button>
        <button type="button" data-mode="desk" aria-pressed="false">Gioca con i progetti ↗</button>
      </div>
      <div class="filters" data-project-filters aria-label="Filtra i progetti per disciplina" hidden>'''
    for key, label in [('tutti', 'Tutti i lavori'), ('interazione', 'Interazione e prodotto'), ('grafica', 'Grafica e comunicazione'), ('branding', 'Identità visiva')]:
        count = len(PROJECTS) if key == 'tutti' else sum(p['category'] == key for p in PROJECTS)
        if not count:
            continue
        pressed = 'true' if key == 'tutti' else 'false'
        content += f'<button type="button" data-filter="{key}" data-label="{label}" aria-pressed="{pressed}">{label}<sup aria-hidden="true">{count:02d}</sup></button>'
    content += '</div><p class="filter-status" data-filter-status role="status" aria-live="polite">Tutti i lavori: 8 progetti</p><div class="portfolio-board">'
    legacy_ids = {'night-train-ride': 'uiux', 'oscilloscope': 'arte', 'identita-visive': 'branding', 'manifesti': 'manifesti'}
    for index, project in enumerate(PROJECTS):
        anchor = legacy_ids.get(project['slug'], project['slug'])
        gallery = project['slug'] in ('identita-visive', 'manifesti')
        classes = 'folio-work project-card' + (' folio-collection' if gallery else '')
        content += f'<article class="{classes}" data-category="{project["category"]}" data-project="{project["slug"]}" id="{anchor}">'
        if gallery:
            content += f'<header class="collection-header"><span class="collection-index" aria-hidden="true">{index + 1:02d}</span><div><span class="eyebrow">{esc(project["discipline"])}</span><h2><a href="{project_url(project)}">{esc(project["title"])}</a></h2><p>{esc(project["summary"])}</p></div><a class="folio-open" href="{project_url(project)}" aria-label="Apri {esc(project["title"])}">↗</a></header>'
            grid_class = 'portfolio-gallery poster-wall' if project['slug'] == 'manifesti' else 'portfolio-gallery brand-wall'
            content += f'<div class="{grid_class}">'
            content += ''.join(picture(image, f'{project["title"]} — lavoro {i + 1}', sizes='(max-width: 540px) 42vw, 30vw') for i, image in enumerate(project['images']))
            content += '</div>'
        else:
            content += f'<div class="folio-order"><span>{index + 1:02d} /</span><span>{esc(project["discipline"])}</span></div>'
            content += f'<div class="folio-stage" data-tone="{project["tone"]}">' + picture(project['cover_original'], project['title'], eager=index < 2) + '<span class="stage-hint" aria-hidden="true">Ingrandisci ↗</span></div>'
            content += f'<div class="folio-caption"><h2><a href="{project_url(project)}">{esc(project["title"])}</a></h2><a class="folio-open" href="{project_url(project)}" aria-label="Apri il progetto {esc(project["title"])}">↗</a></div><p class="folio-summary">{esc(project["intro"])}</p>'
            content += f'<details class="work-details"><summary>Contesto e contributo</summary><p>{esc(project["intro"])}</p><dl class="portfolio-facts"><div><dt>Contesto</dt><dd>{esc(project["context"])}</dd></div><div><dt>Contributo</dt><dd>{esc(project["role"])}</dd></div></dl><a class="text-link" href="{project_url(project)}">Il progetto completo ↗</a></details>'
        content += '</article>'
    content += '</div>' + playground() + contact_band() + '</div>'
    content = content.replace('Selezione / 01—08', f'Selezione / 01—{len(PROJECTS):02d}').replace('Tutti i lavori: 8 progetti', f'Tutti i lavori: {len(PROJECTS)} progetti').replace('8 progetti sul tavolo.', f'{len(PROJECTS)} progetti sul tavolo.')
    page('portfolio.html', 'Portfolio', 'Il portfolio di Michele Rinaldi: progetti di interaction design, identità visiva, grafica e manifesti.', content, 'portfolio')


def playground():
    content = '''<section class="play-desk" data-play-desk hidden aria-label="Tavolo di lavoro interattivo">
      <div class="desk-toolbar"><p id="desk-help">Trascina le immagini. Con la tastiera: frecce per spostare, R per ruotare.</p><div><button type="button" data-desk-shuffle>Spariglia ↗</button><button type="button" data-desk-reset>Rimetti in ordine</button></div></div>
      <div class="play-canvas" data-play-canvas>'''
    for i, project in enumerate(PROJECTS):
        content += f'''<div class="play-card" data-play-category="{project['category']}" data-play-index="{i}" role="group" aria-label="{esc(project['title'])}">
          <button class="play-handle" type="button" aria-label="Sposta {esc(project['title'])}" aria-describedby="desk-help" aria-pressed="false"><img {media_attributes(project['cover_original'], "(max-width: 540px) 40vw, 220px")} alt="" draggable="false" loading="lazy"><span aria-hidden="true">↔</span></button>
          <a href="{project_url(project)}">{esc(project['title'])} <span aria-hidden="true">↗</span></a>
        </div>'''
    content += '''</div><p class="desk-status" data-desk-status role="status" aria-live="polite">8 progetti sul tavolo.</p></section>
    <section class="type-lab" data-type-lab hidden aria-label="Laboratorio di tipografia">
      <div class="section-heading"><h2>Prova la <em>tipografia.</em></h2><p>Scrivi, cambia carattere, scompiglia le lettere.</p></div>
      <div class="type-lab-controls"><label for="type-text">Il tuo testo<input id="type-text" type="text" value="Michele" maxlength="18" autocomplete="off" spellcheck="false"></label><div class="type-fonts" role="group" aria-label="Carattere"><button type="button" data-type-font="Manrope" aria-pressed="true">Sans</button><button type="button" data-type-font="Instrument" aria-pressed="false">Serif</button></div><label for="type-spacing">Spaziatura<input id="type-spacing" type="range" min="-6" max="12" value="-4" step="1"></label></div>
      <div class="type-paper" data-type-paper><div class="type-sample" data-type-sample role="img"></div><span aria-hidden="true" class="type-paper-mark">Aa / 01</span></div>
      <div class="type-lab-footer"><div role="group" aria-label="Colore del foglio"><button type="button" data-type-color="paper" aria-pressed="true">Carta</button><button type="button" data-type-color="blue" aria-pressed="false">Blu</button><button type="button" data-type-color="red" aria-pressed="false">Rosso</button></div><button class="type-mix" type="button" data-type-mix aria-pressed="false">Scompiglia le lettere ↗</button></div>
    </section>'''
    return content


def project_pages():
    for project in ALL_PROJECTS:
        if not project.get('published', True):
            content = '<div class="wrap archive-page">' + heading('Portfolio', 'Progetto non disponibile', 'Questa pagina non è disponibile al momento.')
            content += '<a class="text-link" href="portfolio.html">Torna al portfolio ↗</a></div>'
            page(project_url(project), 'Progetto non disponibile', 'Torna al portfolio di Michele Rinaldi.', content, 'portfolio')
    for index, project in enumerate(PROJECTS):
        content = '<article class="wrap"><a class="back-link" href="portfolio.html">← Tutti i lavori</a>'
        content += heading(project['discipline'], esc(project['title']))
        content += f'<div class="project-intro"><p>{esc(project["intro"])}</p><dl class="facts">'
        for label, key in [('Contesto', 'context'), ('Il mio contributo', 'role'), ('Strumenti / Ambito', 'tools'), ('Risultato', 'output')]:
            content += f'<div><dt>{label}</dt><dd>{esc(project[key])}</dd></div>'
        content += '</dl></div>' + picture(project['cover_original'], project['title'], cover=True)
        content += '<p class="image-caption">Seleziona l’immagine per ingrandirla. Nella galleria puoi aprire anche il file originale.</p>'
        if project.get('narrative'):
            content += '<div class="case-story prose">' + ''.join(f'<p>{esc(p)}</p>' for p in project['narrative']) + '</div>'
        for section in project['sections']:
            content += f'<section class="case-section"><h2>{esc(section["title"])}</h2><div class="prose">'
            content += ''.join(f'<p>{esc(p)}</p>' for p in section['paragraphs']) + '</div></section>'
        if project['images']:
            cls = ' posters' if project['slug'] == 'manifesti' else ''
            content += f'<div class="image-grid{cls}">'
            content += ''.join(picture(img, f'{project["title"]} — tavola {i + 1}') for i, img in enumerate(project['images']))
            content += '</div>'
        links = project['links']
        if project['slug'] == 'syeew':
            links = ARCHIVE['syeew_links']
            content += '<section class="case-section"><h2>Il diario del PCTO</h2><div>'
            # Keep the full first-person account, with absolute 2024 dates.
            for title, keys in [
                ('Figma / 27 maggio – 14 giugno 2024', ['experience_period1_para']),
                ('Flutter / 9 – 20 settembre 2024', ['experience_period2_para']),
                ('SMAU / 29 ottobre 2024', ['experience_period3_para1', 'experience_period3_para2', 'experience_period3_para3', 'experience_period3_para4']),
                ('Riflessioni e ringraziamenti', ['review_para1', 'review_para2', 'review_thanks_lead', 'review_thanks_para', 'review_final_thanks', 'review_sign_off'])]:
                text = ''.join(ARCHIVE['syeew'].get(key, '') for key in keys)
                content += f'<section class="pcto-journal"><h3>{title}</h3><div class="prose">{text}</div></section>'
            content += '</div></section>'
            content += '<div class="image-grid">' + ''.join(picture(f'syeew_smau_{i}.jpg', f'SMAU Milano 2024 — foto {i}') for i in range(1, 4)) + '</div>'
        if links:
            content += '<section class="case-section"><h2>Link e materiali</h2><div>' + resources(links) + '</div></section>'
        following = PROJECTS[(index + 1) % len(PROJECTS)]
        content += f'<nav class="next-project" aria-label="Progetto successivo"><span>Progetto successivo</span><a href="{project_url(following)}">{esc(following["title"])} ↗</a></nav></article>'
        page(project_url(project), project['title'], project['summary'], content, 'portfolio')


def about():
    chapters = json.loads((ROOT / 'data/story.json').read_text())
    content = '<div class="wrap story-page">' + heading('Chi sono', 'La mia <em>storia.</em>')
    content += '<div class="story-layout"><aside class="story-portrait"><img src="assets/images/foto_RinaldiMichele_1.png" alt="Michele Rinaldi" width="2015" height="2442"><a class="text-link" href="portfolio.html">I miei progetti ↗</a></aside><article class="story-prose">'
    for i, chapter in enumerate(chapters):
        content += f'<section id="{chapter["id"]}" class="story-chapter">'
        if i:
            content += f'<h2>{esc(chapter["title"])}</h2>'
        if chapter.get('note'):
            content += f'<p class="story-note">{esc(chapter["note"])}</p>'
        content += ''.join(chapter['paragraphs'])
        if chapter['id'] == 'musica':
            content += '<figure class="story-photo">' + picture('foto_RinaldiMichele_3.jpg', 'Durante un’esibizione con il Corpo Bandistico Don N. Bonanni') + '</figure>'
        content += '</section>'
    content += '</article></div>' + contact_band() + '</div>'
    page('chi-sono.html', 'La mia storia', 'Il racconto di Michele Rinaldi: Cupramontana, i primi video, informatica, musica e la scelta di Interaction Design.', content, 'about')


def journey():
    content = '<div class="wrap">' + heading('Percorso / Appunti e archivio', 'Il mio <em>percorso.</em>', 'Il lavoro in SYEEW, l’università e i materiali che ho raccolto durante la scuola.')
    content += '''<div class="timeline">
    <div class="timeline-item"><span>Da marzo / In corso</span><div><h3>Interaction Designer / SYEEW</h3><p>Sono rientrato nel team e sto ridisegnando le interfacce su cui avevo lavorato tre anni fa, quando iniziavo a usare Figma.</p><a class="text-link" href="pcto.html">Il lavoro in SYEEW ↗</a></div></div>
    <div class="timeline-item"><span>Università</span><div><h3>Interaction Design / Politecnico di Milano</h3><p>Il corso a Lecco e i primi progetti universitari di gruppo, tra cui Night Train Ride.</p></div></div>
    <div class="timeline-item"><span>2024 / PCTO</span><div><h3>SYEEW / Redesign e sviluppo Flutter</h3><p>Redesign dell’interfaccia in Figma e sviluppo di un prototipo mobile in Flutter.</p><a class="text-link" href="pcto.html">Leggi il caso studio ↗</a></div></div>
    <div class="timeline-item"><span>Scuola / Esame 2024/2025</span><div><h3>Informatica / IIS Marconi Pieralisi</h3><p>Ho studiato informatica al Marconi Pieralisi. Il sito è nato per raccogliere i miei lavori in occasione della maturità: qui sotto ci sono ancora i materiali delle diverse materie.</p></div></div>
    </div><div class="section-heading"><h2><span class="index">Archivio /</span>I lavori della scuola</h2><p>Materiali e approfondimenti.</p></div>
    <div class="archive-grid">
      <a class="archive-card" href="areatecnica.html"><span>01 / Tecnologia</span><h2>Area tecnica ↗</h2><p>Programmazione, reti, IA, matematica e gestione dei progetti.</p></a>
      <a class="archive-card" href="areaumanistica.html"><span>02 / Cultura</span><h2>Area umanistica ↗</h2><p>Letteratura, storia e il valore della memoria.</p></a>
      <a class="archive-card" href="educazionecivica.html"><span>03 / Cittadinanza</span><h2>Educazione civica ↗</h2><p>Pace, informazione e riflessioni sull’intelligenza artificiale.</p></a>
    </div><section class="case-section"><h2>La mia storia</h2><div><p>I video, la scuola, la musica e la scelta dell’università fanno parte dello stesso percorso. Li racconto nella pagina dedicata, dai primi video registrati a casa fino alla scelta di studiare Interaction Design.</p><a class="text-link" href="chi-sono.html">Leggi la mia storia ↗</a></div></section>'''
    content += contact_band() + '</div>'
    page('percorso.html', 'Percorso e archivio', 'Formazione, PCTO, università e archivio scolastico di Michele Rinaldi.', content, 'journey')


def archive_pages():
    titles = {'areatecnica.html': ('Area tecnica', 'Progetti di informatica, sistemi, intelligenza artificiale e matematica.'),
              'areaumanistica.html': ('Area umanistica', 'Ricerche e presentazioni di letteratura e storia.'),
              'educazionecivica.html': ('Educazione civica', 'Elaborati sulla pace, l’informazione e l’intelligenza artificiale.')}
    for filename, (title, subtitle) in titles.items():
        content = '<div class="wrap archive-page"><a class="back-link" href="percorso.html">← Percorso e archivio</a>'
        content += heading('Archivio scolastico / Esame 2024/2025', esc(title), subtitle)
        content += '<p class="archive-note">Questi materiali documentano il mio percorso scolastico. I documenti esterni sono conservati nei servizi originali: alcune risorse legate all’account istituzionale potrebbero non essere più accessibili.</p>'
        groups = ARCHIVE[filename]
        if len(groups) > 1:
            content += '<nav class="subject-nav" aria-label="Materie">' + ''.join(f'<a href="#{esc(g["id"])}">{esc(g["label"])}</a>' for g in groups) + '</nav>'
        for group in groups:
            content += f'<section class="archive-section" id="{esc(group["id"] or "documenti")}">'
            if group['label']:
                content += f'<h2>{esc(group["label"])}</h2>'
            for entry in group['items']:
                content += f'<details class="archive-entry"><summary><h3>{esc(entry["title"])}</h3><span>{esc(entry["date"])}</span></summary><div class="prose">'
                content += ''.join(entry['body']) + resources(entry['links'])
                if entry['embeds']:
                    content += resources([{'url':url, 'label':'Apri il documento originale'} for url in entry['embeds']])
                content += '</div></details>'
            content += '</section>'
        if filename == 'areaumanistica.html':
            content += '<a class="text-link" href="RinaldiMichele_Capolavoro1.html">Approfondimento: il capolavoro ↗</a>'
        content += '</div>'
        page(filename, title, f'{title}: elaborati e materiali dell’archivio scolastico di Michele Rinaldi.', content, 'journey')
    content = '<article class="wrap archive-page"><a class="back-link" href="areaumanistica.html">← Area umanistica</a>' + heading('Archivio / Capolavoro 2025', 'Il Nazismo nel<br>contesto del ’900', 'Il lavoro di ricerca presentato per l’Esame di Stato del 2025.')
    for entry in ARCHIVE['capolavoro']:
        content += f'<section class="case-section"><h2>{esc(entry["title"])}</h2><div class="prose">' + ''.join(entry['body']) + '</div></section>'
    content += resources(ARCHIVE['capolavoro_links'])
    content += '<section class="case-section"><h2>Gruppo di lavoro</h2><p>Michele Rinaldi, Luca Andreoni, Lorenzo Romagnoli, Riccardo Sabbatini Peverieri.</p></section></article>'
    page('RinaldiMichele_Capolavoro1.html', 'Il capolavoro', 'Il capolavoro di Michele Rinaldi: il Nazismo nel contesto del Novecento.', content, 'journey')


def contact():
    content = '''<div class="wrap contact-layout"><section class="contact-copy"><span class="eyebrow">Contatti</span><h1 class="contact-title"><em>Contatti.</em></h1><p>Se vuoi parlarmi di un progetto, chiedermi qualcosa su un lavoro che hai visto qui o fare due chiacchiere, puoi usare questo modulo. Mi arriveranno il tuo nome, il messaggio e l’indirizzo a cui risponderti. Se preferisci scrivere dalla tua casella, trovi anche la mia email qui sotto.</p><a class="contact-email" href="mailto:michelerinaldi.info@gmail.com">michelerinaldi.info@gmail.com ↗</a><a class="text-link" href="portfolio.html">Torna al portfolio ↗</a></section>
    <form class="contact-form" action="https://formsubmit.co/michelerinaldi.info@gmail.com" method="post" accept-charset="UTF-8">
      <input type="hidden" name="_subject" value="Nuovo messaggio dal portfolio di Michele Rinaldi">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="_next" value="https://michelerinaldi-stack.github.io/website/contatti.html">
      <input type="hidden" name="_url" value="https://michelerinaldi-stack.github.io/website/contatti.html">
      <div hidden aria-hidden="true"><label for="website">Lascia questo campo vuoto</label><input id="website" name="_honey" type="text" tabindex="-1" autocomplete="off"></div>
      <label for="name">Nome</label><input id="name" name="name" autocomplete="name" placeholder="Il tuo nome" required maxlength="150">
      <label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" placeholder="La tua email" required maxlength="254">
      <label for="message">Messaggio</label><textarea id="message" name="message" placeholder="Scrivi il tuo messaggio" required maxlength="10000"></textarea>
      <button type="submit">Invia il messaggio ↗</button><p class="form-note">Nome, email e messaggio vengono inoltrati tramite FormSubmit per permettermi di risponderti.</p>
    </form></div>'''
    page('contatti.html', 'Contatti', 'Scrivi a Michele Rinaldi tramite il modulo o a michelerinaldi.info@gmail.com.', content, 'contact')
    confirmation = '<div class="wrap archive-page">' + heading('Contatti', 'Grazie per il <em>messaggio.</em>', 'Se hai lasciato la tua email, potrò risponderti lì.')
    confirmation += '<div class="resource-links"><a href="portfolio.html">Torna al portfolio ↗</a><a href="contatti.html">Scrivi un altro messaggio ↗</a></div></div>'
    page('messaggio-inviato.html', 'Grazie per il messaggio', 'Grazie per aver contattato Michele Rinaldi.', confirmation, 'contact')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail when generated HTML is out of date')
    args = parser.parse_args()
    home()
    portfolio()
    project_pages()
    about()
    journey()
    archive_pages()
    contact()
    stale = []
    for filename, text in OUTPUT.items():
        path = ROOT / filename
        text = '<!-- Generated by scripts/build.py. Edit templates/ and data/ instead. -->\n' + '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
        if args.check:
            if not path.exists() or path.read_text() != text:
                stale.append(filename)
        else:
            path.write_text(text, encoding='utf-8')
    if stale:
        raise SystemExit('Rebuild required: ' + ', '.join(stale))
    print(f'{"Checked" if args.check else "Generated"} {len(OUTPUT)} static pages.')


IMAGE_SIZES = json.loads((ROOT / 'data/image-sizes.json').read_text())
if __name__ == '__main__':
    main()
