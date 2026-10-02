# Root Cause Analysis (RCA): Medicine Savings Calculator & Button Failures

* **Project:** `medsave`
* **Module:** Frontend Medicine Modal & Duration Calculator
* **File Affected:** `frontend/main.js`
* **Status:** Resolved & Committed (`1341e8e`)

---

## 1. Executive Summary
Users experienced issues where:
1. The **`+` / `-` increment buttons** and **preset duration pills (30/60/90 days)** did not respond to clicks.
2. Calculations failed or produced incorrect outputs when values were altered or cleared.
3. Currency symbols rendered as corrupted gibberish (`â‚¹` instead of `₹`).

---

## 2. Root Cause Breakdown

### Issue A: Premature Event Binding & Execution Context
* **Root Cause:** The script initialized modal listeners inside an Immediately Invoked Function Expression (`(function initModalChrome() { ... })()`).
* **Why it failed:** When the JavaScript file executed on initial page load, some modal elements were not yet fully parsed or attached to the DOM tree. As a result:
  ```javascript
  const bind = (id, fn) => { 
      const el = document.getElementById(id); 
      if (el) el.addEventListener('click', fn); // ❌ el was null, listeners were never attached!
  };
  ```
  Since the binding silently failed once during script evaluation, subsequent button clicks did nothing.

---

### Issue B: Child Element Event Swallowing (Icon Target Hijacking)
* **Root Cause:** The `+` and `-` buttons contained child elements (FontAwesome icon tags `<i class="fas fa-plus"></i>`).
* **Why it failed:** When a user clicked directly on the plus/minus icon, `event.target` was the `<i>` element rather than the parent `<button>` container.
* Without event delegation utilizing `.closest()`, any direct check like `e.target.id === 'unitsPlus'` returned `false` because `e.target` was the inner `<i>` tag.

---

### Issue C: Input Sanitization & Empty-State Math Errors
* **Root Cause:** Direct unvalidated conversion of input values:
  ```javascript
  const units = Math.max(0, parseFloat(u && u.value) || 0);
  const days = Math.max(0, parseFloat(d && d.value) || 0);
  ```
* **Why it failed:** 
  * If a user backspaced an input to type a new number, the fallback evaluated to `0`.
  * Total price became `₹0.00`, savings percentage calculation resulted in `0%` or `NaN`, and preset pills lost synchronization with the active day count.
  * Inputs were not clamped to a valid floor of `1` dose or `1` day.

---

### Issue D: Character Encoding (Mojibake)
* **Root Cause:** Encoding mismatch between UTF-8 and Windows-1252/ANSI during previous file edits or PowerShell output streams.
* **Why it failed:** The Indian Rupee symbol `₹` (Unicode `U+20B9`, UTF-8 bytes `E2 82 B9`) was interpreted as ANSI characters, rendering `â‚¹` across modal prices, medicine search cards, and badges.

---

## 3. Surgical Fix Architecture

| Area | Before (Broken) | After (Fixed) |
| :--- | :--- | :--- |
| **Event Strategy** | Static element binding on load (`document.getElementById`) | **Global Event Delegation** (`document.addEventListener('click', e => e.target.closest(...))`) |
| **Click Targets** | Direct element matching (missed `<i>` child clicks) | **Target bubbling** via `.closest('#unitsPlus, [data-action="units-plus"]')` |
| **Input Clamping** | `Math.max(0, val)` (allowed 0 and invalid zero-divisions) | `Math.max(1, parseFloat(val) \|\| 1)` (safe floor) |
| **Preset Sync** | Desynchronized on manual typing | Live sync via delegated `'input'` listener updating `.preset-btn.active` |
| **Encoding** | Windows-1252 / Mojibake (`â‚¹`) | Normalized UTF-8 (`₹`) |

---

## 4. Key Takeaways & Best Practices

1. **Use Event Delegation for Modals & Dynamic Components:** Delegating events to `document` ensures buttons work regardless of whether elements are inserted into the DOM asynchronously, conditionally, or dynamically.
2. **Always Use `.closest()` with Icon Buttons:** Whenever buttons wrap `<i>` or `<span>` tags, use `event.target.closest('selector')` to avoid dropping clicks that hit the inner child.
3. **Explicit UTF-8 Output on Windows:** When writing files using PowerShell, always specify `-Encoding UTF8` (`Set-Content -Encoding UTF8`) to avoid corrupting multi-byte unicode characters.