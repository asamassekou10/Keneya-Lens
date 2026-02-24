# Keneya Lens Design System

## Medical-Grade UI/UX Guidelines

This document defines the design system for Keneya Lens, ensuring a professional, clinical-grade interface suitable for healthcare professionals including doctors, nurses, and community health workers.

---

## 1. Design Principles

### 1.1 Core Principles

| Principle | Description |
|-----------|-------------|
| **Clinical Clarity** | Information must be instantly readable in high-stress environments |
| **Error Prevention** | Design must minimize the risk of misinterpretation |
| **Accessibility** | WCAG 2.1 AA compliant for users with visual impairments |
| **Efficiency** | Minimize clicks and cognitive load for time-pressed clinicians |
| **Trust** | Visual design must convey reliability and professionalism |

### 1.2 Design Constraints

- No decorative emojis or icons
- No playful or casual language
- No bright, saturated colors that could cause eye strain
- No animations that delay critical information
- All text must meet minimum contrast ratios (4.5:1 for normal text)

---

## 2. Color Palette

### 2.1 Primary Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Navy Primary** | #1B365D | 27, 54, 93 | Headers, primary actions |
| **Navy Dark** | #0F2340 | 15, 35, 64 | Sidebar, navigation |
| **White** | #FFFFFF | 255, 255, 255 | Backgrounds, text on dark |

### 2.2 Semantic Colors (Triage Levels)

| Level | Name | Hex | Usage |
|-------|------|-----|-------|
| **Critical** | Alert Red | #C41E3A | Immediate/emergency cases |
| **Urgent** | Warning Amber | #D4790E | Urgent referral needed |
| **Moderate** | Caution Yellow | #B8860B | Schedule appointment |
| **Non-Urgent** | Stable Green | #2E7D32 | Can manage locally |
| **Info** | Neutral Blue | #1565C0 | Informational messages |

### 2.3 Neutral Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Gray 900** | #1A1A1A | Primary text |
| **Gray 700** | #4A4A4A | Secondary text |
| **Gray 500** | #767676 | Disabled text, borders |
| **Gray 200** | #E5E5E5 | Dividers, subtle borders |
| **Gray 50** | #FAFAFA | Background, cards |

### 2.4 Background Colors

| Context | Color | Hex |
|---------|-------|-----|
| Main background | Off-white | #F8F9FA |
| Card background | White | #FFFFFF |
| Sidebar | Navy Dark | #0F2340 |
| Input fields | White | #FFFFFF |

---

## 3. Typography

### 3.1 Font Stack

```css
/* Primary font - clean, medical-grade readability */
font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont,
             'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

/* Monospace for data/codes */
font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
```

### 3.2 Type Scale

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| H1 | 28px | 600 | 1.2 | Page titles |
| H2 | 22px | 600 | 1.3 | Section headers |
| H3 | 18px | 600 | 1.4 | Subsection headers |
| Body | 15px | 400 | 1.6 | Main content |
| Body Small | 13px | 400 | 1.5 | Secondary text |
| Caption | 12px | 400 | 1.4 | Labels, metadata |
| Overline | 11px | 600 | 1.2 | Category labels |

### 3.3 Text Colors

| Context | Color | Contrast Ratio |
|---------|-------|----------------|
| Primary text | #1A1A1A | 16:1 |
| Secondary text | #4A4A4A | 9:1 |
| Disabled text | #767676 | 4.5:1 |
| Link text | #1565C0 | 5.5:1 |
| Error text | #C41E3A | 5.8:1 |

---

## 4. Component Specifications

### 4.1 Buttons

#### Primary Button
```
Background: #1B365D (Navy Primary)
Text: #FFFFFF
Border: none
Border-radius: 4px
Padding: 12px 24px
Font-weight: 500
Hover: #0F2340
Active: #0A1A2E
```

#### Secondary Button
```
Background: transparent
Text: #1B365D
Border: 1px solid #1B365D
Border-radius: 4px
Padding: 12px 24px
Hover: #F0F4F8
```

#### Danger Button
```
Background: #C41E3A
Text: #FFFFFF
Border: none
Use: Destructive actions only
```

