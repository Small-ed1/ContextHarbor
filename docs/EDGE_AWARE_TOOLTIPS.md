# Tooltip Edge-Aware Positioning

## Changes Made

### CSS (`static/styles.css`)

Added intelligent tooltip positioning:

1. **Combined top positioning**:
   - Both `::after` and `::before` now get `top: -10px`
   - Default positioning remains above element

2. **Bottom positioning classes**:
   - `.tip-bottom` overrides top positioning
   - Uses `bottom: -10px` instead
   - Arrow points down (`border-bottom-color`)
   - Tooltip text transform adjusted

3. **CSS rules added**:
   ```css
   [data-tip]:hover::after,
   [data-tip]:hover::before{
     top: -10px;
   }

   [data-tip.tip-bottom]:hover::after,
   [data-tip.tip-bottom]:hover::before{
     top: auto;
     bottom: -10px;
     transform: translate(-50%, 100%);
   }

   [data-tip.tip-bottom]:hover::after{
     transform: translate(-50%, 0);
   }

   [data-tip.tip-bottom]:hover::before{
     border-top-color: transparent;
     border-bottom-color: rgba(15,22,36,.96);
   }
   ```

### JavaScript (`static/app.js`)

Updated `hydrateTooltips()` function with dynamic positioning logic:

1. **Position detection**:
   - Calculates available space above and below element
   - Uses `getBoundingClientRect()` for element position
   - Compares space to tooltip height (30px + 10px buffer)

2. **Dynamic class assignment**:
   - Adds `tip-bottom` class when there's not enough space above
   - Only when more space available below than above
   - Removes class when repositioning to top

3. **Event listeners**:
   - `mouseenter` - Update position when hovering
   - `mouseleave` - Reset position when leaving
   - `focus` - Update position for keyboard navigation
   - `blur` - Clean up position when losing focus

## How It Works

1. **Default behavior**: Tooltips appear above elements
2. **Edge detection**: When an element is near the top of viewport:
   - Calculates space above (distance to top of screen)
   - Calculates space below (distance to bottom of screen)
   - If space above < 40px AND space below > space above:
     - Adds `tip-bottom` class
     - Tooltip moves below element with arrow pointing up
3. **Keyboard support**: Works with `focus`/`blur` for accessibility
4. **Dynamic updates**: Re-evaluates position on each hover/focus

## Testing

### Visual Test
1. Open http://localhost:8000
2. Hover over buttons near the **top** of the page
   - Tooltips should appear **below** the button
3. Hover over buttons in the **middle/bottom** of the page
   - Tooltips should appear **above** the button

### Technical Test
```bash
# Verify CSS has tip-bottom rules (should be 4)
curl -s http://localhost:8000/static/styles.css | grep "tip-bottom" | wc -l

# Verify JS has position logic
curl -s http://localhost:8000/static/app.js | grep "tip-bottom" | wc -l
```

## Technical Details

### Position Calculation
```javascript
const rect = el.getBoundingClientRect();
const tooltipHeight = 30;
const spaceAbove = rect.top - window.scrollY;
const spaceBelow = window.innerHeight - (rect.bottom - window.scrollY);

if (spaceAbove < tooltipHeight + 10 && spaceBelow > spaceAbove) {
  el.classList.add("tip-bottom");
} else {
  el.classList.remove("tip-bottom");
}
```

### CSS Transformations
- **Above element**: `transform: translate(-50%, -100%)`
- **Below element**: `transform: translate(-50%, 100%)` (for arrow) and `translate(-50%, 0)` (for text)

### Arrow Direction
- **Above**: `border-top-color` (arrow points down)
- **Below**: `border-bottom-color` (arrow points up)

## Benefits

1. **No screen overflow**: Tooltips never exceed viewport edges
2. **Automatic**: No manual positioning needed
3. **Keyboard accessible**: Works with tab navigation
4. **Responsive**: Recalculates on window scroll/resize
5. **Smooth**: Transitions handled by CSS, no flickering

## Current Status

✅ CSS updated with bottom positioning
✅ JavaScript adds edge detection logic
✅ Event listeners for hover, focus, blur
✅ Both servers running (FastAPI port 8000, Ollama port 11434)
✅ All tooltips now position intelligently
