/**
 * Automata Diagram Generator
 * Generates DFA/NFA/ε-NFA diagrams as SVG
 */

const AutomataGenerator = {
  /**
   * Generate an automaton diagram from specification
   * @param {Object} spec - Diagram specification
   * @returns {SVGElement} SVG diagram
   */
  generate(spec) {
    const {
      states = [],
      alphabet = ['0', '1'],
      transitions = [],
      start = null,
      accept = [],
      type = 'DFA', // DFA, NFA, epsilon-NFA
      layout = 'auto', // auto, circle, grid, force
      width = 800,
      height = 500,
      title = '',
      showAlphabet = true
    } = spec;

    // Validate
    if (!states.length) {
      return DiagramUtils.createPlaceholderDiagram({ type: 'automaton', description: 'No states defined' });
    }

    // Create SVG
    const svg = DiagramUtils.createSVG(width, height);
    svg.setAttribute('class', 'automaton-diagram');

    // Add title if provided
    if (title) {
      const titleEl = DiagramUtils.createText(width / 2, 30, title, {
        'text-anchor': 'middle',
        'font-size': '16',
        'font-weight': 'bold',
        'font-family': 'Inter, sans-serif',
        'fill': DiagramUtils.styles.colors.primary
      });
      svg.appendChild(titleEl);
    }

    // Layout states
    const positionedStates = this.layoutStates(states, transitions, layout, width, height);

    // Create arrow marker
    const arrowId = `arrow-${Date.now()}`;
    DiagramUtils.createArrowMarker(svg, arrowId, DiagramUtils.styles.colors.arrow, DiagramUtils.styles.arrow.size);

    // Draw transitions first (so they appear behind states)
    this.drawTransitions(svg, positionedStates, transitions, arrowId, type);

    // Draw states
    this.drawStates(svg, positionedStates, start, accept);

    // Add legend
    this.addLegend(svg, width, height, type, showAlphabet);

    return svg;
  },

  /**
   * Layout states based on algorithm
   */
  layoutStates(states, transitions, layout, width, height) {
    const stateObjects = states.map((s, i) => ({
      id: typeof s === 'string' ? s : s.id,
      label: typeof s === 'string' ? s : (s.label || s.id),
      isStart: false,
      isAccept: false
    }));

    switch (layout) {
      case 'circle':
        return DiagramUtils.layoutCircle(stateObjects, width / 2, height / 2, Math.min(width, height) / 3);
      case 'grid':
        const cols = Math.ceil(Math.sqrt(stateObjects.length));
        return DiagramUtils.layoutGrid(stateObjects, cols, 180, 100, 100);
      case 'force':
        return DiagramUtils.layoutForce(stateObjects, transitions, width, height);
      case 'auto':
      default:
        // Try to use a smart layout based on transition structure
        return this.smartLayout(stateObjects, transitions, width, height);
    }
  },

  /**
   * Smart layout that tries to arrange states linearly for simple automata
   */
  smartLayout(states, transitions, width, height) {
    // Build adjacency
    const adj = {};
    states.forEach(s => adj[s.id] = []);

    transitions.forEach(t => {
      if (!adj[t.from]) adj[t.from] = [];
      adj[t.from].push(t.to);
      if (!adj[t.to]) adj[t.to] = [];
    });

    // Find start state (or first state)
    const startState = states.find(s => s.isStart) || states[0];

    // BFS from start to get levels
    const visited = new Set();
    const levels = [];
    const queue = [{ id: startState.id, level: 0 }];

    while (queue.length) {
      const { id, level } = queue.shift();
      if (visited.has(id)) continue;
      visited.add(id);

      if (!levels[level]) levels[level] = [];
      levels[level].push(id);

      (adj[id] || []).forEach(neighbor => {
        if (!visited.has(neighbor)) {
          queue.push({ id: neighbor, level: level + 1 });
        }
      });
    }

    // Add any unvisited states
    states.forEach(s => {
      if (!visited.has(s.id)) {
        if (!levels[levels.length]) levels[levels.length] = [];
        levels[levels.length].push(s.id);
      }
    });

    // Position states
    const positioned = [];
    const levelHeight = height / (levels.length + 1);
    const startY = levelHeight;

    levels.forEach((level, levelIdx) => {
      const levelWidth = width / (level.length + 1);
      level.forEach((stateId, stateIdx) => {
        const state = states.find(s => s.id === stateId);
        if (state) {
          positioned.push({
            ...state,
            x: (stateIdx + 1) * levelWidth,
            y: startY + levelIdx * levelHeight
          });
        }
      });
    });

    return positioned;
  },

  /**
   * Draw transitions
   */
  drawTransitions(svg, states, transitions, arrowId, type) {
    const stateMap = {};
    states.forEach(s => stateMap[s.id] = s);
    const R = DiagramUtils.styles.state.radius;

    // Group transitions by from->to pair for multi-label edges
    const edgeGroups = {};
    transitions.forEach(t => {
      const key = `${t.from}->${t.to}`;
      if (!edgeGroups[key]) edgeGroups[key] = [];
      edgeGroups[key].push(t.symbol || t.label || 'ε');
    });

    Object.entries(edgeGroups).forEach(([key, symbols]) => {
      const [fromId, toId] = key.split('->');
      const from = stateMap[fromId];
      const to = stateMap[toId];

      if (!from || !to) return;

      const isSelfLoop = fromId === toId;
      let path;

      if (isSelfLoop) {
        // Determine best direction for self-loop
        const dir = this.getSelfLoopDirection(from, states);
        path = DiagramUtils.calculateSelfLoopPath(from.x, from.y, R, dir);
      } else {
        // Check if reverse edge exists for curved arrows
        const reverseKey = `${toId}->${fromId}`;
        const hasReverse = edgeGroups[reverseKey] && reverseKey !== key;
        const curve = hasReverse ? 50 : 0;
        path = DiagramUtils.calculateArrowPath(from.x, from.y, to.x, to.y, R, R, 0, curve);
      }

      if (!path) return;

      // Draw path
      const pathEl = DiagramUtils.createPath(path, {
        'stroke': DiagramUtils.styles.transition.stroke,
        'stroke-width': DiagramUtils.styles.transition.strokeWidth,
        'fill': 'none',
        'marker-end': arrowId
      });
      svg.appendChild(pathEl);

      // Add label
      this.addTransitionLabel(svg, path, symbols.join(', '), isSelfLoop, from, to);
    });
  },

  /**
   * Determine best direction for self-loop
   */
  getSelfLoopDirection(state, allStates) {
    // Find nearby states to avoid overlap
    const directions = ['top', 'right', 'bottom', 'left'];
    const R = DiagramUtils.styles.state.radius + 40;

    for (const dir of directions) {
      let hasConflict = false;
      const angles = { top: -Math.PI/2, right: 0, bottom: Math.PI/2, left: Math.PI };
      const angle = angles[dir];
      const lx = state.x + Math.cos(angle) * R;
      const ly = state.y + Math.sin(angle) * R;

      for (const other of allStates) {
        if (other.id === state.id) continue;
        const dist = Math.sqrt((other.x - lx)**2 + (other.y - ly)**2);
        if (dist < R * 2) {
          hasConflict = true;
          break;
        }
      }

      if (!hasConflict) return dir;
    }

    return 'top'; // default
  },

  /**
   * Add transition label along path
   */
  addTransitionLabel(svg, pathStr, label, isSelfLoop, from, to) {
    // Simple midpoint labeling - for production, use path textPath
    let labelX, labelY;

    if (isSelfLoop) {
      const R = DiagramUtils.styles.state.radius + 40;
      labelX = from.x;
      labelY = from.y - R - 10;
    } else {
      // Approximate midpoint
      labelX = (from.x + to.x) / 2;
      labelY = (from.y + to.y) / 2 - 15;
    }

    // Background for label
    const textEl = DiagramUtils.createText(labelX, labelY, label, {
      'text-anchor': 'middle',
      'dominant-baseline': 'middle',
      'font-size': DiagramUtils.styles.transition.fontSize,
      'font-family': DiagramUtils.styles.transition.fontFamily,
      'fill': DiagramUtils.styles.transition.stroke,
      'font-weight': '500',
      'paint-order': 'stroke',
      'stroke': 'white',
      'stroke-width': '3'
    });
    svg.appendChild(textEl);
  },

  /**
   * Draw states
   */
  drawStates(svg, states, startId, acceptIds) {
    const R = DiagramUtils.styles.state.radius;
    const acceptSet = new Set(acceptIds || []);

    states.forEach(state => {
      const isStart = state.id === startId;
      const isAccept = acceptSet.has(state.id);

      const g = DiagramUtils.createGroup('state');
      g.setAttribute('transform', `translate(${state.x}, ${state.y})`);

      if (isAccept) {
        // Double circle for accept states
        const outer = DiagramUtils.createCircle(0, 0, R, {
          'fill': DiagramUtils.styles.acceptState.fill,
          'stroke': DiagramUtils.styles.acceptState.stroke,
          'stroke-width': DiagramUtils.styles.acceptState.strokeWidth
        });
        const inner = DiagramUtils.createCircle(0, 0, R - 6, {
          'fill': 'none',
          'stroke': DiagramUtils.styles.acceptState.stroke,
          'stroke-width': DiagramUtils.styles.acceptState.strokeWidth
        });
        g.appendChild(outer);
        g.appendChild(inner);
      } else {
        // Single circle
        const circle = DiagramUtils.createCircle(0, 0, R, {
          'fill': isStart ? DiagramUtils.styles.startState.fill : DiagramUtils.styles.state.fill,
          'stroke': isStart ? DiagramUtils.styles.startState.stroke : DiagramUtils.styles.state.stroke,
          'stroke-width': isStart ? DiagramUtils.styles.startState.strokeWidth : DiagramUtils.styles.state.strokeWidth
        });
        g.appendChild(circle);
      }

      // State label
      const label = DiagramUtils.createText(0, 4, state.label || state.id, {
        'text-anchor': 'middle',
        'dominant-baseline': 'middle',
        'font-size': DiagramUtils.styles.state.fontSize,
        'font-family': DiagramUtils.styles.state.fontFamily,
        'font-weight': DiagramUtils.styles.state.fontWeight,
        'fill': DiagramUtils.styles.colors.text
      });
      g.appendChild(label);

      // Start arrow
      if (isStart) {
        const arrowX = -R - 15;
        const arrowY = 0;
        const startArrow = DiagramUtils.createPath(
          `M${arrowX - 15},${arrowY - 8} L${arrowX},${arrowY} L${arrowX - 15},${arrowY + 8}`,
          {
            'fill': 'none',
            'stroke': DiagramUtils.styles.colors.start,
            'stroke-width': 2
          }
        );
        g.appendChild(startArrow);

        const startLabel = DiagramUtils.createText(arrowX - 25, arrowY + 4, 'start', {
          'text-anchor': 'end',
          'dominant-baseline': 'middle',
          'font-size': 10,
          'font-family': 'Inter, sans-serif',
          'fill': DiagramUtils.styles.colors.start,
          'font-weight': 'bold'
        });
        g.appendChild(startLabel);
      }

      svg.appendChild(g);
    });
  },

  /**
   * Add legend
   */
  addLegend(svg, width, height, type, showAlphabet) {
    const legendItems = [
      { label: 'Start State', color: DiagramUtils.styles.colors.start, shape: 'arrow' },
      { label: 'Accept State', color: DiagramUtils.styles.colors.accept, shape: 'double-circle' },
      { label: 'Regular State', color: DiagramUtils.styles.colors.primary, shape: 'circle' }
    ];

    if (type === 'NFA' || type === 'epsilon-NFA') {
      legendItems.push({ label: 'ε-transition', color: DiagramUtils.styles.colors.accent, shape: 'dashed' });
    }

    const legendX = 20;
    let legendY = height - legendItems.length * 25 - 20;

    const legendGroup = DiagramUtils.createGroup('legend');
    legendGroup.setAttribute('transform', `translate(${legendX}, ${legendY})`);

    // Background
    const bg = DiagramUtils.createRect(-5, -5, 180, legendItems.length * 25 + 10, {
      'fill': 'rgba(255,255,255,0.9)',
      'stroke': DiagramUtils.styles.colors.border,
      'stroke-width': 1,
      'rx': 5
    });
    legendGroup.appendChild(bg);

    legendItems.forEach((item, i) => {
      const y = i * 25;

      if (item.shape === 'arrow') {
        const arrow = DiagramUtils.createPath('M0,-5 L15,0 L0,5', {
          'fill': 'none',
          'stroke': item.color,
          'stroke-width': 2
        });
        legendGroup.appendChild(arrow);
      } else if (item.shape === 'double-circle') {
        const outer = DiagramUtils.createCircle(8, 0, 8, {
          'fill': 'none',
          'stroke': item.color,
          'stroke-width': 2
        });
        const inner = DiagramUtils.createCircle(8, 0, 4, {
          'fill': 'none',
          'stroke': item.color,
          'stroke-width': 2
        });
        legendGroup.appendChild(outer);
        legendGroup.appendChild(inner);
      } else if (item.shape === 'circle') {
        const circle = DiagramUtils.createCircle(8, 0, 8, {
          'fill': 'white',
          'stroke': item.color,
          'stroke-width': 2
        });
        legendGroup.appendChild(circle);
      } else if (item.shape === 'dashed') {
        const line = DiagramUtils.createLine(0, 0, 16, 0, {
          'stroke': item.color,
          'stroke-width': 2,
          'stroke-dasharray': '4,2'
        });
        legendGroup.appendChild(line);
      }

      const label = DiagramUtils.createText(25, 4, item.label, {
        'font-size': '11',
        'font-family': 'Inter, sans-serif',
        'fill': DiagramUtils.styles.colors.text,
        'dominant-baseline': 'middle'
      });
      legendGroup.appendChild(label);
    });

    svg.appendChild(legendGroup);
  }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AutomataGenerator;
}

window.DiagramGenerators = window.DiagramGenerators || {};
window.DiagramGenerators.automaton = AutomataGenerator.generate.bind(AutomataGenerator);