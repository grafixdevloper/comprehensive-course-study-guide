# Document Design Guidelines

## Overview
Design principles for the Comprehensive Course Study Guide HTML/PDF output.

## Design Philosophy

### Academic Professionalism
- Clean, readable typography optimized for print
- Consistent visual hierarchy
- Purposeful use of color (not decoration)
- High contrast for accessibility

### Information Density
- Comprehensive but not cluttered
- Scannable structure with clear signposts
- Efficient use of page space
- Logical grouping of related content

### Traceability
- Every claim linked to source
- Visual distinction between:
  - Core content (definitions, theorems)
  - Exam-oriented material (PYQs, patterns)
  - Synthesis (explanations, tips)
  - Metadata (sources, priorities)

## Typography

### Font Stack
```css
--font-family-serif: 'Georgia', 'Times New Roman', serif;      /* Body text */
--font-family-sans: 'Inter', '-apple-system', 'Segoe UI', sans-serif; /* Headings, UI */
--font-family-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace; /* Code, formulas */
```

### Scale (Print)
| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 (Cover) | 36pt | Bold | 1.1 |
| H1 (Unit) | 24pt | Bold | 1.2 |
| H2 | 20pt | Bold | 1.2 |
| H3 (Topic) | 16pt | Bold | 1.2 |
| H4 | 13pt | Semibold | 1.3 |
| Body | 11pt | Normal | 1.55 |
| Small/Caption | 9pt | Normal | 1.5 |
| Footnote | 8pt | Normal | 1.4 |

### Hierarchy Rules
1. **H1**: Unit titles only
2. **H2**: Major sections (Exam Analysis, Revision)
3. **H3**: Topic titles
4. **H4**: Sub-sections within topics
5. **Body**: All explanatory text
6. **Callout titles**: Uppercase, 8pt, letter-spaced

## Color System

### Primary Palette
```css
--color-primary: #1a3c5e;      /* Dark navy - headings, primary elements */
--color-primary-dark: #0d2436; /* Darker - cover background */
--color-primary-light: #2d5a87; /* Lighter - accents */
--color-secondary: #2c6f8a;    /* Teal - secondary elements */
--color-accent: #c0392b;       /* Red - warnings, high priority */
--color-accent-light: #e74c3c; /* Lighter red */
```

### Semantic Colors
```css
--color-success: #27ae60;      /* Green - tips, accept states */
--color-warning: #f39c12;      /* Orange - moderate priority */
--color-error: #c0392b;        /* Red - mistakes, very high priority */
--color-info: #2980b9;         /* Blue - definitions, info */
```

### Priority Colors
```css
--priority-very-high: #c0392b;  /* Red */
--priority-high: #e67e22;       /* Orange */
--priority-moderate: #f39c12;   /* Yellow */
--priority-lower: #27ae60;      /* Green */
```

### Callout Backgrounds (Subtle)
```css
--callout-repeated-bg: #fdf2f2;    /* Light red */
--callout-priority-bg: #fff8e1;    /* Light yellow */
--callout-tip-bg: #e8f5e9;         /* Light green */
--callout-mistake-bg: #fdf2f2;     /* Light red */
--callout-definition-bg: #e8f0fe;  /* Light blue */
--callout-formula-bg: #f3e5f5;     /* Light purple */
--callout-important-bg: #fff3e0;   /* Light orange */
```

### Print Considerations
- All colors must work in grayscale
- Use `-webkit-print-color-adjust: exact` for backgrounds
- Minimum contrast ratio 4.5:1 for text
- Avoid color-only encoding (always use icons/text too)

## Layout

### Page Setup (A4)
```
Paper: A4 (210mm × 297mm)
Margins: Top 20mm, Right 18mm, Bottom 20mm, Left 18mm
Content Width: ~174mm
```

### Grid System
- 12-column conceptual grid
- Main content: 8-10 columns
- Side annotations: 2-4 columns (if used)
- Gutter: 4mm

### Spacing Scale
```css
--space-xs: 4pt   (0.25rem)
--space-sm: 8pt   (0.5rem)
--space-md: 12pt  (1rem)
--space-lg: 18pt  (1.5rem)
--space-xl: 24pt  (2rem)
--space-2xl: 36pt (3rem)
```

### Page Breaks
**Avoid Breaking:**
- Headings (all levels)
- Callout boxes
- Figures/diagrams
- Tables (prefer repeat header)
- Code blocks
- Question items
- Topic cards
- Revision boxes

**Force Breaks:**
- Unit starts (H1)
- Major sections (H2)
- Cover page
- Table of Contents

