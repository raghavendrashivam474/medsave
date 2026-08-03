/**
 * ============================================================
 * AAROGYA — HOME PAGE SCRIPT
 * js/home.js
 *
 * Handles homepage-specific interactions:
 * - Medicine chip clicks → populate search
 * - Search form submission → redirect to search results
 * - Keyboard navigation on search
 * ============================================================
 */

document.addEventListener('DOMContentLoaded', () => {

  // ----------------------------------------------------------
  // ELEMENTS
  // ----------------------------------------------------------

  const searchInput = document.getElementById('hero-search-input');
  const searchForm  = document.getElementById('hero-search-form');
  const chips       = document.querySelectorAll('[data-medicine-chip]');

  // ----------------------------------------------------------
  // NAVIGATE TO SEARCH RESULTS
  // Central helper — every entry point uses this
  // ----------------------------------------------------------

  function goToResults(query) {
    const trimmed = (query || '').trim();
    if (!trimmed) {
      searchInput?.focus();
      return;
    }
    window.location.href =
      `search-results.html?q=${encodeURIComponent(trimmed)}`;
  }

  // ----------------------------------------------------------
  // MEDICINE CHIPS
  // Clicking a chip performs an immediate search
  // ----------------------------------------------------------

  chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const medicine = chip.getAttribute('data-medicine-chip');
      if (searchInput && medicine) {
        searchInput.value = medicine;
      }
      goToResults(medicine);
    });

    chip.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        chip.click();
      }
    });
  });

  // ----------------------------------------------------------
  // SEARCH FORM SUBMIT
  // ----------------------------------------------------------

  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      goToResults(searchInput?.value);
    });
  }

  // ----------------------------------------------------------
  // SEARCH INPUT — Enter key submits
  // ----------------------------------------------------------

  if (searchInput) {
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        goToResults(searchInput.value);
      }
    });
  }

});
