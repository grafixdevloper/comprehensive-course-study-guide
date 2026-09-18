/**
 * Flowchart Diagram Generator
 * Generates flowchart diagrams as SVG
 */

const FlowchartGenerator = {
  /**
   * Generate a flowchart diagram from specification
   * @param {Object} spec - Diagram specification
   * @returns {SVGElement} SVG diagram
   */
  generate(spec) {
    const {
      nodes = [],
      edges = [],
      layout = 'top-down', // top-down, left-right
      width = 800,
      height = 600,
      title = '',
      nodeDefaults = {}
    } = spec;

    if (!nodes.length) {
      return DiagramUtils.createPlaceholderDiagram({ type: 'flowchart', description: 'No nodes defined' });
    }

    const svg = DiagramUtils.createSVG(width, height);
    svg.setAttribute('class', 'flowchart-diagram');

    // Add title
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

    // Create arrow marker
    const arrowId = `arrow-fc-${Date.now()}`;
    DiagramUtils.createArrowMarker(svg, arrowId, DiagramUtils.styles.colors.arrow, 8);

    // Layout nodes
    const positionedNodes = this.layoutNodes(nodes, edges, layout, width, height);

    // Draw edges
    this.drawEdges(svg, positionedNodes, edges, arrowId);

    // Draw nodes
    this.drawNodes(svg, positionedNodes, nodeDefaults);

    return svg;
  },

  /**
   * Layout nodes for flowchart
   */
  layoutNodes(nodes, edges, layout, width, height) {
    const nodeMap = {};
    nodes.forEach(n => nodeMap[n.id] = { ...n });

    // Build adjacency
    const children = {};
    const parents = {};
    nodes.forEach(n => {
      children[n.id] = [];
      parents[n.id] = [];
    });
    edges.forEach(e => {
      if (!children[e.from]) children[e.from] = [];
      if (!parents[e.to]) parents[e.to] = [];
      children[e.from].push(e.to);
      parents[e.to].push(e.from);
    });

    // Find roots (nodes with no parents)
    const roots = nodes.filter(n => parents[n.id].length === 0);
    if (roots.length === 0) roots.push(nodes[0]);

    // Assign levels using BFS from roots
    const levels = {};
    const queue = [...roots.map(r => ({ id: r.id, level: 0 }))];
    const visited = new Set();

    while (queue.length) {
      const { id, level } = queue.shift();
      if (visited.has(id)) continue;
      visited.add(id);
      levels[id] = level;

      (children[id] || []).forEach(childId => {
        if (!visited.has(childId)) {
          queue.push({ id: childId, level: level + 1 });
        }
      });
    }

    // Add unvisited nodes
    nodes.forEach(n => {
      if (!(n.id in levels)) levels[n.id] = 0;
    });

    // Group by level
    const levelGroups = {};
    Object.entries(levels).forEach(([id, level]) => {
      if (!levelGroups[level]) levelGroups[level] = [];
      levelGroups[level].push(id);
    }

    // Position nodes
    const maxLevel = Math.max(...Object.values(levels));
    const levelHeight = (height - 100) / (maxLevel + 1);

    const positioned = [];
    Object.entries(levelGroups).forEach(([level, ids]) => {
      const levelWidth = width / (ids.length + 1);
      ids.forEach((id, idx) => {
        const node = nodeMap[id];
        if (layout === 'top-down') {
          node.x = (idx + 1) * levelWidth;
          node.y = 60 + level * levelHeight;
        } else {
          node.x = 60 + level * levelWidth;
          node.y = (idx + 1) * levelHeight;
        }
        positioned.push(node);
      });
    });

    return positioned;
  },

  /**
   * Draw edges between nodes
   */
  drawEdges(svg, nodes, edges, arrowId) {
    const nodeMap = {};
    nodes.forEach(n => nodeMap[n.id] = n);

    edges.forEach(edge => {
      const from = nodeMap[edge.from];
      const to = nodeMap[edge.to];
      if (!from || !to) return;

      const path = this.getEdgePath(from, to, edge);
      if (!path) return;

      const pathEl = DiagramUtils.createPath(path, {
        'stroke': DiagramUtils.styles.colors.arrow,
        'stroke-width': 1.5,
        'fill': 'none',
        'marker-end': arrowId,
        'stroke-dasharray': edge.style === 'dashed' ? '5,3' : 'none'
      });
      svg.appendChild(pathEl);

      // Edge label
      if (edge.label) {
        this.addEdgeLabel(svg, from, to, edge.label);
      }
    });
  },

  /**
   * Get path for edge between two nodes
   */
  getEdgePath(from, to, edge) {
    // Node dimensions
    const w = from.width || 120;
    const h = from.height || 50;

    // Connection points (center of edges)
    let fromX, fromY, toX, toY;

    if (from.x < to.x) { // left to right
      fromX = from.x + w/2;
      fromY = from.y + h/2;
      toX = to.x - w/2;
      toY = to.y + h/2;
    } else if (from.x > to.x) { // right to left
      fromX = from.x - w/2;
      fromY = from.y + h/2;
      toX = to.x + w/2;
      toY = to.y + h/2;
    } else if (from.y < to.y) { // top to bottom
      fromX = from.x;
      fromY = from.y + h/2;
      toX = to.x;
      toY = to.y - h/2;
    } else { // bottom to top
      fromX = from.x;
      fromY = from.y - h/2;
      toX = to.x;
      toY = to.y + h/2;
    }

    // Straight line with optional curve for parallel edges
    const dx = toX - fromX;
    const dy = toY - fromY;

    // Check for parallel edges
    const parallelEdges = edges.filter(e =>
      (e.from === edge.from && e.to === edge.to) ||
      (e.from === edge.to && e.to === edge.from)
    );

    if (parallelEdges.length > 1) {
      const idx = parallelEdges.findIndex(e => e === edge);
      const offset = (idx - (parallelEdges.length - 1) / 2) * 20;
      const midX = (fromX + toX) / 2 - dy * offset / Math.sqrt(dx*dx + dy*dy);
      const midY = (fromY + toY) / 2 + dx * offset / Math.sqrt(dx*dx + dy*dy);
      return `M${fromX},${fromY} Q${midX},${midY} ${toX},${toY}`;
    }

    return `M${fromX},${fromY} L${toX},${toY}`;
  },

  /**
   * Add label to edge
   */
  addEdgeLabel(svg, from, to, label) {
    const midX = (from.x + to.x) / 2;
    const midY = (from.y + to.y) / 2 - 10;

    const textEl = DiagramUtils.createText(midX, midY, label, {
      'text-anchor': 'middle',
      'dominant-baseline': 'middle',
      'font-size': '10',
      'font-family': 'JetBrains Mono, monospace',
      'fill': DiagramUtils.styles.colors.text,
      'font-weight': '500',
      'paint-order': 'stroke',
      'stroke': 'white',
      'stroke-width': '3'
    });
    svg.appendChild(textEl);
  },

  /**
   * Draw nodes
   */
  drawNodes(svg, nodes, defaults) {
    nodes.forEach(node => {
      const shape = node.shape || defaults.shape || 'rectangle';
      const width = node.width || defaults.width || 120;
      const height = node.height || defaults.height || 50;
      const x = node.x - width / 2;
      const y = node.y - height / 2;
      const fill = node.fill || defaults.fill || DiagramUtils.styles.colors.surface;
      const stroke = node.stroke || defaults.stroke || DiagramUtils.styles.colors.primary;
      const strokeWidth = node.strokeWidth || defaults.strokeWidth || 2;
      const radius = node.radius || defaults.radius || 8;

      const g = DiagramUtils.createGroup('node');
      g.setAttribute('transform', `translate(${x}, ${y})`);

      // Draw shape
      let shapeEl;
      switch (shape) {
        case 'ellipse':
        case 'oval':
          shapeEl = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
          shapeEl.setAttribute('cx', width/2);
          shapeEl.setAttribute('cy', height/2);
          shapeEl.setAttribute('rx', width/2);
          shapeEl.setAttribute('ry', height/2);
          break;
        case 'diamond':
          shapeEl = DiagramUtils.createPath(
            `M${width/2},0 L${width},${height/2} L${width/2},${height} L0,${height/2} Z`
          );
          break;
        case 'parallelogram':
          const offset = 15;
          shapeEl = DiagramUtils.createPath(
            `M${offset},0 L${width},0 L${width-offset},${height} L0,${height} Z`
          );
          break;
        case 'rounded':
        case 'rectangle':
        default:
          shapeEl = DiagramUtils.createRect(0, 0, width, height, { rx: radius, ry: radius });
          break;
      }

      shapeEl.setAttribute('fill', fill);
      shapeEl.setAttribute('stroke', stroke);
      shapeEl.setAttribute('stroke-width', strokeWidth);
      g.appendChild(shapeEl);

      // Node label
      const label = node.label || node.id;
      const lines = this.wrapText(label, width - 20);
      lines.forEach((line, i) => {
        const textEl = DiagramUtils.createText(width/2, height/2 - (lines.length - 1) * 7 + i * 14, line, {
          'text-anchor': 'middle',
          'dominant-baseline': 'middle',
          'font-size': '11',
          'font-family': 'Inter, sans-serif',
          'font-weight': '500',
          'fill': DiagramUtils.styles.colors.text
        });
        g.appendChild(textEl);
      });

      svg.appendChild(g);
    });
  },

  /**
   * Wrap text to fit in node
   */
  wrapText(text, maxWidth) {
    // Simple word wrap - in production, measure text
    const words = text.split(' ');
    const lines = [];
    let current = '';

    words.forEach(word => {
      if ((current + ' ' + word).length > maxWidth / 6) { // rough char width
        lines.push(current);
        current = word;
      } else {
        current += (current ? ' ' : '') + word;
      }
    });
    if (current) lines.push(current);
    return lines;
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = FlowchartGenerator;
}

window.DiagramGenerators = window.DiagramGenerators || {};
window.DiagramGenerators.flowchart = FlowchartGenerator.generate.bind(FlowchartGenerator);