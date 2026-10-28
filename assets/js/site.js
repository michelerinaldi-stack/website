// Progressive enhancement: links, content and forms work without JavaScript.
const filters = document.querySelector('[data-project-filters]');
if (filters) {
  const cards = [...document.querySelectorAll('[data-category]')];
  const status = document.querySelector('[data-filter-status]');
  filters.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-filter]');
    if (!button) return;
    const category = button.dataset.filter;
    document.querySelector('.portfolio-board')?.classList.toggle('is-filtered', category !== 'tutti');
    for (const control of filters.querySelectorAll('button')) {
      control.setAttribute('aria-pressed', String(control === button));
    }
    for (const card of cards) {
      card.hidden = category !== 'tutti' && card.dataset.category !== category;
    }
    const count = cards.filter((card) => !card.hidden).length;
    status.textContent = `${button.dataset.label || button.textContent.trim()}: ${count} progetti`;
  });
  filters.hidden = false;
}

const lightbox = document.querySelector('.lightbox');
if (lightbox && typeof lightbox.showModal === 'function') {
  const image = lightbox.querySelector('img');
  const caption = lightbox.querySelector('figcaption');
  const close = () => lightbox.close();
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[data-lightbox]');
    if (!link) return;
    event.preventDefault();
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    caption.textContent = image.alt;
    lightbox.showModal();
  });
  lightbox.querySelector('button').addEventListener('click', close);
  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox) close();
  });
  lightbox.addEventListener('close', () => image.removeAttribute('src'));
}
