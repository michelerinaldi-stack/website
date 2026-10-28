#!/usr/bin/env python3
"""Check static pages, local links, fragments and source consistency."""
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links, self.errors = set(), [], []
        self.headings = 0
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append(f'Duplicate ID: {attrs["id"]}')
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.headings += 1
        if tag == 'img' and 'alt' not in attrs:
            self.errors.append('Image without alt attribute')
        for candidate in attrs.get('srcset', '').split(','):
            if candidate.strip():
                self.links.append(candidate.strip().split()[0])
        if attrs.get('data-original'):
            self.links.append(attrs['data-original'])
        for key in ('href', 'src', 'action'):
            if attrs.get(key):
                self.links.append(attrs[key])
        if tag == 'style' or (tag == 'script' and 'src' not in attrs):
            self.errors.append('Inline script/style instead of shared files')


def main():
    subprocess.run([sys.executable, str(ROOT / 'scripts/build.py'), '--check'], check=True)
    pages = {path.resolve(): Page(path) for path in ROOT.glob('*.html')}
    errors = []
    for path, page in pages.items():
        errors.extend(f'{path.name}: {error}' for error in page.errors)
        if page.headings != 1:
            errors.append(f'{path.name}: expected exactly one h1')
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.exists():
                errors.append(f'{path.name}: missing local target {link}')
            if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f'{path.name}: missing fragment {link}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Checked {len(pages)} pages: local links, fragments, images and shared resources OK.')


if __name__ == '__main__':
    main()
