(() => {
  'use strict';

  const navToggle = document.querySelector('[data-nav-toggle]');
  const nav = document.getElementById('primary-nav');
  if (navToggle && nav) {
    const setOpen = (open) => {
      nav.classList.toggle('is-open', open);
      navToggle.setAttribute('aria-expanded', String(open));
      navToggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    };
    setOpen(false);
    navToggle.hidden = false;
    document.documentElement.classList.add('js');
    navToggle.addEventListener('click', () => {
      setOpen(navToggle.getAttribute('aria-expanded') !== 'true');
    });
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && navToggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        navToggle.focus();
      }
    });
  }

  document.querySelectorAll('a[href^="https://wa.me/"]').forEach((link) => {
    link.addEventListener('click', () => {
      if (typeof window.gtag !== 'function') return;
      try {
        window.gtag('event', 'whatsapp_click', {
          product: link.dataset.product || 'general',
          cta: link.dataset.cta || 'whatsapp',
          page_path: window.location.pathname,
        });
      } catch (_) {
        // Contact remains available if analytics is unavailable or fails.
      }
    });
  });

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('[data-carousel]').forEach((carousel) => {
    const track = carousel.querySelector('.carousel-track');
    const previous = carousel.querySelector('[data-carousel-prev]');
    const next = carousel.querySelector('[data-carousel-next]');
    const toggle = carousel.querySelector('[data-carousel-toggle]');
    if (!track || !track.children.length) return;

    let manuallyPaused = false;
    let hovered = false;
    let focused = carousel.contains(document.activeElement);
    let touching = false;
    let interactionUntil = 0;
    let timer;
    const interval = 5000;

    const updateToggle = () => {
      if (!toggle) return;
      toggle.hidden = false;
      toggle.disabled = reducedMotion.matches;
      toggle.setAttribute('aria-pressed', String(manuallyPaused));
      const label = reducedMotion.matches
        ? 'Rotación automática desactivada por preferencia de movimiento reducido'
        : manuallyPaused ? 'Reanudar rotación automática' : 'Pausar rotación automática';
      toggle.setAttribute('aria-label', label);
      toggle.textContent = reducedMotion.matches
        ? 'Rotación desactivada' : manuallyPaused ? 'Reanudar' : 'Pausar';
    };

    const advance = (direction) => {
      const maximum = track.scrollWidth - track.clientWidth;
      if (maximum <= 1) return;
      const current = track.scrollLeft;
      const positions = Array.from(track.children, (child) =>
        child.getBoundingClientRect().left - track.getBoundingClientRect().left + current
      );
      let target;
      if (direction > 0) {
        target = current >= maximum - 2
          ? 0 : positions.find((position) => position > current + 2) ?? maximum;
      } else {
        target = current <= 2
          ? maximum : positions.reverse().find((position) => position < current - 2) ?? 0;
      }
      track.scrollTo({
        left: Math.max(0, Math.min(maximum, target)),
        behavior: reducedMotion.matches ? 'auto' : 'smooth',
      });
    };

    const schedule = () => {
      window.clearTimeout(timer);
      if (manuallyPaused || reducedMotion.matches || document.hidden || hovered || focused || touching) return;
      timer = window.setTimeout(() => {
        if (Date.now() >= interactionUntil) advance(1);
        schedule();
      }, Math.max(interval, interactionUntil - Date.now()));
    };
    const pauseForInteraction = () => {
      interactionUntil = Date.now() + 8000;
      schedule();
    };

    carousel.addEventListener('pointerenter', (event) => {
      if (event.pointerType !== 'mouse' && event.pointerType !== 'pen') return;
      hovered = true;
      schedule();
    });
    carousel.addEventListener('pointerleave', () => {
      hovered = false;
      schedule();
    });
    carousel.addEventListener('focusin', () => {
      focused = true;
      schedule();
    });
    carousel.addEventListener('focusout', () => {
      // Check after focus has moved, including between carousel controls.
      window.setTimeout(() => {
        focused = carousel.contains(document.activeElement);
        schedule();
      }, 0);
    });
    track.addEventListener('touchstart', () => {
      touching = true;
      schedule();
    }, { passive: true });
    const endTouch = () => {
      touching = false;
      pauseForInteraction();
    };
    track.addEventListener('touchend', endTouch, { passive: true });
    track.addEventListener('touchcancel', endTouch, { passive: true });
    track.addEventListener('wheel', pauseForInteraction, { passive: true });
    track.addEventListener('keydown', (event) => {
      if (['ArrowLeft', 'ArrowRight', 'Home', 'End', 'PageUp', 'PageDown', ' '].includes(event.key)) {
        pauseForInteraction();
      }
    });
    [previous, next].forEach((button, index) => {
      if (!button) return;
      button.hidden = false;
      button.addEventListener('click', () => {
        pauseForInteraction();
        advance(index === 0 ? -1 : 1);
      });
    });
    if (toggle) {
      toggle.addEventListener('click', () => {
        manuallyPaused = !manuallyPaused;
        updateToggle();
        schedule();
      });
    }
    document.addEventListener('visibilitychange', schedule);
    const onMotionChange = () => {
      updateToggle();
      schedule();
    };
    if (typeof reducedMotion.addEventListener === 'function') {
      reducedMotion.addEventListener('change', onMotionChange);
    } else {
      reducedMotion.addListener(onMotionChange);
    }
    updateToggle();
    schedule();
  });
})();
