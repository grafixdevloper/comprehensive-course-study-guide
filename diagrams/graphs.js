/**
 * Graph Diagram Generator
 * Generates graph diagrams (directed/undirected) as SVG
 */

const GraphGenerator = {
  /**
   * Generate a graph diagram from specification
   * @param {Object} spec - Diagram specification
   * @returns {SVGElement} SVG diagram
   */
  generate(spec) {
    const {
      nodes = [],
      edges = [],
      directed = true,
      weighted = false,
      layout = 'force', // force, circle, grid
      width = 800,
      height = 600,
      title = '',
      nodeDefaults = {}
    } = spec;

    if (!nodes.length) {
      return DiagramUtils.createPlaceholderDiagram({ type: 'graph', description: 'No nodes defined' });
    }

    const svg = DiagramUtils.createSVG(width, height);
    svg.setAttribute('class', 'graph-diagram');

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

    // Create arrow marker for directed edges
    const arrowId = `arrow-gr-${Date.now()}`;
    if (directed) {
      DiagramUtils.createArrowMarker(svg, arrowId, DiagramUtils.styles.colors.arrow, 7);
    }

    // Layout nodes
    const positionedNodes = this.layoutNodes(nodes, edges, layout, width, height);

    // Draw edges
    this.drawEdges(svg, positionedNodes, edges, arrowId, directed, weighted);

    // Draw nodes
    this.drawNodes(svg, positionedNodes, nodeDefaults);

    return svg;
  },

  /**
   * Layout nodes
   */
  layoutNodes(nodes, edges, layout, width, height) {
    const nodeMap = {};
    nodes.forEach(n => nodeMap[n.id] = { ...n });

    if (layout === 'circle') {
      return DiagramUtils.layoutCircle(
        Object.values(nodeMap),
        width / 2,
        height / 2,
        Math.min(width, height) / 2.5
      );
    } else if (layout === 'grid') {
      const cols = Math.ceil(Math.sqrt(nodes.length));
      return DiagramUtils.layoutGrid(Object.values(nodeMap), cols, 150, 100, 100);
    } else {
      // Force-directed layout
      return DiagramUtils.layoutForce(Object.values(nodeMap), edges, width, height);
    }
  },

  /**
   * Draw edges
   */
  drawEdges(svg, nodes, edges, arrowId, directed, weighted) {
    const nodeMap = {};
    nodes.forEach(n => nodeMap[n.id] = n);

    // Group parallel edges
    const edgeGroups = {};
    edges.forEach(edge => {
      const key = directed ? `${edge.from}->${edge.to}` : [edge.from, edge.to].sort().join('-');
      if (!edgeGroups[key]) edgeGroups[key] = [];
      edgeGroups[key].push(edge);
    });

    Object.entries(edgeGroups).forEach(([key, group]) => {
      const [fromId, toId] = directed ? key.split('->') : key.split('-');
      const from = nodeMap[fromId];
      const to = nodeMap[toId];
      if (!from || !to) return;

      const isSelfLoop = fromId === toId;
      const R = 20; // node radius

      let path;
      if (isSelfLoop) {
        path = DiagramUtils.calculateSelfLoopPath(from.x, from.y, R, 'top', 30);
      } else {
        // Check for reverse edge
        const reverseKey = directed ? `${toId}->${fromId}` : key;
        const hasReverse = directed && edgeGroups[reverseKey] && reverseKey !== key;
        const curve = hasReverse ? 40 : 0;
        path = DiagramUtils.calculateArrowPath(from.x, from.y, to.x, to.y, R, R, 0, curve);
      }

      if (!path) return;

      // Draw each edge in group with offset for parallel edges
      group.forEach((edge, idx) => {
        let edgePath = path;
        if (group.length > 1 && !isSelfLoop) {
          // Offset parallel edges
          const offset = (idx - (group.length - 1) / 2) * 15;
          edgePath = this.offsetPath(path, offset, from, to);
        }

        const pathEl = DiagramUtils.createPath(edgePath, {
          'stroke': edge.color || DiagramUtils.styles.colors.arrow,
          'stroke-width': edge.width || 1.5,
          'fill': 'none',
          'marker-end': directed ? arrowId : 'none',
          'stroke-dasharray': edge.style === 'dashed' ? '5,3' : 'none',
          'opacity': edge.opacity || 1
        });
        svg.appendChild(pathEl);

        // Edge label (weight or custom label)
        const label = weighted && edge.weight !== undefined ? String(edge.weight) : edge.label;
        if (label) {
          this.addEdgeLabel(svg, edgePath, from, to, label, idx, group.length);
        }
      });
    });
  },

  /**
   * Offset a path for parallel edges
   */
  offsetPath(pathStr, offset, from, to) {
    // For simplicity, just add a slight curve in opposite direction
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist === 0) return pathStr;

    const ux = dx / dist;
    const uy = dy / dist;
    const midX = (from.x + to.x) / 2 - uy * offset;
    const midY = (from.y + to.y) / 2 + ux * offset;

    return `M${from.x},${from.y} Q${midX},${midY} ${to.x},${to.y}`;
  },

  /**
   * Add edge label
   */
  addEdgeLabel(svg, pathStr, from, to, label, idx, total) {
    // Calculate midpoint
    let labelX, labelY;

    if (from.id === to.id) {
      labelX = from.x;
      labelY = from.y - 50;
    } else {
      labelX = (from.x + to.x) / 2;
      labelY = (from.y + to.y) / 2;

      // Offset for parallel edges
      if (total > 1) {
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist > 0) {
          const ux = -dy / dist;
          const uy = dx / dist;
          labelX += ux * (idx - (total - 1) / 2) * 15;
          labelY += uy * (idx - (total - 1) / 2) * 15;
        }
      }
      labelY -= 10;
    }

    const textEl = DiagramUtils.createText(labelX, labelY, label, {
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
    const R = defaults.radius || 20;

    nodes.forEach(node => {
      const fill = node.fill || defaults.fill || DiagramUtils.styles.colors.surface;
      const stroke = node.stroke || defaults.stroke || DiagramUtils.styles.colors.primary;
      const strokeWidth = node.strokeWidth || defaults.strokeWidth || 2;

      const g = DiagramUtils.createGroup('node');
      g.setAttribute('transform', `translate(${node.x}, ${node.y})`);

      // Node circle
      const circle = DiagramUtils.createCircle(0, 0, R, {
        'fill': fill,
        'stroke': stroke,
        'stroke-width': strokeWidth
      });
      g.appendChild(circle);

      // Node label
      const label = node.label || node.id;
      const textEl = DiagramUtils.createText(0, 4, label, {
        'text-anchor': 'middle',
        'dominant-baseline': 'middle',
        'font-size': '12',
        'font-family': 'Inter, sans-serif',
        'font-weight': '600',
        'fill': DiagramUtils.styles.colors.text
      });
      g.appendChild(textEl);

      // Node value/weight
      if (node.value !== undefined) {
        const valEl = DiagramUtils.createText(0, 22, String(node.value), {
          'text-anchor': 'middle',
          'dominant-baseline': 'middle',
          'font-size': '9',
          'font-family': 'JetBrains Mono, monospace',
          'fill': DiagramUtils.styles.colors.textLight
        });
        g.appendChild(valEl);
      }

      svg.appendChild(g);
    });
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = GraphGenerator;
}

window.DiagramGenerators = window.DiagramGenerators || {};
window.DiagramGenerators.graph = GraphGenerator.generate.bind(GraphGenerator);