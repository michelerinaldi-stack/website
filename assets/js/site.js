// Progressive enhancement: content, links and native details work without JS.
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
const animate = (element, frames, options = {}) => {
  if (reducedMotion.matches || !element.animate) return null;
  return element.animate(frames, {
    duration: 360, easing: 'cubic-bezier(.2,.75,.25,1)', ...options,
  });
};

// Animate the new positions, rather than delaying which results are visible.
const filters = document.querySelector('[data-project-filters]');
if (filters) {
  const cards = [...document.querySelectorAll('[data-category]')];
  const status = document.querySelector('[data-filter-status]');
  filters.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-filter]');
    if (!button || button.getAttribute('aria-pressed') === 'true') return;
    const positions = new Map(cards.filter((card) => !card.hidden)
      .map((card) => [card, card.getBoundingClientRect()]));
    cards.forEach((card) => card.getAnimations().forEach((animation) => animation.cancel()));
    const category = button.dataset.filter;
    document.querySelector('.portfolio-board')?.classList.toggle('is-filtered', category !== 'tutti');
    for (const control of filters.querySelectorAll('button')) {
      control.setAttribute('aria-pressed', String(control === button));
    }
    for (const card of cards) card.hidden = category !== 'tutti' && card.dataset.category !== category;
    const visible = cards.filter((card) => !card.hidden);
    for (const card of visible) {
      const before = positions.get(card);
      const after = card.getBoundingClientRect();
      const nearby = before && before.bottom > 0 && before.top < innerHeight
        && Math.abs(before.top - after.top) < innerHeight * .75;
      const from = nearby
        ? { transform: `translate(${before.left - after.left}px, ${before.top - after.top}px)` }
        : { opacity: 0, transform: 'translateY(18px)' };
      const motion = animate(card, [from, { opacity: 1, transform: 'none' }], { duration: 430 });
      motion?.finished.then(updateProgress).catch(() => {});
    }
    animate(button, [{ opacity: .5 }, { opacity: 1 }], { duration: 220 });
    status.textContent = `${button.dataset.label || button.textContent.trim()}: ${visible.length} progetti`;
    requestAnimationFrame(updateProgress);
  });
  filters.hidden = false;
}

// Keep native focus, Escape and original-image links; enhance with navigation.
const lightbox = document.querySelector('.lightbox');
if (lightbox && typeof lightbox.showModal === 'function') {
  const image = lightbox.querySelector('img');
  const caption = lightbox.querySelector('figcaption');
  const original = lightbox.querySelector('[data-gallery-original]');
  const controls = lightbox.querySelector('.lightbox-controls');
  const count = lightbox.querySelector('[data-gallery-count]');
  let links = [];
  let index = 0;
  const showImage = (next, direction = 1) => {
    index = (next + links.length) % links.length;
    const link = links[index];
    const src = link.href;
    image.getAnimations().forEach((animation) => animation.cancel());
    image.classList.add('is-loading');
    original.href = link.dataset.original || src;
    original.hidden = false;
    image.src = src;
    image.alt = link.querySelector('img').alt;
    caption.textContent = image.alt;
    count.textContent = `${index + 1} / ${links.length}`;
    controls.hidden = links.length < 2;
    image.decode().catch(() => {}).then(() => {
      if (image.src !== src || !lightbox.open) return;
      image.classList.remove('is-loading');
      animate(image, [{ opacity: .4, transform: `translateX(${direction * 18}px)` },
        { opacity: 1, transform: 'none' }], { duration: 240 });
    });
  };
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[data-lightbox]');
    if (!link) return;
    event.preventDefault();
    const group = link.closest('.portfolio-gallery, .image-grid') || document;
    links = [...group.querySelectorAll('a[data-lightbox]')].filter((item) => item.getClientRects().length);
    lightbox.showModal();
    showImage(links.indexOf(link));
  });
  lightbox.querySelector('.lightbox-close').addEventListener('click', () => lightbox.close());
  lightbox.querySelector('[data-gallery-prev]').addEventListener('click', () => showImage(index - 1, -1));
  lightbox.querySelector('[data-gallery-next]').addEventListener('click', () => showImage(index + 1));
  lightbox.addEventListener('keydown', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey || links.length < 2) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      const direction = event.key === 'ArrowLeft' ? -1 : 1;
      showImage(index + direction, direction);
    }
  });
  let touchStart = null;
  lightbox.querySelector('figure').addEventListener('touchstart', (event) => {
    touchStart = event.touches.length === 1 ? event.touches[0] : null;
  }, { passive: true });
  lightbox.querySelector('figure').addEventListener('touchend', (event) => {
    if (!touchStart || links.length < 2) return;
    const end = event.changedTouches[0];
    const dx = end.clientX - touchStart.clientX;
    const dy = end.clientY - touchStart.clientY;
    touchStart = null;
    if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy) * 1.4) {
      const direction = dx < 0 ? 1 : -1;
      showImage(index + direction, direction);
    }
  }, { passive: true });
  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox) lightbox.close();
  });
  lightbox.addEventListener('close', () => {
    image.getAnimations().forEach((animation) => animation.cancel());
    image.removeAttribute('src');
    original.hidden = true;
    image.classList.remove('is-loading');
    touchStart = null;
  });
}

