/**
 * ============================================================
 * AAROGYA — THEME MANAGER
 * js/theme.js
 *
 * Manages light / dark theme switching.
 * - Reads saved preference from localStorage
 * - Falls back to system preference
 * - Applies theme to <html data-theme="">
 * - Persists user choice
 * - No page reload required
 * ============================================================
 */

const ThemeManager = (() => {

  const STORAGE_KEY = 'aarogya-theme';
  const DARK        = 'dark';
  const LIGHT       = 'light';
  const root        = document.documentElement;

  /**
   * Get the currently active theme from the DOM.
   */
  function getCurrent() {
    return root.getAttribute('data-theme') || LIGHT;
  }

  /**
   * Get the user's saved preference from localStorage.
   * Returns null if no preference has been saved.
   */
  function getSaved() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch {
      return null;
    }
  }

  /**
   * Get the operating system / browser colour preference.
   */
  function getSystemPreference() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? DARK
      : LIGHT;
  }

  /**
   * Apply a theme to the document.
   * @param {string} theme - 'light' | 'dark'
   */
  function apply(theme) {
    root.setAttribute('data-theme', theme);

    // Update toggle button aria-label for accessibility
    const toggleBtn = document.querySelector('[data-theme-toggle]');
    if (toggleBtn) {
      toggleBtn.setAttribute(
        'aria-label',
        theme === DARK ? 'Switch to light theme' : 'Switch to dark theme'
      );
      toggleBtn.setAttribute('title',
        theme === DARK ? 'Switch to light theme' : 'Switch to dark theme'
      );
    }

    // Dispatch a custom event so other modules can react
    document.dispatchEvent(
      new CustomEvent('themechange', { detail: { theme } })
    );
  }

  /**
   * Save preference to localStorage.
   * @param {string} theme
   */
  function save(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // Storage may be unavailable (private browsing, etc.)
    }
  }

  /**
   * Toggle between light and dark.
   */
  function toggle() {
    const next = getCurrent() === DARK ? LIGHT : DARK;
    apply(next);
    save(next);
  }

  /**
   * Initialise the theme on page load.
   * Priority: saved preference > system preference
   */
  function init() {
    const resolved = getSaved() || getSystemPreference();
    apply(resolved);

    // Watch for system preference changes
    // (only applies if user has not explicitly set a preference)
    window
      .matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', (e) => {
        if (!getSaved()) {
          apply(e.matches ? DARK : LIGHT);
        }
      });
  }

  // Public API
  return { init, toggle, getCurrent, apply, save };

})();

// Initialise immediately when script loads
ThemeManager.init();