**CSS:**
```css
h1, h2, h3, h4, h5, h6 { break-after: avoid-page; }
.callout, .revision-box, .question-item, .topic-card, 
figure, .diagram-container, table, pre { break-inside: avoid; }
.unit-start, h1 { break-before: page; }
.cover-page { page: cover; }
```

## Components

### 1. Cover Page
- Full-page, centered content
- Dark background with gradient
- Course name (36pt)
- Subtitle (18pt, italic)
- Metadata: syllabus, date, PYQ count
- Disclaimer if no PYQ data
- Decorative divider line

### 2. Table of Contents
- Three-level hierarchy
- Right-aligned page numbers (filled during PDF generation)
- Dotted leaders between title and page
- Unit > Topic > Subtopic

### 3. Unit Header
- Page break before
- Unit number + title
- Syllabus reference
- Priority badge (if unit-level)

### 4. Topic Card
- Container with subtle border
- Header: Title + priority badge
- Content sections separated by spacing
- Source references at bottom of each section

### 5. Callout Boxes
**Structure:**
```
┌─────────────────────────────────┐
│ ICON TITLE                      │ ← callout-title (uppercase, small)
├─────────────────────────────────┤
│ Content...                      │ ← callout-content
└─────────────────────────────────┘
```

**Variants:**
| Variant | Border Color | Background | Use Case |
|---------|--------------|------------|----------|
| repeated | Red | Light red | Exact PYQ repetition |
| priority | Orange | Light yellow | High-priority topic |
| tip | Green | Light green | Exam tips |
| mistake | Red | Light red | Common mistakes |
| definition | Blue | Light blue | Formal definitions |
| formula | Purple | Light purple | Key formulas |
| important | Orange | Light orange | Important notes |

### 6. Question Items
- Card-style container
- Header: Question number + marks + year
- Body: Question text
- Footer: Family/concept tag

### 7. Revision Box
- Bordered container
- Title bar with topic name
- Bulleted list of key points
- Compact formatting

### 8. Diagrams
- Centered, max-width 100%
- Caption below (italic, 9pt)
- SVG preferred (vector, scalable)
- Fallback: PNG at 300 DPI

### 9. Tables
- Full-width by default
- Header: Dark navy background, white text
- Alternating row colors
- Minimum 9pt font
- Repeat header on page break

### 10. Mathematical Content
- MathJax with TeX input, SVG output
- Inline: `\( ... \)` - same line height
- Display: `\[ ... \]` - centered, margins
- Font size: 1.1em relative to body
- Line height: 1.8 for display math

### 11. Source References
- Inline: `[Source: file.pdf p.12]`
- Small, muted color
- Clickable in HTML (anchor to source index)

### 12. Priority Badges
- Inline, uppercase, small
- Color-coded by priority level
- Rounded corners

### 13. Footers/Headers
**Header (top):**
- Left: Document title (shortened)
- Right: Current unit/topic

**Footer (bottom):**
- Center: Page X / Y
- Small, muted

## Responsive Behavior

### Screen (Development)
- Max-width container centered
- Page shadows for visual separation
- All content accessible

### Print (PDF)
- No margins on @page
- No shadows
- Page breaks enforced
- Colors printed exactly

## Accessibility

### Color
- Not sole information carrier
- Sufficient contrast
- Patterns/text labels for priority

### Structure
- Semantic HTML5 elements
- Proper heading hierarchy
- Alt text for all diagrams
- Table headers and captions

### Reading Order
- Logical DOM order matches visual
- Skip links for navigation
- Focus indicators

## Implementation Checklist

### HTML Generation
- [ ] Semantic elements (article, section, header, footer, aside)
- [ ] Proper heading hierarchy (h1-h6)
- [ ] All images have alt text
- [ ] Tables have thead/tbody, captions
- [ ] MathJax configured
- [ ] CSS variables used throughout
- [ ] Print media queries separate

### CSS
- [ ] No hardcoded colors (use variables)
- [ ] No px for layout (use rem/pt)
- [ ] Page break rules comprehensive
- [ ] Print color adjust enabled
- [ ] Font fallbacks specified
- [ ] Dark mode support (for screen)

### PDF Generation
- [ ] Wait for MathJax ready
- [ ] Wait for fonts loaded
- [ ] Wait for images/SVG loaded
- [ ] PrintBackground: true
- [ ] Header/footer templates
- [ ] Page size A4
- [ ] Margins correct

### QA
- [ ] No clipped content
- [ ] No orphan headings
- [ ] Tables not awkwardly split
- [ ] Diagrams fully visible
- [ ] Math renders correctly
- [ ] Page count reasonable
- [ ] All sections present