// Animate open/close without replacing the accessible native details control.
const detailAnimations = new Map();
for (const details of document.querySelectorAll('.work-details, .archive-entry')) {
  details.querySelector('summary').addEventListener('click', (event) => {
    if (reducedMotion.matches || !details.animate) return;
    event.preventDefault();
    const current = details.getBoundingClientRect().height;
    const previous = detailAnimations.get(details);
    const opening = previous ? !previous.opening : !details.open;
    previous?.animation.cancel();
    details.open = true;
    const style = getComputedStyle(details);
    const closed = details.querySelector('summary').offsetHeight
      + parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
    const target = opening ? details.getBoundingClientRect().height : closed;
    details.classList.add('is-animating');
    const animation = animate(details, [{ height: `${current}px` }, { height: `${target}px` }], { duration: 280 });
    detailAnimations.set(details, { animation, opening });
    animation.finished.then(() => {
      if (detailAnimations.get(details)?.animation !== animation) return;
      details.open = opening;
      details.classList.remove('is-animating');
      detailAnimations.delete(details);
      updateProgress();
    }).catch(() => {});
  });
}

// Pointer effects use one frame per pointer update and never move the hit area.
for (const plane of document.querySelectorAll('.folio-stage, .project-visual, .portfolio-gallery a')) {
  let frame = 0;
  plane.classList.add('motion-plane');
  const reset = () => {
    cancelAnimationFrame(frame);
    frame = 0;
    plane.style.removeProperty('--tilt-x');
    plane.style.removeProperty('--tilt-y');
    plane.style.removeProperty('--image-scale');
    plane.classList.remove('is-tracking');
  };
  plane.addEventListener('pointermove', (event) => {
    if (!finePointer.matches || reducedMotion.matches) return;
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      const rect = plane.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - .5;
      const y = (event.clientY - rect.top) / rect.height - .5;
      plane.style.setProperty('--tilt-x', `${-y * 5}deg`);
      plane.style.setProperty('--tilt-y', `${x * 5}deg`);
      plane.style.setProperty('--image-scale', '1.025');
      plane.style.setProperty('--hint-x', `${Math.max(12, Math.min(rect.width - 135, event.clientX - rect.left + 18))}px`);
      plane.style.setProperty('--hint-y', `${Math.max(12, Math.min(rect.height - 45, event.clientY - rect.top + 18))}px`);
      plane.classList.add('is-tracking');
    });
  });
  plane.addEventListener('pointerleave', reset);
  plane.addEventListener('pointercancel', reset);
  reducedMotion.addEventListener('change', reset);
}

for (const button of document.querySelectorAll('.round-link, .folio-open')) {
  button.classList.add('magnetic-link');
  const icon = document.createElement('span');
  icon.className = 'magnetic-icon';
  icon.setAttribute('aria-hidden', 'true');
  icon.textContent = button.textContent;
  button.replaceChildren(icon);
  button.addEventListener('pointermove', (event) => {
    if (!finePointer.matches || reducedMotion.matches) return;
    const rect = button.getBoundingClientRect();
    button.style.setProperty('--magnet-x', `${(event.clientX - rect.left - rect.width / 2) * .18}px`);
    button.style.setProperty('--magnet-y', `${(event.clientY - rect.top - rect.height / 2) * .18}px`);
  });
  const reset = () => {
    button.style.removeProperty('--magnet-x');
    button.style.removeProperty('--magnet-y');
  };
  button.addEventListener('pointerleave', reset);
  button.addEventListener('pointercancel', reset);
  reducedMotion.addEventListener('change', reset);
}

