// The desk and typography lab are optional views; the editorial portfolio is the fallback.
(() => {
  const modes = document.querySelector('[data-portfolio-modes]');
  const desk = document.querySelector('[data-play-desk]');
  const board = document.querySelector('.portfolio-board');
  if (!modes || !desk || !board) return;
  const canvas = desk.querySelector('[data-play-canvas]');
  const cards = [...canvas.querySelectorAll('.play-card')];
  const status = desk.querySelector('[data-desk-status]');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const states = new Map(cards.map(card => [card, { x: 0, y: 0, angle: 0 }]));
  let active = false;
  let selected = null;
  let layer = 0;
  const clamp = (value, min, max) => Math.min(Math.max(min, max), Math.max(min, value));
  const visible = () => cards.filter(card => !card.hidden);
  const place = (card, state, animated = false) => {
    const before = getComputedStyle(card).transform;
    card.getAnimations().forEach(animation => animation.cancel());
    const angle = state.angle * Math.PI / 180;
    const rotatedWidth = Math.abs(card.offsetWidth * Math.cos(angle)) + Math.abs(card.offsetHeight * Math.sin(angle));
    const rotatedHeight = Math.abs(card.offsetWidth * Math.sin(angle)) + Math.abs(card.offsetHeight * Math.cos(angle));
    const margin = Math.max(innerWidth < 540 ? 14 : 24, (rotatedWidth - card.offsetWidth) / 2 + 8);
    const verticalMargin = Math.max(innerWidth < 540 ? 14 : 24, (rotatedHeight - card.offsetHeight) / 2 + 8);
    state.x = clamp(state.x, margin, canvas.clientWidth - card.offsetWidth - margin);
    state.y = clamp(state.y, verticalMargin, canvas.clientHeight - card.offsetHeight - verticalMargin);
    states.set(card, state);
    card.style.setProperty('--card-x', `${state.x}px`);
    card.style.setProperty('--card-y', `${state.y}px`);
    card.style.setProperty('--card-angle', `${state.angle}deg`);
    if (animated && !reduced.matches) card.animate([
      { transform: before }, { transform: `translate(${state.x}px, ${state.y}px) rotate(${state.angle}deg)` },
    ], { duration: 450, easing: 'cubic-bezier(.2,.8,.2,1)' });
  };
  const select = card => {
    selected = card;
    for (const item of cards) {
      item.classList.toggle('is-selected', item === card);
      item.querySelector('.play-handle').setAttribute('aria-pressed', String(item === card));
    }
    card.style.zIndex = String(++layer);
  };
  const layout = (shuffle = false, animated = false) => {
    if (!active) return;
    const items = visible();
    const columns = canvas.clientWidth < 650 ? 2 : canvas.clientWidth < 1000 ? 3 : 4;
    const rows = Math.ceil(items.length / columns);
    for (const [index, card] of items.entries()) {
      const margin = innerWidth < 540 ? 18 : 28;
      const rangeX = Math.max(0, canvas.clientWidth - card.offsetWidth - margin * 2);
      const rangeY = Math.max(0, canvas.clientHeight - card.offsetHeight - margin * 2);
      const column = index % columns;
      const row = Math.floor(index / columns);
      const x = margin + (columns > 1 ? column / (columns - 1) : .5) * rangeX;
      const y = margin + (rows > 1 ? row / (rows - 1) : .4) * rangeY;
      place(card, {
        x: shuffle ? margin + Math.random() * rangeX : x,
        y: shuffle ? margin + Math.random() * rangeY : y,
        angle: shuffle ? Math.random() * 24 - 12 : (index % 2 ? 3 : -3),
      }, animated);
    }
    status.textContent = `${items.length} progetti sul tavolo.`;
  };
  const sync = () => {
    const category = document.querySelector('[data-filter][aria-pressed="true"]')?.dataset.filter || 'tutti';
    for (const card of cards) card.hidden = category !== 'tutti' && card.dataset.playCategory !== category;
    layout(false, true);
  };
  for (const button of modes.querySelectorAll('[data-mode]')) {
    button.addEventListener('click', () => {
      active = button.dataset.mode === 'desk';
      for (const control of modes.querySelectorAll('[data-mode]')) control.setAttribute('aria-pressed', String(control === button));
      board.hidden = active;
      desk.hidden = !active;
      if (active) sync();
      window.dispatchEvent(new Event('resize'));
    });
  }
  modes.hidden = false;
  // Put the alternative view beside the editorial board, before the lab.
  board.after(desk);
  document.querySelector('[data-project-filters]').addEventListener('click', event => {
    if (active && event.target.closest('[data-filter]')) sync();
  });
  desk.querySelector('[data-desk-shuffle]').addEventListener('click', () => layout(true, true));
  desk.querySelector('[data-desk-reset]').addEventListener('click', () => layout(false, true));
  for (const card of cards) {
    const handle = card.querySelector('.play-handle');
    let drag = null;
    handle.addEventListener('pointerdown', event => {
      if (event.button !== 0 || drag) return;
      const matrix = new DOMMatrixReadOnly(getComputedStyle(card).transform);
      const state = { x: matrix.e, y: matrix.f, angle: Math.atan2(matrix.b, matrix.a) * 180 / Math.PI };
      place(card, state);
      select(card);
      handle.focus({ preventScroll: true });
      drag = { pointer: event.pointerId, startX: event.clientX, startY: event.clientY, x: state.x, y: state.y };
      handle.setPointerCapture(event.pointerId);
      card.classList.add('is-dragging');
    });
    handle.addEventListener('pointermove', event => {
      if (!drag || drag.pointer !== event.pointerId) return;
      place(card, { ...states.get(card), x: drag.x + event.clientX - drag.startX, y: drag.y + event.clientY - drag.startY });
    });
    const release = () => { drag = null; card.classList.remove('is-dragging'); };
    handle.addEventListener('pointerup', release);
    handle.addEventListener('pointercancel', release);
    handle.addEventListener('lostpointercapture', release);
    handle.addEventListener('focus', () => select(card));
    handle.addEventListener('keydown', event => {
      const arrows = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
      const delta = arrows[event.key];
      if (!delta && event.key.toLowerCase() !== 'r') return;
      event.preventDefault();
      select(card);
      const state = { ...states.get(card) };
      if (delta) { state.x += delta[0] * (event.shiftKey ? 35 : 12); state.y += delta[1] * (event.shiftKey ? 35 : 12); }
      else state.angle = (state.angle + (event.shiftKey ? -8 : 8)) % 360;
      place(card, state);
    });
  }
  if ('ResizeObserver' in window) new ResizeObserver(() => layout()).observe(canvas);
  else window.addEventListener('resize', () => layout());
  reduced.addEventListener('change', () => { if (reduced.matches) cards.forEach(card => card.getAnimations().forEach(a => a.cancel())); });

  const lab = document.querySelector('[data-type-lab]');
  const paper = lab.querySelector('[data-type-paper]');
  const sample = lab.querySelector('[data-type-sample]');
  const input = lab.querySelector('#type-text');
  const spacing = lab.querySelector('#type-spacing');
  const mix = lab.querySelector('[data-type-mix]');
  let mixed = false;
  let font = 'Manrope';
  const renderType = () => {
    const text = input.value || 'Aa';
    sample.setAttribute('aria-label', text);
    sample.replaceChildren(...Array.from(text).map(character => {
      const glyph = document.createElement('span');
      glyph.textContent = character === ' ' ? '\u00a0' : character;
      glyph.setAttribute('aria-hidden', 'true');
      if (mixed) {
        glyph.style.rotate = `${Math.random() * 30 - 15}deg`;
        glyph.style.translate = `0 ${Math.random() * 20 - 10}px`;
        glyph.style.fontFamily = Math.random() > .5 ? 'Instrument, Georgia, serif' : 'Manrope, sans-serif';
        glyph.style.fontStyle = glyph.style.fontFamily.startsWith('Instrument') ? 'italic' : 'normal';
      }
      return glyph;
    }));
    sample.style.fontFamily = font === 'Instrument' ? 'Instrument, Georgia, serif' : 'Manrope, sans-serif';
    sample.style.fontStyle = font === 'Instrument' ? 'italic' : 'normal';
    sample.style.letterSpacing = `${Number(spacing.value) / 100}em`;
  };
  input.addEventListener('input', renderType);
  spacing.addEventListener('input', renderType);
  mix.addEventListener('click', () => {
    mixed = !mixed;
    mix.setAttribute('aria-pressed', String(mixed));
    mix.textContent = mixed ? 'Ricomponi le lettere ↗' : 'Scompiglia le lettere ↗';
    renderType();
  });
  for (const button of lab.querySelectorAll('[data-type-font]')) button.addEventListener('click', () => {
    font = button.dataset.typeFont;
    for (const control of lab.querySelectorAll('[data-type-font]')) control.setAttribute('aria-pressed', String(control === button));
    renderType();
  });
  for (const button of lab.querySelectorAll('[data-type-color]')) button.addEventListener('click', () => {
    paper.dataset.color = button.dataset.typeColor;
    for (const control of lab.querySelectorAll('[data-type-color]')) control.setAttribute('aria-pressed', String(control === button));
  });
  lab.hidden = false;
  renderType();
})();