### 4.2 Input Fields

```
Background: #FFFFFF
Border: 1px solid #D1D5DB
Border-radius: 4px
Padding: 12px 16px
Focus border: #1B365D
Error border: #C41E3A
Placeholder: #767676
```

### 4.3 Cards

```
Background: #FFFFFF
Border: 1px solid #E5E5E5
Border-radius: 8px
Padding: 24px
Box-shadow: 0 1px 3px rgba(0,0,0,0.08)
```

### 4.4 Triage Alert Boxes

#### Critical Alert
```
Background: #FEF2F2
Border-left: 4px solid #C41E3A
Icon: Solid circle (filled)
Text: #7F1D1D
```

#### Urgent Alert
```
Background: #FFFBEB
Border-left: 4px solid #D4790E
Icon: Triangle outline
Text: #78350F
```

#### Moderate Alert
```
Background: #FEF9E7
Border-left: 4px solid #B8860B
Icon: Clock outline
Text: #713F12
```

#### Non-Urgent Alert
```
Background: #F0FDF4
Border-left: 4px solid #2E7D32
Icon: Checkmark
Text: #14532D
```

---

## 5. Layout Specifications

### 5.1 Grid System

- **Container max-width**: 1200px
- **Sidebar width**: 280px (fixed)
- **Main content**: Fluid (remaining width)
- **Gutter**: 24px
- **Column gap**: 16px

### 5.2 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight spacing |
| sm | 8px | Related elements |
| md | 16px | Standard spacing |
| lg | 24px | Section spacing |
| xl | 32px | Major sections |
| 2xl | 48px | Page sections |

### 5.3 Page Structure

```
+----------------------------------------------------------+
|  HEADER BAR (64px)                                        |
|  [Logo] Keneya Lens              [Status] [Settings]      |
+----------------------------------------------------------+
|         |                                                 |
| SIDEBAR |  MAIN CONTENT AREA                              |
|  (280px)|                                                 |
|         |  +------------------------------------------+   |
|  Nav    |  | TAB BAR                                  |   |
|  Items  |  +------------------------------------------+   |
|         |  |                                          |   |
|  -----  |  | CONTENT PANEL                            |   |
|         |  |                                          |   |
|  Config |  |                                          |   |
|  Panel  |  |                                          |   |
|         |  |                                          |   |
|         |  +------------------------------------------+   |
+----------------------------------------------------------+
|  FOOTER (48px) - Disclaimer                               |
+----------------------------------------------------------+
```

---

## 6. Iconography

### 6.1 Icon Style

- **Style**: Outlined, 1.5px stroke
- **Size**: 20px (standard), 16px (small), 24px (large)
- **Color**: Inherit from text color
- **Source**: Lucide Icons or Heroicons (MIT licensed)

### 6.2 Standard Icons

| Function | Icon Name | Usage |
|----------|-----------|-------|
| Search | `search` | Query input |
| Settings | `settings` | Configuration |
| Upload | `upload` | File upload |
| Document | `file-text` | PDF/guidelines |
| Image | `image` | Medical images |
| History | `clock` | Query history |
| Info | `info` | Information |
| Alert | `alert-triangle` | Warnings |
| Check | `check-circle` | Success |
| Close | `x` | Dismiss |
| Menu | `menu` | Mobile nav |

---

## 7. Triage Level Visual System

### 7.1 Triage Indicators

Each triage level has a consistent visual treatment:

| Level | Label | Color Badge | Border |
|-------|-------|-------------|--------|
| 1 | CRITICAL | Red filled | 4px left red |
| 2 | URGENT | Amber filled | 4px left amber |
| 3 | MODERATE | Yellow filled | 4px left yellow |
| 4 | NON-URGENT | Green filled | 4px left green |

### 7.2 Triage Response Header

```
+----------------------------------------------------------+
| [BADGE] TRIAGE LEVEL: URGENT                              |
|         Recommend referral within 24 hours                |
+----------------------------------------------------------+
```

---

## 8. Accessibility Requirements

### 8.1 Color Contrast

- Normal text (< 18px): Minimum 4.5:1 ratio
- Large text (>= 18px bold or >= 24px): Minimum 3:1 ratio
- UI components: Minimum 3:1 ratio against background

