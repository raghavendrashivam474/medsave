---

### 1. 🚨 Problems Encountered

1. **Hidden / Cut-off Close Button (`✕`):**
   * On mobile phones, when a user clicked a medicine card to open the detail modal, the top portion (including the close icon and generic analysis badges) was hidden behind the sticky site header (`.header`).
   * On laptops, the close button was only partially visible or clipped at the top right.
2. **UI Distortions & Symbol Corruption (Mid-fix regression):**
   * FontAwesome icons disappeared, layout margins smashed together, and special UTF-8 characters like the Rupee symbol (`₹`), em-dash (`—`), and middle dot (`·`) turned into broken question marks (`?`) or codes like `<97>`.
3. **Unresponsive Close Button Click:**
   * Even after fixing the visual layout, clicking the close button (`✕`) failed to dismiss the modal popup.

---

### 2. 🧪 What We Tried & What Didn't Work

#### Attempt 1: Adjusting `z-index` and Mobile Padding in CSS
* **What we tried:** Added `z-index: 110` to `.modal-close` and added right padding to `.modal-header`.
* **Why it failed:** The close button was still trapped behind the sticky navbar because of a deeper CSS **Stacking Context** problem.

#### Attempt 2: Setting Ultra-High `z-index` (`2147483646`) on the Modal Overlay
* **What we tried:** Cranked the `z-index` of `#medicineModal.modal-overlay` to maximum integer values.
* **Why it failed:** `#medicineModal` was HTML-nested inside `<main class="container">`, and `.container` had `z-index: 1`. In CSS, an element **can never escape a parent's stacking context**, no matter how high its `z-index` is. The sticky `.header` (`z-index: 50`) was always rendering on top of `<main>` and everything inside it.
* **Side-effect (PowerShell Encoding):** Standard PowerShell commands like `Set-Content` saved files as Windows-1252/ANSI, corrupting the project's UTF-8 symbols and FontAwesome icon definitions.

---

### 3. ✅ What Finally Worked (The Root Cause Solutions)

#### Solution 1: DOM Restructuring (Escaping the Stacking Context)
* **Fix:** Moved `<div id="medicineModal">` **out of `<main>`** and relocated it as a direct child of `<body>` (placed right before `</body>`).
* **Result:** Freed from the parent container's `z-index: 1` jail, setting `z-index: 99999 !important` on `#medicineModal.modal-overlay` allowed the backdrop and modal window to render cleanly **above the sticky header bar** on all screen sizes.

#### Solution 2: Explicit Relative Anchoring & Mobile Safe Viewport
* **Fix:** Set `position: relative !important;` on `#medicineModal .modal-content` and added vertical bounds (`max-height: 85vh; margin: auto`).
* **Result:** Anchored the `.modal-close` button (`top: 1.1rem; right: 1.1rem`) directly to the top-right corner of the medicine card itself, ensuring it stays visible and reachable on all phone aspect ratios.

#### Solution 3: Pure UTF-8 File Writing
* **Fix:** Used .NET `System.Text.UTF8Encoding($false)` in PowerShell to perform all file modifications.
* **Result:** Cleanly restored all original typography, CSS styling, Rupee symbols (`₹`), and FontAwesome icons without character corruption.

#### Solution 4: Bulletproof Event Delegation & Pointer-Events
* **Fix:**
  1. Added `pointer-events: auto !important;` to `.modal-close` and `pointer-events: none !important;` to `.modal-close *` (so clicking the `<i>` icon passes the click directly to the button).
  2. Added global capturing event delegation (`document.addEventListener('click', ..., true)`) targeting `#closeModal, .modal-close` as well as backdrop clicks.
* **Result:** The modal now closes instantly whether clicking the button border, the icon inside it, or tapping outside on the dark backdrop overlay.

---

### 💡 Key Takeaway
Whenever building modals with sticky site headers, **always render the modal overlay directly under `<body>`** at the DOM root level to prevent parent container `z-index` trapping, and use **capturing event delegation** for touch-friendly dismissals on mobile!