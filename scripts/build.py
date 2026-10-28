#!/usr/bin/env python3
"""Generate GitHub Pages HTML from shared templates and JSON. Python stdlib only."""
import argparse
import html
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'data/projects.json').read_text())
ARCHIVE = json.loads((ROOT / 'data/archive.json').read_text())
BASE = Template((ROOT / 'templates/base.html').read_text())
OUTPUT = {}


def esc(value):
    return html.escape(str(value), quote=True)


def project_url(project):
    return project.get('url', project['slug'] + '.html')


def page(filename, title, description, content, active=''):
    navigation = []
    for url, label, key in [('portfolio.html', 'Lavori', 'portfolio'),
                            ('chi-sono.html', 'Chi sono', 'about'),
                            ('percorso.html', 'Percorso', 'journey'),
                            ('contatti.html', 'Parliamone ↗', 'contact')]:
        current = ' aria-current="page"' if active == key else ''
        navigation.append(f'<a href="{url}"{current}>{label}</a>')
    OUTPUT[filename] = BASE.substitute(title=esc(title), description=esc(description),
                                       navigation=''.join(navigation), content=content)


def heading(kicker, title, description=''):
    text = f'<p>{description}</p>' if description else ''
    return f'<header class="page-heading"><span class="eyebrow">{kicker}</span><h1>{title}</h1>{text}</header>'


def picture(original, alt, cover=False):
    source = Path(original)
    preview = f'assets/images/previews/{source.stem}.webp'
    # Dimensions reserve image space and prevent layout shifts.
    dimensions = IMAGE_SIZES[source.stem]
    loading = 'eager' if cover else 'lazy'
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
    return '''<section class="contact-band"><div><span class="eyebrow">Le cose belle iniziano parlando</span><h2>Hai qualcosa<br>in mente?</h2></div><a class="round-link" href="contatti.html" aria-label="Parliamo del tuo progetto">↗</a></section>'''


def home():
    content = '''<div class="wrap">
  <section class="hero" aria-labelledby="hero-title">
    <span class="eyebrow">Michele Rinaldi · Portfolio personale</span>
    <h1 id="hero-title">Un po’ design.<br>Un po’ codice.<br><em>Molto curioso.</em></h1>
    <div class="hero-bottom">
      <div><p class="hero-intro">Progetto interfacce, identità visive e cose che raccontano qualcosa. Mi piace capire come funzionano. E come potrebbero funzionare meglio.</p><a class="text-link" href="#lavori">Esplora i miei lavori <span aria-hidden="true">↓</span></a></div>
      <div class="hero-aside"><img src="assets/images/previews/foto_RinaldiMichele_1.webp" alt="Ritratto di Michele Rinaldi" width="66" height="76"><p>Interaction Design · Informatica<br>Con la musica sempre in sottofondo.</p></div>
    </div>
  </section>
  <section id="lavori" aria-labelledby="selected-title">
    <div class="section-heading"><h2 id="selected-title"><span class="index">01 /</span>Lavori selezionati</h2><p>Interazioni, immagini, esperimenti.</p></div>'''
    content += cards(PROJECTS[:4], home=True)
    content += '''<div class="section-end"><a class="text-link" href="portfolio.html">Tutti i progetti <span aria-hidden="true">↗</span></a></div></section>
  <section class="about-strip"><div><span class="eyebrow">La persona dietro i progetti</span><h2>Mi piace dare<br>forma alle idee.</h2></div><div><p>Sono Michele. Vengo da Cupramontana e il mio percorso unisce informatica e Interaction Design. Da bambino montavo video; oggi passo dalle interfacce alla grafica. Quando non progetto, suono la batteria.</p><div class="skill-line"><span>Interaction design</span><span>Comunicazione visiva</span><span>Codice</span><span>Musica</span></div><a class="text-link" href="chi-sono.html">Qualcosa in più su di me <span aria-hidden="true">↗</span></a></div></section>'''
    content += contact_band() + '</div>'
    page('index.html', 'Design, codice e curiosità', 'Il portfolio di Michele Rinaldi: interaction design, identità visive, grafica e progetti tra tecnologia e creatività.', content)