### 8.2 Keyboard Navigation

- All interactive elements must be keyboard accessible
- Focus indicators must be clearly visible (2px solid outline)
- Tab order must be logical (left-to-right, top-to-bottom)

### 8.3 Screen Reader Support

- All images must have descriptive alt text
- Form fields must have associated labels
- Dynamic content must announce changes
- Triage levels must be announced verbally

---

## 9. Responsive Breakpoints

| Breakpoint | Width | Layout Change |
|------------|-------|---------------|
| Mobile | < 640px | Single column, collapsed sidebar |
| Tablet | 640-1024px | Collapsible sidebar |
| Desktop | > 1024px | Full layout with fixed sidebar |

---

## 10. Motion and Transitions

### 10.1 Transition Timing

- **Standard**: 200ms ease-out
- **Expand/collapse**: 300ms ease-in-out
- **Page transitions**: None (instant)

### 10.2 Loading States

- Use skeleton loaders for content
- Use spinner for actions (submit, analyze)
- Always show progress for long operations (> 2s)

---

## 11. Form Design Patterns

### 11.1 Symptom Input Form

```
+----------------------------------------------------------+
| PATIENT SYMPTOMS                                          |
| Enter detailed symptom description                        |
+----------------------------------------------------------+
|                                                          |
| [Multi-line text area - min 150px height]                |
|                                                          |
+----------------------------------------------------------+
| Character count: 0/5000                                  |
+----------------------------------------------------------+
|                                                          |
| [Analyze Symptoms]  [Clear]                              |
+----------------------------------------------------------+
```

### 11.2 Image Upload Form

```
+----------------------------------------------------------+
| MEDICAL IMAGE ANALYSIS                                    |
+----------------------------------------------------------+
|                                                          |
| +------------------------------------------------------+ |
| |                                                      | |
| |              [Upload Area]                           | |
| |        Drag and drop or click to upload              | |
| |        Supported: JPEG, PNG (max 10MB)               | |
| |                                                      | |
| +------------------------------------------------------+ |
|                                                          |
| Image Type: [Dropdown: X-ray | Skin lesion | Other]     |
|                                                          |
| Additional notes (optional):                             |
| [Text input]                                             |
|                                                          |
| [Analyze Image]                                          |
+----------------------------------------------------------+
```

---

## 12. Error and Validation States

### 12.1 Inline Validation

- Show validation on blur, not on input
- Error message appears below field
- Error border: 1px solid #C41E3A
- Error text: #C41E3A, 13px

### 12.2 System Errors

- Display in dedicated error panel at top of content area
- Include error code for support reference
- Provide clear next steps

---

## 13. Implementation Notes

### 13.1 CSS Custom Properties

```css
:root {
  /* Primary */
  --color-primary: #1B365D;
  --color-primary-dark: #0F2340;
  --color-primary-light: #2A4A7A;

  /* Semantic */
  --color-critical: #C41E3A;
  --color-urgent: #D4790E;
  --color-moderate: #B8860B;
  --color-stable: #2E7D32;
  --color-info: #1565C0;

  /* Neutral */
  --color-text-primary: #1A1A1A;
  --color-text-secondary: #4A4A4A;
  --color-border: #E5E5E5;
  --color-background: #F8F9FA;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Typography */
  --font-sans: 'Inter', -apple-system, sans-serif;
  --font-mono: 'SF Mono', monospace;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
}
```

### 13.2 Streamlit Custom CSS

The design system is implemented through Streamlit's custom CSS injection. See `app/streamlit_app.py` for the complete implementation.

---

## 14. Quality Checklist

Before deployment, verify:

- [ ] No emojis in production UI
- [ ] All text meets contrast requirements
- [ ] Triage colors are distinguishable
- [ ] All buttons have hover/focus states
- [ ] Forms have proper validation
- [ ] Loading states are implemented
- [ ] Error messages are clear
- [ ] Keyboard navigation works
- [ ] Screen reader tested
- [ ] Mobile layout verified

---

*Design System Version 1.0 | Keneya Lens Medical AI*