// Preserve each font's ligatures: play with whole typographic fragments.
for (const heading of document.querySelectorAll('.hero h1, .portfolio-masthead h1')) {
  const copy = heading.cloneNode(true);
  copy.querySelectorAll('[aria-hidden]').forEach((node) => node.remove());
  copy.querySelectorAll('br').forEach((node) => node.replaceWith(' '));
  heading.setAttribute('aria-label', copy.textContent.replace(/\s+/g, ' ').trim());
  const walker = document.createTreeWalker(heading, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) {
    if (walker.currentNode.textContent.trim() && !walker.currentNode.parentElement.closest('[aria-hidden], .hero-period')) {
      nodes.push(walker.currentNode);
    }
  }
  nodes.forEach((node, i) => {
    const word = document.createElement('span');
    word.className = 'type-word';
    word.setAttribute('aria-hidden', 'true');
    word.textContent = node.textContent;
    node.replaceWith(word);
    const play = () => {
      word.getAnimations().forEach((animation) => animation.cancel());
      animate(word, [{ transform: 'none' }, { transform: `translateY(-7px) rotate(${i % 2 ? 1.5 : -1.5}deg)` },
        { transform: 'none' }], { duration: 620 });
    };
    word.addEventListener('pointerenter', (event) => { if (event.pointerType !== 'touch') play(); });
    word.addEventListener('pointerdown', (event) => { if (event.pointerType === 'touch') play(); });
  });
}

// Content is visible by default; reveal animation is optional and runs once.
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      observer.unobserve(entry.target);
      if (entry.target.getAnimations().length) continue;
      animate(entry.target, [{ opacity: .15, transform: 'translateY(22px)' },
        { opacity: 1, transform: 'none' }], { duration: 550 });
    }
  }, { threshold: .06 });
  for (const element of document.querySelectorAll('.folio-work:not(.folio-collection), .collection-header, .portfolio-gallery a, .about-strip, .case-section')) {
    if (element.getBoundingClientRect().top > innerHeight * .95) observer.observe(element);
  }
}

const progress = document.createElement('div');
progress.className = 'scroll-progress';
progress.setAttribute('aria-hidden', 'true');
const toTop = document.createElement('a');
toTop.className = 'to-top';
toTop.href = '#contenuto';
toTop.setAttribute('aria-label', 'Torna all’inizio');
toTop.textContent = '↑';
toTop.hidden = true;
toTop.addEventListener('click', (event) => {
  event.preventDefault();
  window.scrollTo({ top: 0, behavior: reducedMotion.matches ? 'instant' : 'smooth' });
  const target = document.querySelector('.signature');
  target.focus({ preventScroll: true });
});
document.body.append(progress, toTop);
let scrollFrame = 0;
const updateProgress = () => {
  scrollFrame = 0;
  const distance = document.documentElement.scrollHeight - innerHeight;
  progress.style.setProperty('--scroll', distance > 0 ? Math.min(1, Math.max(0, scrollY / distance)) : 0);
  toTop.hidden = scrollY < innerHeight;
};
window.addEventListener('scroll', () => {
  if (!scrollFrame) scrollFrame = requestAnimationFrame(updateProgress);
}, { passive: true });
window.addEventListener('resize', updateProgress);
updateProgress();
reducedMotion.addEventListener('change', () => {
  if (!reducedMotion.matches) return;
  for (const [details, state] of detailAnimations) {
    state.animation.cancel();
    details.open = state.opening;
    details.classList.remove('is-animating');
  }
  detailAnimations.clear();
  document.getAnimations().forEach((animation) => animation.cancel());
});

