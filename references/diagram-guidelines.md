# Diagram Guidelines

## Overview
Standards and best practices for generating technical diagrams in the study guide.

## Core Principles

### 1. Correctness Over Aesthetics
- Technical accuracy is paramount
- Labels, symbols, topology must be exact
- Mathematical relationships must be precise
- Visual decoration is secondary

### 2. SVG as Primary Format
- Vector-based (infinite scalability)
- Sharp at any resolution/print size
- Programmatically generated (deterministic)
- Styleable via CSS
- Accessible (text is selectable)

### 3. Deterministic Generation
- Same input → identical output
- No random layout (unless seeded)
- Reproducible across runs
- Version controllable

## Diagram Types & Use Cases

| Type | Generator | Use Cases |
|------|-----------|-----------|
| Automaton | automata.js | DFA, NFA, ε-NFA, state machines |
| Flowchart | flowcharts.js | Algorithms, procedures, decision flows |
| Block Diagram | block-diagrams.js | System architecture, data flow, components |
| Graph | graphs.js | Networks, dependencies, relationships |
| Tree | trees.js | Parse trees, decision trees, hierarchies |
| Timeline | process-diagrams.js | Historical progression, process steps |
| Sequence | process-diagrams.js | Protocol interactions, lifelines |

## Automaton Diagrams (DFA/NFA/ε-NFA)

### Node Representation
```
Regular State:     ○ (circle, 28pt radius)
Start State:       ○ with incoming arrow labeled "start"
Accept State:      ⦿ (double circle, 28pt + 22pt radii)
Trap/Dead State:   ○ with "⊥" or "dead" label
```

### Edge Representation
```
Transition:        ───► (solid arrow, 1.5pt)
ε-Transition:      ╌► (dashed arrow, 1.5pt)
Label:             Centered on edge, offset 8pt
Multiple labels:   Comma-separated: "0, 1"
Self-loop:         Curved arrow (40pt radius), labeled at top
```

### Layout Algorithm
1. **Smart Layout** (default): BFS from start state, level-based
2. **Circle**: Evenly spaced on circle
3. **Grid**: Rectangular grid
4. **Force-directed**: For complex automata

### Styling Constants
```javascript
const STYLES = {
  state: {
    radius: 28,
    fill: '#ffffff',
    stroke: '#1a3c5e',
    strokeWidth: 2,
    fontSize: 13,
    fontFamily: 'Inter, sans-serif',
    fontWeight: 600
  },
  startState: {
    stroke: '#27ae60',
    strokeWidth: 3
  },
  acceptState: {
    stroke: '#c0392b',
    doubleCircle: true,
    innerRadius: 22
  },
  transition: {
    stroke: '#333',
    strokeWidth: 1.5,
    fontSize: 11,
    fontFamily: 'JetBrains Mono, monospace',
    labelBackground: 'rgba(255,255,255,0.9)',
    labelPadding: 3
  },
  arrow: {
    size: 8,
    color: '#333'
  }
};
```

### Required Elements
- Legend (start, accept, regular, ε-transition if applicable)
- State labels (q0, q1, etc. or descriptive)
- Transition labels (input symbols)
- Start arrow
- Title/caption

### Example Spec
```json
{
  "type": "automaton",
  "title": "DFA for Strings Ending in 01",
  "states": ["q0", "q1", "q2"],
  "alphabet": ["0", "1"],
  "transitions": [
    {"from": "q0", "to": "q1", "symbol": "0"},
    {"from": "q0", "to": "q0", "symbol": "1"},
    {"from": "q1", "to": "q1", "symbol": "0"},
    {"from": "q1", "to": "q2", "symbol": "1"},
    {"from": "q2", "to": "q1", "symbol": "0"},
    {"from": "q2", "to": "q0", "symbol": "1"}
  ],
  "start": "q0",
  "accept": ["q2"],
  "type": "DFA"
}
```

## Flowcharts

### Node Shapes
| Shape | Use Case |
|-------|----------|
| Rectangle | Process step |
| Diamond | Decision |
| Ellipse | Start/End |
| Parallelogram | Input/Output |
| Rounded Rect | Subroutine |

### Connections
- Orthogonal routing (Manhattan style)
- Arrowheads on all edges
- Labels on decision branches (Yes/No)

### Layout
- Top-down for algorithms
- Left-right for data flow
- Minimum 50pt node spacing

## Block Diagrams

### Block Types
| Type | Color | Use Case |
|------|-------|----------|
| Input | #3498db (blue) | Data sources, user input |
| Process | #27ae60 (green) | Computation, transformation |
| Output | #e67e22 (orange) | Results, display |
| Storage | #8e44ad (purple) | Databases, memory |
| Decision | #c0392b (red) | Branching logic |

### Ports
- Named ports (top, bottom, left, right)
- Labels on connections
- Orthogonal routing with Manhattan bends

## Graphs

### Node Styles
- Circles (default, 20pt radius)
- Labels centered
- Optional values below label

### Edge Styles
- Directed: Arrowhead
- Undirected: No arrowhead
- Weighted: Label with weight
- Parallel: Curved offset

### Layouts
- Force-directed (default)
- Circular
- Hierarchical (if DAG)

## Trees

### Types
- **Binary**: Left/right children
- **General**: Multiple children
- **Parse**: Terminals (green) vs Non-terminals (blue)
- **Decision**: Diamond internal nodes