def portfolio():
    content = '<div class="wrap portfolio-list">' + heading('Portfolio / Tutti i lavori', 'Idee che prendono <em>forma.</em>', 'Interfacce, identità visive, musica e sperimentazioni. Una selezione di quello che ho progettato e di ciò che sto imparando.')
    content += '''<div class="filters" data-project-filters aria-label="Filtra i progetti per disciplina" hidden>
      <button type="button" data-filter="tutti" aria-pressed="true">Tutti i lavori</button>
      <button type="button" data-filter="interazione" aria-pressed="false">Interazione e prodotto</button>
      <button type="button" data-filter="grafica" aria-pressed="false">Grafica e comunicazione</button>
      <button type="button" data-filter="branding" aria-pressed="false">Identità visiva</button>
    </div><p class="filter-status" data-filter-status role="status" aria-live="polite">8 progetti · Tutti i lavori</p>'''
    content += cards(PROJECTS) + '</div>'
    page('portfolio.html', 'Portfolio', 'Esplora i progetti di Michele Rinaldi: interaction design, prodotti, branding, manifesti e comunicazione visiva.', content, 'portfolio')


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
                ('Figma · 27 maggio – 14 giugno 2024', ['experience_period1_para']),
                ('Flutter · 9 – 20 settembre 2024', ['experience_period2_para']),
                ('SMAU · 29 ottobre 2024', ['experience_period3_para1', 'experience_period3_para2', 'experience_period3_para3', 'experience_period3_para4']),
                ('Riflessioni e ringraziamenti', ['review_para1', 'review_para2', 'review_thanks_lead', 'review_thanks_para', 'review_final_thanks', 'review_sign_off'])]:
                text = ''.join(ARCHIVE['syeew'].get(key, '') for key in keys)
                content += f'<details class="archive-entry"><summary><h3>{title}</h3></summary><div class="prose">{text}</div></details>'
            content += '</div></section>'
            content += '<div class="image-grid">' + ''.join(picture(f'syeew_smau_{i}.jpg', f'SMAU Milano 2024 — foto {i}') for i in range(1, 4)) + '</div>'
        if links:
            content += '<section class="case-section"><h2>Esplora il progetto</h2><div>' + resources(links) + '</div></section>'
        following = PROJECTS[(index + 1) % len(PROJECTS)]
        content += f'<nav class="next-project" aria-label="Progetto successivo"><span>Continua a esplorare</span><a href="{project_url(following)}">{esc(following["title"])} ↗</a></nav></article>'
        page(project_url(project), project['title'], project['summary'], content, 'portfolio')


def about():
    content = '<div class="wrap">' + heading('Chi sono', 'Il filo comune?<br><em>La curiosità.</em>')
    content += '''<div class="portrait-layout"><img class="portrait" src="assets/images/previews/foto_RinaldiMichele_1.webp" alt="Michele Rinaldi" width="900" height="1200"><div class="prose"><p>Sono Michele, vengo da Cupramontana e mi piace costruire cose. Ho cominciato con i video, ho scelto l’informatica e mi sono avvicinato al design sperimentando con Photoshop, Figma e Fusion 360.</p><p>Per me il codice dà struttura alle idee. Il design mi aiuta a chiedermi quali idee valga la pena costruire e come renderle comprensibili alle persone.</p><p>L’esperienza in SYEEW e i primi progetti universitari hanno dato una direzione a questa curiosità: l’Interaction Design, dove tecnologia, creatività e attenzione alle persone si incontrano.</p><a class="text-link" href="portfolio.html">Guarda cosa progetto ↗</a></div></div>
    <section class="case-section"><h2>Prima delle interfacce,<br>i video.</h2><div class="prose"><p>Il 10 agosto 2015, a nove anni, ho pubblicato il mio primo video. Nei tre anni successivi ne ho realizzati 213: gameplay, curiosità storiche con mio fratello, magie, esperimenti e tutorial.</p><p>Mi occupavo di tutto, dal montaggio alle grafiche, imparando da solo. È stato il primo modo che ho trovato per unire racconto, tecnologia e un progetto tutto mio.</p></div></section>
    <section class="portrait-layout"><div class="prose"><span class="eyebrow">Fuori dallo schermo</span><h2 class="contact-title">Sempre a<br><em>tempo mio.</em></h2><p>Studio musica da quando avevo quattro anni e suono la batteria da quando ne avevo sei. Faccio parte del Corpo Bandistico Don N. Bonanni di Cupramontana.</p><p>Ho affiancato gli insegnanti nei corsi musicali e nei centri estivi, lavorando con bambini e ragazzi. Insegnare percussioni mi ha fatto scoprire un altro modo di condividere quello che mi appassiona.</p></div><img src="assets/images/previews/foto_RinaldiMichele_3.webp" alt="Michele durante un’esibizione con il corpo bandistico" loading="lazy" width="720" height="960"></section>'''
    content += contact_band() + '</div>'
    page('chi-sono.html', 'Chi sono', 'La storia di Michele Rinaldi, tra informatica, interaction design, video e musica.', content, 'about')


