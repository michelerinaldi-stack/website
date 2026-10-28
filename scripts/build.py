#!/usr/bin/env python3
"""Generate GitHub Pages HTML from shared templates and JSON. Python stdlib only."""
import argparse
import html
import hashlib
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'data/projects.json').read_text())
ARCHIVE = json.loads((ROOT / 'data/archive.json').read_text())
BASE = Template((ROOT / 'templates/base.html').read_text())
ASSET_VERSIONS = {kind: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:12]
                  for kind, path in [('css', 'assets/css/site.css'), ('js', 'assets/js/site.js')]}
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
    OUTPUT[filename] = BASE.substitute(title=esc(title), description=esc(description),
                                       navigation=''.join(navigation), content=content,
                                       page_class='page-' + Path(filename).stem,
                                       css_version=ASSET_VERSIONS['css'], js_version=ASSET_VERSIONS['js'])


def heading(kicker, title, description=''):
    text = f'<p>{description}</p>' if description else ''
    return f'<header class="page-heading"><span class="eyebrow">{kicker}</span><h1>{title}</h1>{text}</header>'


def picture(original, alt, cover=False, eager=False):
    source = Path(original)
    preview = f'assets/images/previews/{source.stem}.webp'
    # Dimensions reserve image space and prevent layout shifts.
    dimensions = IMAGE_SIZES[source.stem]
    loading = 'eager' if cover or eager else 'lazy'
    return (f'<a class="cover-link" href="assets/images/{esc(original)}" data-lightbox>'
            f'<img class="{"cover-image" if cover else "gallery-image"}" '
            f'src="{preview}" alt="{esc(alt)}" width="{dimensions[0]}" height="{dimensions[1]}" '
            f'loading="{loading}" decoding="async"></a>')


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
      <img src="assets/images/previews/{project['cover']}.webp" alt="{esc(project['title'])} — {esc(project['discipline'])}" width="{dims[0]}" height="{dims[1]}" loading="{loading}" decoding="async">
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
      <p class="hero-intro">Mi occupo di interfacce, grafica e identità visiva. Il mio percorso parte dall’informatica e continua nell’Interaction Design.</p>
      <a class="text-link" href="#lavori">I miei progetti <span aria-hidden="true">↓</span></a>
    </div>
    <figure class="hero-portrait"><img src="assets/images/foto_RinaldiMichele_1.png" alt="Michele Rinaldi" width="2015" height="2442" fetchpriority="high" decoding="async"></figure>
    <div class="hero-footer"><span>Interaction Design</span><span>Grafica e identità visiva</span><span>Cupramontana / Lecco</span></div>
  </section>
  <section id="lavori" aria-labelledby="selected-title">
    <div class="section-heading"><h2 id="selected-title"><span class="index">01 /</span>Progetti selezionati</h2><p>Interaction design e comunicazione visiva</p></div>'''
    content += cards(PROJECTS[:4], home=True)
    content += '''<div class="section-end"><a class="text-link" href="portfolio.html">Vai al portfolio <span aria-hidden="true">↗</span></a></div></section>
  <section class="about-strip"><div><span class="eyebrow">Chi sono</span><h2>Dall’informatica<br>al design.</h2></div><div><p>Vengo da Cupramontana. Ho studiato informatica al Marconi Pieralisi di Jesi e ho scelto di proseguire con Interaction Design al Politecnico di Milano. La grafica è entrata nel mio percorso attraverso i video, i progetti personali e la musica. Suono la batteria da quando avevo sei anni.</p><a class="text-link" href="chi-sono.html">La mia storia <span aria-hidden="true">↗</span></a></div></section>'''
    content += contact_band() + '</div>'
    page('index.html', 'Portfolio', 'Michele Rinaldi. Progetti di interaction design, identità visiva e grafica.', content)


def portfolio():
    content = '''<div class="wrap portfolio-list">
      <header class="portfolio-heading">
        <div class="portfolio-kicker"><span>Design e comunicazione visiva</span><span>Selezione / 01—08</span></div>
        <div class="portfolio-masthead"><h1>Port<em>folio</em><span aria-hidden="true">↗</span></h1><p>Interfacce, identità visive<br>e progetti personali.</p></div>
      </header>
      <div class="filters" data-project-filters aria-label="Filtra i progetti per disciplina" hidden>'''
    for key, label in [('tutti', 'Tutti i lavori'), ('interazione', 'Interazione e prodotto'), ('grafica', 'Grafica e comunicazione'), ('branding', 'Identità visiva')]:
        count = len(PROJECTS) if key == 'tutti' else sum(p['category'] == key for p in PROJECTS)
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
            content += ''.join(picture(image, f'{project["title"]} — lavoro {i + 1}') for i, image in enumerate(project['images']))
            content += '</div>'
        else:
            content += f'<div class="folio-order"><span>{index + 1:02d} /</span><span>{esc(project["discipline"])}</span></div>'
            content += f'<div class="folio-stage" data-tone="{project["tone"]}">' + picture(project['cover_original'], project['title'], eager=index < 2) + '<span class="stage-hint" aria-hidden="true">Ingrandisci ↗</span></div>'
            content += f'<div class="folio-caption"><h2><a href="{project_url(project)}">{esc(project["title"])}</a></h2><a class="folio-open" href="{project_url(project)}" aria-label="Apri il progetto {esc(project["title"])}">↗</a></div><p class="folio-summary">{esc(project["summary"])}</p>'
            content += f'<details class="work-details"><summary>Contesto e contributo</summary><p>{esc(project["intro"])}</p><dl class="portfolio-facts"><div><dt>Contesto</dt><dd>{esc(project["context"])}</dd></div><div><dt>Contributo</dt><dd>{esc(project["role"])}</dd></div></dl><a class="text-link" href="{project_url(project)}">Il progetto completo ↗</a></details>'
        content += '</article>'
    content += '</div>' + contact_band() + '</div>'
    page('portfolio.html', 'Portfolio', 'Il portfolio di Michele Rinaldi: progetti di interaction design, identità visiva, grafica e manifesti.', content, 'portfolio')


def project_pages():
    for index, project in enumerate(PROJECTS):
        content = '<article class="wrap"><a class="back-link" href="portfolio.html">← Tutti i lavori</a>'
        content += heading(project['discipline'], esc(project['title']))
        content += f'<div class="project-intro"><p>{esc(project["intro"])}</p><dl class="facts">'
        for label, key in [('Contesto', 'context'), ('Il mio contributo', 'role'), ('Strumenti / Ambito', 'tools'), ('Risultato', 'output')]:
            content += f'<div><dt>{label}</dt><dd>{esc(project[key])}</dd></div>'
        content += '</dl></div>' + picture(project['cover_original'], project['title'], cover=True)
        content += '<p class="image-caption">Seleziona l’immagine per vederla nel formato originale.</p>'
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
                content += f'<details class="archive-entry"><summary><h3>{title}</h3></summary><div class="prose">{text}</div></details>'
            content += '</div></section>'
            content += '<div class="image-grid">' + ''.join(picture(f'syeew_smau_{i}.jpg', f'SMAU Milano 2024 — foto {i}') for i in range(1, 4)) + '</div>'
        if links:
            content += '<section class="case-section"><h2>Link e materiali</h2><div>' + resources(links) + '</div></section>'
        following = PROJECTS[(index + 1) % len(PROJECTS)]
        content += f'<nav class="next-project" aria-label="Progetto successivo"><span>Progetto successivo</span><a href="{project_url(following)}">{esc(following["title"])} ↗</a></nav></article>'
        page(project_url(project), project['title'], project['summary'], content, 'portfolio')


def about():
    content = '<div class="wrap">' + heading('Chi sono', 'Michele <em>Rinaldi.</em>')
    content += '''<div class="portrait-layout"><img class="portrait" src="assets/images/foto_RinaldiMichele_1.png" alt="Michele Rinaldi" width="2015" height="2442"><div class="prose"><p>Vengo da Cupramontana, nelle Marche. Ho studiato informatica al Marconi Pieralisi di Jesi e ho scelto Interaction Design al Politecnico di Milano, nella sede di Lecco.</p><p>Ho iniziato a occuparmi di grafica mentre montavo i miei video. Poi sono arrivati Photoshop, Figma e Fusion 360, le prime interfacce e i lavori per eventi e musicisti.</p><p>Durante il PCTO in SYEEW ho lavorato al redesign di un’app e a una demo in Flutter. In università ho iniziato a lavorare anche su progetti di interazione in gruppo, come Night Train Ride.</p><a class="text-link" href="portfolio.html">I miei progetti ↗</a></div></div>
    <section class="case-section"><h2>I primi video</h2><div class="prose"><p>Il 10 agosto 2015, a nove anni, ho pubblicato il mio primo video. Nei tre anni successivi ne ho realizzati 213: gameplay, curiosità storiche con mio fratello, magie, esperimenti e tutorial.</p><p>Mi occupavo di tutto, dal montaggio alle grafiche, imparando da solo. È stato il primo modo che ho trovato per unire racconto, tecnologia e un progetto tutto mio.</p></div></section>
    <section class="portrait-layout"><div class="prose"><span class="eyebrow">Musica</span><h2 class="contact-title">La <em>batteria.</em></h2><p>Studio musica da quando avevo quattro anni e suono la batteria da quando ne avevo sei. Faccio parte del Corpo Bandistico Don N. Bonanni di Cupramontana.</p><p>Ho affiancato gli insegnanti nei corsi musicali e nei centri estivi, lavorando con bambini e ragazzi. Insegnare percussioni mi ha fatto scoprire un altro modo di condividere quello che mi appassiona.</p></div><img src="assets/images/previews/foto_RinaldiMichele_3.webp" alt="Michele durante un’esibizione con il corpo bandistico" loading="lazy" width="720" height="960"></section>'''
    content += contact_band() + '</div>'
    page('chi-sono.html', 'Chi sono', 'La storia di Michele Rinaldi, tra informatica, interaction design, video e musica.', content, 'about')


def journey():
    content = '<div class="wrap">' + heading('Percorso / Appunti e archivio', 'Il mio <em>percorso.</em>', 'Gli studi, il PCTO e i materiali dell’esame di maturità del 2025.')
    content += '''<div class="timeline">
    <div class="timeline-item"><span>Università</span><div><h3>Interaction Design / Politecnico di Milano</h3><p>Il corso a Lecco e i primi progetti universitari di gruppo, tra cui Night Train Ride.</p></div></div>
    <div class="timeline-item"><span>2024 / PCTO</span><div><h3>SYEEW / Redesign e sviluppo Flutter</h3><p>Redesign dell’interfaccia in Figma e sviluppo di un prototipo mobile in Flutter.</p><a class="text-link" href="pcto.html">Leggi il caso studio ↗</a></div></div>
    <div class="timeline-item"><span>Scuola / Esame 2024/2025</span><div><h3>Informatica / IIS Marconi Pieralisi</h3><p>Programmazione, sistemi, intelligenza artificiale, ma anche cultura umanistica e cittadinanza. Il sito è nato per raccogliere questi lavori in occasione della maturità.</p></div></div>
    </div><div class="section-heading"><h2><span class="index">Archivio /</span>I lavori della scuola</h2><p>Materiali e approfondimenti.</p></div>
    <div class="archive-grid">
      <a class="archive-card" href="areatecnica.html"><span>01 / Tecnologia</span><h2>Area tecnica ↗</h2><p>Programmazione, reti, IA, matematica e gestione dei progetti.</p></a>
      <a class="archive-card" href="areaumanistica.html"><span>02 / Cultura</span><h2>Area umanistica ↗</h2><p>Letteratura, storia e il valore della memoria.</p></a>
      <a class="archive-card" href="educazionecivica.html"><span>03 / Cittadinanza</span><h2>Educazione civica ↗</h2><p>Pace, informazione e riflessioni sull’intelligenza artificiale.</p></a>
    </div><section class="case-section"><h2>Il racconto originale</h2><div><p>La storia personale e le riflessioni scritte per l’esame, conservate come tappa del percorso.</p>'''
    for i, entry in enumerate(ARCHIVE['story']):
        # Mark historical future plans clearly rather than presenting them as current.
        content += f'<details class="archive-entry"><summary><h3>{esc(entry["title"])}</h3><span>Testo del 2025</span></summary><div class="prose">' + ''.join(entry['body']) + '</div></details>'
    content += '</div></section>' + contact_band() + '</div>'
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
    content = '''<div class="wrap contact-layout"><section class="contact-copy"><span class="eyebrow">Contatti</span><h1 class="contact-title"><em>Contatti.</em></h1><p>Puoi scrivermi per un progetto, una collaborazione o informazioni sui miei lavori. Lascia la tua email per ricevere una risposta.</p><a class="text-link" href="portfolio.html">Torna al portfolio ↗</a></section>
    <form class="contact-form" action="https://formspree.io/f/xovwnrjq" method="post">
      <label for="name">Nome</label><input id="name" name="name" autocomplete="name" placeholder="Il tuo nome" required maxlength="150">
      <label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" placeholder="La tua email" required maxlength="254">
      <label for="message">Messaggio</label><textarea id="message" name="message" placeholder="Scrivi il tuo messaggio" required maxlength="10000"></textarea>
      <button type="submit">Invia il messaggio ↗</button><p class="form-note">Il modulo usa Formspree per inoltrare il messaggio. Inviandolo, condividi nome, email e testo per permettermi di risponderti.</p>
    </form></div>'''
    page('contatti.html', 'Contatti', 'Contatta Michele Rinaldi per un progetto, una collaborazione o un saluto.', content, 'contact')


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