### Layouts
- **Top-down**: Root at top, children below (Reingold-Tilford)
- **Left-right**: Root left, children right
- **Radial**: Root center, children radiating

### Node Shapes
| Type | Shape | Color |
|------|-------|-------|
| Terminal | Circle | Green (#27ae60) |
| Non-terminal | Circle | Blue (#3498db) |
| Epsilon | Circle | Orange (#e67e22) |
| Decision | Diamond | Red (#c0392b) |

## SVG Technical Requirements

### Viewport & Sizing
```xml
<svg width="800" height="500" viewBox="0 0 800 500" 
     xmlns="http://www.w3.org/2000/svg">
```
- Explicit width/height for initial render
- viewBox for scaling
- Responsive via CSS: `max-width: 100%; height: auto;`

### Font Handling
- Use system fonts (Inter, JetBrains Mono)
- Embed as `<text>` elements (not paths)
- Minimum font size: 9pt
- `text-anchor: middle` for centered labels
- `dominant-baseline: middle` for vertical centering

### Arrow Markers
```xml
<defs>
  <marker id="arrow-1" markerWidth="8" markerHeight="8" 
          refX="7" refY="4" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L8,4 L0,8 Z" fill="#333"/>
  </marker>
</defs>
```
- Define once in `<defs>`
- Reference via `marker-end="url(#arrow-1)"`
- `markerUnits="strokeWidth"` for scaling

### Clipping & Overflow
- No clipping by default
- `overflow: visible` on SVG
- Container handles sizing

### Accessibility
```xml
<title>DFA for strings ending in 01</title>
<desc>Three-state DFA with states q0, q1, q2. q0 is start. q2 is accept.</desc>
```
- `<title>` for tooltip
- `<desc>` for screen readers
- Semantic grouping with `<g class="state">`

## CSS Styling for Diagrams

### Container
```css
.diagram-container {
  text-align: center;
  margin: 1.5rem 0;
  page-break-inside: avoid;
  break-inside: avoid;
}

.diagram-container svg {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}
```

### Print Optimization
```css
@media print {
  .diagram-container svg {
    max-width: 100% !important;
    max-height: 60vh;
  }
  
  svg {
    shape-rendering: geometricPrecision;
    text-rendering: geometricPrecision;
  }
}
```

### Dark Mode
```css
@media (prefers-color-scheme: dark) {
  .diagram-container svg {
    filter: invert(1) hue-rotate(180deg);
  }
  .diagram-container svg image {
    filter: invert(1) hue-rotate(180deg);
  }
}
```

## Quality Checklist

### Before Generation
- [ ] Spec matches source material exactly
- [ ] All states/transitions accounted for
- [ ] Labels use correct notation (ε not epsilon)
- [ ] Accept states marked correctly
- [ ] Start state indicated

### After Generation
- [ ] Renders at 100% without clipping
- [ ] Text readable at 75% zoom
- [ ] Arrows visible and correctly oriented
- [ ] No overlapping labels
- [ ] Legend present and accurate
- [ ] Caption descriptive

### Print Validation
- [ ] Scales to page width
- [ ] No pixelation at 300 DPI
- [ ] Colors work in grayscale
- [ ] Text not inverted in dark mode
- [ ] Fits within margins

## Common Patterns

### DFA for Suffix Language
```
Pattern: Strings ending in "xyz"
States: q0 (start), q1 (matched x), q2 (matched xy), q3 (matched xyz - accept)
Transitions: Build prefix function (KMP-style)
```

### NFA to DFA (Subset Construction)
- Show ε-closures
- Label DFA states with NFA state sets
- Highlight accept states (contain NFA accept)

### Product Construction (Intersection)
- Grid layout
- States as pairs (q1, q2)
- Transitions synchronized

### Pumping Lemma Proof
- String decomposition: xyz
- Show |xy| ≤ p, |y| > 0
- Show xy^iz ∉ L for some i

## Generator API

### Standard Interface
```javascript
generate(spec) → SVGElement
```

### Spec Schema
```json
{
  "type": "automaton|flowchart|block-diagram|graph|tree|timeline|sequence",
  "title": "Optional title",
  "width": 800,
  "height": 500,
  ...type-specific fields
}
```

### Registration
```javascript
window.DiagramGenerators = {
  automaton: AutomataGenerator.generate,
  flowchart: FlowchartGenerator.generate,
  blockDiagram: BlockDiagramGenerator.generate,
  graph: GraphGenerator.generate,
  tree: TreeGenerator.generate,
  timeline: ProcessDiagramGenerator.generate,
  process: ProcessDiagramGenerator.generate,
  sequence: ProcessDiagramGenerator.generate
};
```

## Testing

### Unit Tests
- Each generator with known inputs
- Snapshot comparison of SVG output
- Edge cases: empty, single node, self-loops

### Visual Regression
- Render to PNG at multiple sizes
- Compare against baseline
- Test print CSS

### Correctness Tests
- Automaton: Verify language acceptance
- Flowchart: Verify reachability
- Graph: Verify connectivity

## Future Extensions

- Interactive diagrams (HTML version only)
- Animation for algorithm steps
- Parameterized families (e.g., DFA for any suffix)
- Export to TikZ/LaTeX for alternative rendering
- Diagram versioning in content model