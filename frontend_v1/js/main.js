/**
 * ============================================================
 * AAROGYA — MAIN SCRIPT
 * js/main.js
 *
 * Entry point for all UI interactions.
 * This sprint only initialises:
 * - Theme toggle wiring
 * - Header scroll behaviour
 * - Mobile menu toggle
 * ============================================================
 */

document.addEventListener('DOMContentLoaded', () => {

  // ------------------------------------------------------------
  // THEME TOGGLE
  // Wire up any element with [data-theme-toggle]
  // ------------------------------------------------------------

  const themeToggles = document.querySelectorAll('[data-theme-toggle]');
  themeToggles.forEach((btn) => {
    btn.addEventListener('click', () => {
      ThemeManager.toggle();
    });
  });

  // ------------------------------------------------------------
  // HEADER — scroll shadow
  // ------------------------------------------------------------

  const header = document.querySelector('.header');

  if (header) {
    const onScroll = () => {
      if (window.scrollY > 8) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // run once on load
  }

  // ------------------------------------------------------------
  // MOBILE MENU TOGGLE
  // ------------------------------------------------------------

  const menuToggle  = document.querySelector('[data-mobile-toggle]');
  const mobileNav   = document.querySelector('.mobile-nav');

  if (menuToggle && mobileNav) {
    menuToggle.addEventListener('click', () => {
      const isOpen = mobileNav.classList.toggle('open');
      menuToggle.classList.toggle('open', isOpen);
      menuToggle.setAttribute('aria-expanded', String(isOpen));

      // Prevent body scroll when menu is open
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    // Close menu when a nav link is clicked
    mobileNav.querySelectorAll('.nav-link').forEach((link) => {
      link.addEventListener('click', () => {
        mobileNav.classList.remove('open');
        menuToggle.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });

    // Close menu on outside click
    document.addEventListener('click', (e) => {
      if (
        mobileNav.classList.contains('open') &&
        !mobileNav.contains(e.target) &&
        !menuToggle.contains(e.target)
      ) {
        mobileNav.classList.remove('open');
        menuToggle.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      }
    });
  }

});
