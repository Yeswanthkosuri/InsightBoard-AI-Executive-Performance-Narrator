# InsightBoard Design System

## Color Palette (Neutral + Calm)

### Core Colors
- **Charcoal** (Primary text): `#0f0f0f` – Deep, professional
- **Slate** (Secondary text): `#6b7280` – Muted, readable
- **Off-white** (Background): `#fafaf8` – Warm white, easy on eyes
- **Indigo** (Accent/Primary): `#4f46e5` – Calm, professional blue
- **Indigo Dark** (Hover): `#4338ca` – Slightly deeper

### Semantic Colors
- **Success**: `#10b981` (Emerald)
- **Warning**: `#f59e0b` (Amber)
- **Danger**: `#ef4444` (Red)
- **Info**: `#06b6d4` (Cyan)

### Neutral Scale
- `#ffffff` – Pure white (surfaces)
- `#f9fafb` – Almost white
- `#f3f4f6` – Light gray
- `#e5e7eb` – Subtle border
- `#6b7280` – Muted secondary
- `#374151` – Muted tertiary
- `#1f2937` – Medium gray
- `#111827` – Near black (for depth)
- `#0f0f0f` – Charcoal (text)

### Backgrounds
- **Default**: `#fafaf8`
- **Elevated**: `#ffffff`
- **Subtle**: `#f3f4f6`
- **Overlay**: `rgba(15, 15, 15, 0.5)`

---

## Spacing System (8px Base)

```
8px   = 1 unit (8)
16px  = 2 units (xs)
24px  = 3 units (sm)
32px  = 4 units (md)
40px  = 5 units (lg)
48px  = 6 units (xl)
56px  = 7 units (2xl)
64px  = 8 units (3xl)
```

### Application
- **Padding**: 16px (forms), 24px (cards), 32px (sections)
- **Gaps**: 16px (form fields), 24px (grid), 32px (section)
- **Margins**: Top 0, bottom varies by context
- **Page padding**: 24px mobile, 32px desktop

---

## Typography

### Font Stack
- **Sans-serif**: `"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- **Mono**: `"Fira Code", "IBM Plex Mono", monospace`

### Type Scale
| Level | Size | Weight | Use Case |
|-------|------|--------|----------|
| Display | 3.5rem | 700 | Page hero |
| H1 | 2rem | 700 | Section titles |
| H2 | 1.5rem | 600 | Card headers |
| H3 | 1.25rem | 600 | Sub headers |
| Body | 1rem | 400 | Content |
| Small | 0.875rem | 400 | Secondary |
| Tiny | 0.75rem | 500 | Labels, badges |

### Line Heights
- Headings: 1.2
- Body: 1.6
- Compact: 1.4

---

## Border & Shadows

### Radius
- `2px` – Subtle (inputs, small elements)
- `4px` – Standard (buttons, cards)
- `8px` – Rounded (panels)
- `16px` – Large (hero section)
- `999px` – Pill (badges, full-round buttons)

### Shadows
```css
/* Elevation 1: Subtle card/hover */
box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);

/* Elevation 2: Standard card */
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);

/* Elevation 3: Lifted/modal */
box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);

/* Elevation 4: Hero/prominent */
box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

### Borders
- Standard border: `1px solid #e5e7eb`
- Subtle border: `1px solid #f3f4f6`
- Focus border: `2px solid #4f46e5` (with outline)

---

## Components

### Buttons
- **Primary**: Indigo background, white text, rounded, 12px vertical padding
- **Secondary**: Gray background, dark text, rounded
- **Ghost**: Transparent background, accent text, minimal
- **Disabled**: 50% opacity, cursor not-allowed
- **Hover**: Scale up 2%, color transition 180ms
- **Focus**: 2px indigo outline, 2px offset

### Form Inputs
- **Height**: 40px (text, select)
- **Padding**: 10px 12px
- **Border**: 1px gray, on focus 2px indigo
- **Radius**: 4px
- **Typography**: 0.95rem body weight

### Cards / Panels
- **Padding**: 24px
- **Border**: 1px subtle
- **Radius**: 8px
- **Background**: White or subtle
- **Shadow**: Elevation 2
- **Hover**: Slight shadow increase (Elevation 3)

### Badges
- **Padding**: 4px 8px
- **Font**: 0.75rem, 600 weight
- **Radius**: 999px
- **Colors**: Semantic (success green, danger red, etc.)

---

## Spacing: Japanese-Inspired Minimalism

### Whitespace Principles
1. **Generous margins** between major sections (40-56px)
2. **Tight form fields** (16px gap)
3. **Breathing room** around images (24px)
4. **Balanced layouts** with max-widths
5. **Asymmetric grids** for visual interest

### Rhythm
- Consistent 8px increments create visual harmony
- Odd multiples (3, 5, 7) for asymmetry
- Even multiples (2, 4, 6) for alignment

---

## Interactions

### Transitions
- **Fast**: 150ms (hover, focus)
- **Standard**: 200ms (state changes)
- **Slow**: 350ms (modals, major layout)
- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)` (ease-in-out)

### States
- **Hover**: Slight lift (shadow increase), color shift
- **Focus**: 2px outline, offset 2px
- **Active**: Color shift + slight scale (0.98x)
- **Disabled**: 50% opacity, no pointer

---

## Accessibility (WCAG AAA)

### Contrast
- **Normal text**: 7:1 (charcoal on white)
- **Large text**: 4.5:1 minimum
- **UI components**: 3:1 minimum

### Focus States
- Always visible (2px outline, offset 2px)
- Color: Indigo (`#4f46e5`)
- Never removed

### Font Sizes
- Minimum 16px on mobile
- Line height minimum 1.4
- Adequate spacing between links

### Labels
- All inputs have visible labels
- Error messages associated with inputs
- Form validation clear and immediate

---

## Responsive Breakpoints

| Breakpoint | Width | Device |
|-----------|-------|--------|
| Mobile | < 640px | Phone |
| Tablet | 640px - 1024px | Tablet |
| Desktop | 1024px+ | Desktop |

### Adjustments
- **Mobile**: Single column, 24px padding, stacked buttons
- **Tablet**: 2-column layout where appropriate
- **Desktop**: Full grid, optimal reading width (1200px max)

---

## Implementation Notes

### Japanese Aesthetic Elements
1. **Subtle dividers**: Thin 1px borders between sections
2. **Generous whitespace**: 40px+ margins around major sections
3. **Calm colors**: Neutral palette without bold contrasts
4. **Minimalist iconography**: Geometric, simple shapes
5. **Layered shadows**: Multiple soft layers instead of one bold shadow
6. **Zen-inspired layout**: Balanced asymmetry, breathing room

### Best Practices
- No decorative elements
- Hierarchy through typography and spacing
- Consistency across all pages
- Mobile-first responsive design
- Performance-focused (no heavy animations)
- Accessibility-first approach