// Inline story annotations: hover, keyboard focus or a tap on the same words.
const storyWords = [...document.querySelectorAll('[data-story-effect]')];
if (storyWords.length) {
  const annotation = document.createElement('aside');
  annotation.id = 'story-annotation';
  annotation.className = 'story-annotation';
  annotation.hidden = true;
  const fragments = {
    code: '<span class="story-annotation-label">Informatica / Ciao, mondo</span><pre class="story-code"><b>function</b> saluta(nome) {\n  <b>return</b> `Ciao, ${nome}!`;\n}\nsaluta("Michele");</pre>',
    music: '<span class="story-annotation-label">Musica / Un piccolo ritmo</span><div class="story-equalizer" aria-hidden="true">' + [15, 29, 20, 40, 25, 34, 17, 28, 13].map((h) => `<i style="--bar-height:${h}px"></i>`).join('') + '</div><div class="story-beat"><span>4/4</span><span>1 &nbsp; 2 &nbsp; 3 &nbsp; 4</span></div>',
    design: '<span class="story-annotation-label">Design / Prove in Figma</span><div class="story-design"><em>Michele</em></div><div class="story-swatches" aria-hidden="true"><i></i><i></i><i></i></div>',
  };
  document.body.append(annotation);
  let active = null;
  let pinned = false;
  let closeTimer;
  const close = () => {
    clearTimeout(closeTimer);
    active?.setAttribute('aria-expanded', 'false');
    active = null;
    pinned = false;
    annotation.hidden = true;
    annotation.getAnimations({ subtree: true }).forEach((motion) => motion.cancel());
  };
  const position = () => {
    if (!active) return;
    const word = active.getBoundingClientRect();
    annotation.hidden = word.bottom < 0 || word.top > innerHeight;
    if (annotation.hidden) return;
    const box = annotation.getBoundingClientRect();
    annotation.style.left = `${Math.min(innerWidth - box.width - 16, Math.max(16, word.left))}px`;
    const below = word.bottom + 10;
    annotation.style.top = `${below + box.height < innerHeight - 16 ? below : Math.max(16, word.top - box.height - 10)}px`;
  };
  const show = (button) => {
    clearTimeout(closeTimer);
    if (active === button) return;
    close();
    active = button;
    annotation.dataset.kind = button.dataset.storyEffect;
    annotation.innerHTML = fragments[button.dataset.storyEffect];
    annotation.setAttribute('aria-label', `Appunto su ${button.textContent}`);
    annotation.hidden = false;
    button.setAttribute('aria-expanded', 'true');
    position();
    animate(annotation, [{ opacity: 0, transform: 'translateY(4px)' }, { opacity: 1, transform: 'none' }], { duration: 180 });
    annotation.querySelectorAll('.story-equalizer i').forEach((bar, i) => {
      animate(bar, [{ transform: 'scaleY(.4)' }, { transform: 'scaleY(1)' }, { transform: 'scaleY(.55)' }, { transform: 'scaleY(1)' }], { duration: 500 + i * 35, iterations: 2 });
    });
    const sample = annotation.querySelector('.story-design em');
    if (sample) animate(sample, [{ transform: 'rotate(-3deg)' }, { transform: 'rotate(1deg)' }, { transform: 'none' }], { duration: 430 });
    const code = annotation.querySelector('.story-code');
    if (code) animate(code, [{ opacity: .2 }, { opacity: 1 }], { duration: 450 });
  };
  const scheduleClose = () => {
    clearTimeout(closeTimer);
    if (!pinned) closeTimer = setTimeout(close, 180);
  };
  for (const word of storyWords) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'story-word';
    button.dataset.storyEffect = word.dataset.storyEffect;
    button.dataset.label = word.textContent;
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-controls', annotation.id);
    const label = document.createElement('span');
    label.textContent = word.textContent;
    button.append(label);
    word.replaceWith(button);
    button.addEventListener('pointerenter', (event) => {
      if (event.pointerType !== 'touch') show(button);
    });
    button.addEventListener('pointerleave', scheduleClose);
    button.addEventListener('focus', () => requestAnimationFrame(() => {
      if (document.activeElement === button) show(button);
    }));
    button.addEventListener('blur', scheduleClose);
    button.addEventListener('click', () => {
      if (active === button && pinned) close();
      else { show(button); pinned = true; }
    });
  }
  annotation.addEventListener('pointerenter', () => clearTimeout(closeTimer));
  annotation.addEventListener('pointerleave', scheduleClose);
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') close(); });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.story-word, .story-annotation')) close();
  });
  window.addEventListener('scroll', () => {
    if (active === document.activeElement) position();
    else close();
  }, { passive: true });
  window.addEventListener('resize', close);
}