def journey():
    content = '<div class="wrap">' + heading('Percorso / Appunti e archivio', 'Le cose che mi hanno<br>portato <em>fin qui.</em>', 'La formazione, le esperienze e i lavori che fanno da sfondo al portfolio. Il sito è nato per la maturità del 2025 e continua a evolversi insieme a me.')
    content += '''<div class="timeline">
    <div class="timeline-item"><span>Università</span><div><h3>Interaction Design · Politecnico di Milano</h3><p>Il percorso a Lecco e i primi progetti di gruppo, come Night Train Ride: progettare l’incontro tra persone e tecnologia.</p></div></div>
    <div class="timeline-item"><span>2024 · Esperienza sul campo</span><div><h3>SYEEW · Dal mockup all’app</h3><p>Il PCTO tra Figma, design system e Flutter. Un primo confronto con la progettazione dentro un team.</p><a class="text-link" href="pcto.html">Leggi il caso studio ↗</a></div></div>
    <div class="timeline-item"><span>Scuola · Esame 2024/2025</span><div><h3>Informatica · IIS Marconi Pieralisi</h3><p>Programmazione, sistemi, intelligenza artificiale, ma anche cultura umanistica e cittadinanza. Le basi da cui è partito questo sito.</p></div></div>
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
    titles = {'areatecnica.html': ('Area tecnica', 'Programmare, sperimentare, capire.'),
              'areaumanistica.html': ('Area umanistica', 'Storie, idee e memoria.'),
              'educazionecivica.html': ('Educazione civica', 'Uno sguardo sul mondo.')}
    for filename, (title, subtitle) in titles.items():
        content = '<div class="wrap archive-page"><a class="back-link" href="percorso.html">← Percorso e archivio</a>'
        content += heading('Archivio scolastico · Esame 2024/2025', esc(title), subtitle)
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
    content = '<article class="wrap archive-page"><a class="back-link" href="areaumanistica.html">← Area umanistica</a>' + heading('Archivio · Capolavoro 2025', 'Il Nazismo nel<br>contesto del ’900', 'Ricerca, memoria e responsabilità. Il capolavoro presentato per l’Esame di Stato.')
    for entry in ARCHIVE['capolavoro']:
        content += f'<section class="case-section"><h2>{esc(entry["title"])}</h2><div class="prose">' + ''.join(entry['body']) + '</div></section>'
    content += resources(ARCHIVE['capolavoro_links'])
    content += '<section class="case-section"><h2>Gruppo di lavoro</h2><p>Michele Rinaldi, Luca Andreoni, Lorenzo Romagnoli, Riccardo Sabbatini Peverieri.</p></section></article>'
    page('RinaldiMichele_Capolavoro1.html', 'Il capolavoro', 'Il capolavoro di Michele Rinaldi: il Nazismo nel contesto del Novecento.', content, 'journey')


def contact():
    content = '''<div class="wrap contact-layout"><section class="contact-copy"><span class="eyebrow">Contatti</span><h1 class="contact-title">Facciamo<br>due <em>parole.</em></h1><p>Un progetto da immaginare insieme, un’idea da confrontare o semplicemente un saluto. Scrivimi qui.</p><a class="text-link" href="portfolio.html">Prima, dai un’occhiata ai lavori ↗</a></section>
    <form class="contact-form" action="https://formspree.io/f/xovwnrjq" method="post">
      <label for="name">Come ti chiami?</label><input id="name" name="name" autocomplete="name" placeholder="Il tuo nome" required maxlength="150">
      <label for="email">Dove posso risponderti?</label><input id="email" name="email" type="email" autocomplete="email" placeholder="La tua email" required maxlength="254">
      <label for="message">Cosa hai in mente?</label><textarea id="message" name="message" placeholder="Raccontami la tua idea…" required maxlength="10000"></textarea>
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
