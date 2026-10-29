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

// Each story detail has a specific response; all decorative content is hidden from AT.
const storySvg = (body, viewBox = '0 0 100 10') => `<svg viewBox="${viewBox}" fill="none" stroke="currentColor" stroke-width="1" aria-hidden="true">${body}</svg>`;
const storyMarks = {
  record: '<i></i>', timeline: '<i></i>', terminal: 'print("Ciao!");', braces: '<span>{</span><span>}</span>',
  brush: '<i></i>', rewind: '', volume: '', selection: '<i></i>'.repeat(4),
  network: storySvg('<path d="M3 5H97" opacity=".3"/><circle cx="3" cy="5" r="2"/><circle cx="50" cy="5" r="2"/><circle cx="97" cy="5" r="2"/><circle class="spark-packet" cx="3" cy="5" r="1.5" fill="currentColor"/>'),
  ballot: storySvg('<rect x="1" y="1" width="8" height="8"/><path class="spark-check" d="m3 4 2 2 6-6"/>','0 0 13 10'),
  podium: '<i></i>'.repeat(3), equalizer: '<i></i>'.repeat(9),
  live: storySvg('<path d="M12 8q3-5 6 0M8 8q7-11 14 0M4 8q11-16 22 0"/>','0 0 30 10'),
  drums: '<i></i>'.repeat(4), metronome: storySvg('<path d="m4 9 4-8 4 8Z" opacity=".3"/><path class="spark-pendulum" d="M8 9V0"/>','0 0 16 10'),
  interaction: storySvg('<path d="M1 0v8l2-2 2 3 1-1-2-3h3Z" fill="currentColor"/>','0 0 8 10'),
  waiting: '<i></i>'.repeat(3), settle: storySvg('<path d="M0 5q12-6 25 0t25 0t25 0t25 0"/>'), build: '<i></i>'.repeat(3),
};
for (const word of document.querySelectorAll('.story-spark')) {
  const text = word.textContent;
  const kind = word.dataset.spark;
  const copy = document.createElement('span'); copy.className = 'spark-copy'; copy.textContent = text;
  const space = document.createElement('span'); space.className = 'spark-space'; space.textContent = text; space.setAttribute('aria-hidden', 'true');
  const mark = document.createElement('span'); mark.className = 'spark-mark'; mark.setAttribute('aria-hidden', 'true');
  if (kind === 'terminal') { mark.classList.add('spark-trace'); mark.textContent = storyMarks[kind]; }
  else mark.innerHTML = storyMarks[kind] || '';
  word.replaceChildren(copy, space, mark); word.classList.add('is-ready');
  if (kind === 'together') {
    copy.setAttribute('aria-hidden', 'true');
    const readable = document.createElement('span'); readable.className = 'spark-readable'; readable.textContent = text; word.append(readable);
    copy.replaceChildren(...[...text].map((letter) => {
      const span = document.createElement('span'); span.className = 'spark-letter'; span.textContent = letter; return span;
    }));
  }
  const counter = document.createElement('span');
  if (kind === 'counter') { counter.className = 'spark-counter'; counter.setAttribute('aria-hidden', 'true'); word.append(counter); }
  let timers = [], motions = [], touch = null;
  const reset = () => {
    timers.forEach(clearTimeout); timers = [];
    word.classList.remove('is-active');
    motions.forEach((motion) => motion.cancel()); motions = [];
    word.style.removeProperty('--cursor-x');
  };
  const motion = (element, frames, duration = 600, delay = 0) => {
    if (!element) return;
    const animation = animate(element, frames, { duration, delay, fill: word.contains(element) ? 'both' : 'none' });
    if (animation) motions.push(animation);
  };
  const play = () => {
    reset(); word.classList.add('is-active');
    const bars = [...mark.querySelectorAll('i')];
    switch (kind) {
      case 'record': motion(bars[0], [{ opacity: .3 }, { opacity: 1 }, { opacity: .3 }, { opacity: 1 }], 900); break;
      case 'counter':
        counter.textContent = text;
        if (!reducedMotion.matches) ['000,', '071,', '142,', text].forEach((value, i) => timers.push(setTimeout(() => { counter.textContent = value; }, i * 85)));
        break;
      case 'timeline': motion(bars[0], [{ transform: 'translateX(0)' }, { transform: `translateX(${word.offsetWidth - 1}px)` }], 800); break;
      case 'terminal': motion(mark, [{ clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0 0 0)' }], 400); break;
      case 'braces': motion(mark, [{ transform: 'scaleX(.8)' }, { transform: 'scaleX(1)' }], 300); break;
      case 'brush':
        motion(bars[0], [{ clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0 0 0)' }]);
        motion(document.querySelector('.story-portrait img'), [{ filter: 'grayscale(1)' }, { filter: 'grayscale(0)' }], 800); break;
      case 'rewind': motion(mark, [{ transform: 'scaleX(1)' }, { transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], 650); break;
      case 'volume': motion(copy, [{ transform: 'none' }, { transform: 'translate(-1px,-1px)' }, { transform: 'none' }]); break;
      case 'selection': motion(mark, [{ opacity: 0 }, { opacity: .8 }], 180); break;
      case 'network': motion(mark.querySelector('.spark-packet'), [{ transform: 'translateX(0)' }, { transform: 'translateX(94px)' }], 800); break;
      case 'ballot': motion(mark.querySelector('.spark-check'), [{ strokeDasharray: '14', strokeDashoffset: '14' }, { strokeDasharray: '14', strokeDashoffset: '0' }], 350); break;
      case 'podium': motion(bars[2], [{ transform: 'scaleY(0)' }, { transform: 'scaleY(1)' }], 350); break;
      case 'equalizer': bars.forEach((bar, i) => motion(bar, [{ transform: 'scaleY(.5)' }, { transform: `scaleY(${i % 3 + 1})` }, { transform: 'scaleY(1)' }], 400, i * 30)); break;
      case 'live': [...mark.querySelectorAll('path')].forEach((arc, i) => motion(arc, [{ opacity: 0 }, { opacity: 1 }, { opacity: .2 }], 550, i * 100)); break;
      case 'drums': bars.forEach((bar, i) => motion(bar, [{ transform: 'scale(.6)', opacity: .3 }, { transform: 'scale(1.35)', opacity: 1 }, { transform: 'scale(1)', opacity: .6 }], 180, i * 180)); break;
      case 'metronome': motion(mark.querySelector('.spark-pendulum'), [{ transform: 'rotate(-24deg)' }, { transform: 'rotate(24deg)' }, { transform: 'rotate(-24deg)' }, { transform: 'none' }], 1000); break;
      case 'together': [...copy.children].forEach((letter, i) => motion(letter, [{ transform: `translateX(${(i - 3) * 1.3}px)` }, { transform: 'none' }], 450)); break;
      case 'interaction': motion(mark, [{ opacity: 0 }, { opacity: .8 }], 180); break;
      case 'waiting': bars.forEach((dot, i) => motion(dot, [{ opacity: .15 }, { opacity: 1 }, { opacity: .15 }], 550, i * 140)); break;
      case 'leap': motion(copy, [{ transform: 'none' }, { transform: 'translateY(-4px) rotate(-2deg)', offset: .35 }, { transform: 'none' }], 500); break;
      case 'settle': motion(mark, [{ transform: 'scaleY(1)' }, { transform: 'scaleY(.15)' }], 950); break;
      case 'build': bars.forEach((block, i) => motion(block, [{ opacity: 0, transform: 'translateY(-3px)' }, { opacity: 1, transform: 'none' }], 250, i * 160)); break;
    }
    timers.push(setTimeout(reset, 1600));
  };
  word.addEventListener('pointerenter', (event) => { if (event.pointerType !== 'touch') play(); });
  word.addEventListener('pointermove', (event) => {
    if (kind !== 'interaction' || reducedMotion.matches || event.pointerType === 'touch') return;
    word.style.setProperty('--cursor-x', `${Math.max(0, Math.min(word.offsetWidth - 8, event.clientX - word.getBoundingClientRect().left))}px`);
  });
  word.addEventListener('pointerleave', (event) => { if (event.pointerType !== 'touch') reset(); });
  word.addEventListener('pointerdown', (event) => { if (event.pointerType === 'touch') touch = { x: event.clientX, y: event.clientY }; });
  word.addEventListener('pointerup', (event) => {
    if (touch && Math.hypot(event.clientX - touch.x, event.clientY - touch.y) < 10) play(); touch = null;
  });
  word.addEventListener('pointercancel', () => { touch = null; reset(); });
  reducedMotion.addEventListener('change', reset);
}
