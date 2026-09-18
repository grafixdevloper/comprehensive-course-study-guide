/**
 * Tree Diagram Generator
 * Generates tree diagrams (binary trees, parse trees, decision trees) as SVG
 */

const TreeGenerator = {
  /**
   * Generate a tree diagram from specification
   * @param {Object} spec - Diagram specification
   * @returns {SVGElement} SVG diagram
   */
  generate(spec) {
    const {
      root = null,
      nodes = [],
      edges = [],
      type = 'binary', // binary, general, parse, decision
      layout = 'top-down', // top-down, left-right, radial
      width = 800,
      height = 600,
      title = '',
      nodeDefaults = {}
    } = spec;

    // Support both node/edge format and nested root format
    let treeNodes, treeEdges;
    if (root) {
      // Convert nested structure to nodes/edges
      const result = this.flattenTree(root);
      treeNodes = result.nodes;
      treeEdges = result.edges;
    } else {
      treeNodes = nodes;
      treeEdges = edges;
    }

    if (!treeNodes.length) {
      return DiagramUtils.createPlaceholderDiagram({ type: 'tree', description: 'No nodes defined' });
    }

    const svg = DiagramUtils.createSVG(width, height);
    svg.setAttribute('class', 'tree-diagram');

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

    // Layout nodes
    const positionedNodes = this.layoutTree(treeNodes, treeEdges, layout, width, height, type);

    // Draw edges
    this.drawEdges(svg, positionedNodes, treeEdges);

    // Draw nodes
    this.drawNodes(svg, positionedNodes, nodeDefaults, type);

    return svg;
  },

  /**
   * Flatten nested tree structure
   */
  flattenTree(node, parentId = null, nodes = [], edges = [], depth = 0) {
    const id = node.id || `node-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    nodes.push({ ...node, id, depth });

    if (parentId) {
      edges.push({ from: parentId, to: id, label: node.edgeLabel });
    }

    if (node.children) {
      node.children.forEach(child => {
        this.flattenTree(child, id, nodes, edges, depth + 1);
      });
    } else if (node.left || node.right) {
      // Binary tree format
      if (node.left) this.flattenTree(node.left, id, nodes, edges, depth + 1);
      if (node.right) this.flattenTree(node.right, id, nodes, edges, depth + 1);
    }

    return { nodes, edges };
  },

  /**
   * Layout tree nodes
   */
  layoutTree(nodes, edges, layout, width, height, type) {
    const nodeMap = {};
    nodes.forEach(n => nodeMap[n.id] = { ...n });

    // Build children map
    const children = {};
    const parents = {};
    nodes.forEach(n => {
      children[n.id] = [];
      parents[n.id] = null;
    });
    edges.forEach(e => {
      if (!children[e.from]) children[e.from] = [];
      children[e.from].push(e.to);
      parents[e.to] = e.from;
    });

    // Find root (no parent)
    const rootNode = nodes.find(n => parents[n.id] === null) || nodes[0];

    if (layout === 'top-down') {
      return this.layoutTopDown(nodeMap, children, rootNode.id, width, height);
    } else if (layout === 'left-right') {
      return this.layoutLeftRight(nodeMap, children, rootNode.id, width, height);
    } else if (layout === 'radial') {
      return this.layoutRadial(nodeMap, children, rootNode.id, width, height);
    }

    return Object.values(nodeMap);
  },

  /**
   * Top-down layout (standard tree)
   */
  layoutTopDown(nodeMap, children, rootId, width, height) {
    // Calculate subtree widths
    const subtreeWidth = {};
    const maxDepth = this.getMaxDepth(children, rootNodeId => rootNodeId, rootId);

    function computeWidth(id) {
      const kids = children[id] || [];
      if (kids.length === 0) {
        subtreeWidth[id] = 1;
        return 1;
      }
      let w = 0;
      kids.forEach(kid => w += computeWidth(kid));
      subtreeWidth[id] = Math.max(w, 1);
      return subtreeWidth[id];
    }

    computeWidth(rootId);

    // Position nodes
    const positioned = [];
    const levelHeight = (height - 100) / (maxDepth + 1);

    function positionNode(id, xStart, depth) {
      const node = nodeMap[id];
      const kids = children[id] || [];

      if (kids.length === 0) {
        // Leaf
        node.x = xStart + 0.5 * (width / (subtreeWidth[rootId] + 1));
        node.y = 50 + depth * levelHeight;
        node.subtreeLeft = node.x;
        node.subtreeRight = node.x;
        positioned.push(node);
        return node.x;
      }

      // Position children first
      let currentX = xStart;
      const childCenters = [];

      kids.forEach(kid => {
        const childWidth = subtreeWidth[kid];
        const childCenter = positionNode(kid, currentX, depth + 1);
        childCenters.push(childCenter);
        currentX += childWidth * (width / (subtreeWidth[rootId] + 1));
      });

      // Parent centered over children
      node.x = (childCenters[0] + childCenters[childCenters.length - 1]) / 2;
      node.y = 50 + depth * levelHeight;
      positioned.push(node);

      return node.x;
    }

    positionNode(rootId, 0, 0);
    return positioned;
  },

  /**
   * Left-right layout
   */
  layoutLeftRight(nodeMap, children, rootId, width, height) {
    // Similar to top-down but rotated
    const positioned = [];
    const maxDepth = this.getMaxDepth(children, rootNodeId => rootNodeId, rootId);
    const levelWidth = (width - 100) / (maxDepth + 1);

    function positionNode(id, depth, yStart, yEnd) {
      const node = nodeMap[id];
      const kids = children[id] || [];

      node.x = 50 + depth * levelWidth;
      node.y = (yStart + yEnd) / 2;
      positioned.push(node);

      if (kids.length > 0) {
        const segmentHeight = (yEnd - yStart) / kids.length;
        kids.forEach((kid, i) => {
          positionNode(kid, depth + 1, yStart + i * segmentHeight, yStart + (i + 1) * segmentHeight);
        });
      }
    }

    positionNode(rootId, 0, 0, height);
    return positioned;
  },

  /**
   * Radial layout
   */
  layoutRadial(nodeMap, children, rootId, width, height) {
    const positioned = [];
    const centerX = width / 2;
    const centerY = height / 2;
    const maxRadius = Math.min(width, height) / 2 - 50;

    // Get depths
    const depths = {};
    function assignDepths(id, depth) {
      depths[id] = depth;
      (children[id] || []).forEach(kid => assignDepths(kid, depth + 1));
    }
    assignDepths(rootId, 0);

    const maxDepth = Math.max(...Object.values(depths));
    const radiusStep = maxDepth > 0 ? maxRadius / maxDepth : maxRadius;

    function positionNode(id, angle, depth) {
      const node = nodeMap[id];
      const r = depth * radiusStep;
      node.x = centerX + Math.cos(angle) * r;
      node.y = centerY + Math.sin(angle) * r;
      positioned.push(node);

      const kids = children[id] || [];
      if (kids.length > 0) {
        const angleStep = (2 * Math.PI) / kids.length;
        kids.forEach((kid, i) => {
          positionNode(kid, angle - Math.PI + i * angleStep, depth + 1);
        });
      }
    }

    positionNode(rootId, -Math.PI / 2, 0);
    return positioned;
  },

  /**
   * Get max depth of tree
   */
  getMaxDepth(children, getId, rootId) {
    let max = 0;
    function traverse(id, depth) {
      max = Math.max(max, depth);
      (children[id] || []).forEach(kid => traverse(kid, depth + 1));
    }
    traverse(rootId, 0);
    return max;
  },

  /**
   * Draw edges
   */
  drawEdges(svg, nodes, edges) {
    const nodeMap = {};
    nodes.forEach(n => nodeMap[n.id] = n);

    edges.forEach(edge => {
      const from = nodeMap[edge.from];
      const to = nodeMap[edge.to];
      if (!from || !to) return;

      // Simple straight line or slight curve
      const dx = to.x - from.x;
      const dy = to.y - from.y;

      let path;
      if (Math.abs(dx) < 5) {
        // Vertical-ish
        path = `M${from.x},${from.y} L${to.x},${to.y}`;
      } else {
        // Slight curve for visual appeal
        const midX = (from.x + to.x) / 2;
        const midY = (from.y + to.y) / 2;
        path = `M${from.x},${from.y} Q${midX},${midY} ${to.x},${to.y}`;
      }

      const pathEl = DiagramUtils.createPath(path, {
        'stroke': DiagramUtils.styles.colors.arrow,
        'stroke-width': 1.5,
        'fill': 'none'
      });
      svg.appendChild(pathEl);

      // Edge label
      if (edge.label) {
        const labelX = (from.x + to.x) / 2;
        const labelY = (from.y + to.y) / 2 - 8;

        const textEl = DiagramUtils.createText(labelX, labelY, edge.label, {
          'text-anchor': 'middle',
          'dominant-baseline': 'middle',
          'font-size': '9',
          'font-family': 'JetBrains Mono, monospace',
          'fill': DiagramUtils.styles.colors.text,
          'font-weight': '500',
          'paint-order': 'stroke',
          'stroke': 'white',
          'stroke-width': '2'
        });
        svg.appendChild(textEl);
      }
    });
  },

  /**
   * Draw nodes
   */
  drawNodes(svg, nodes, defaults, type) {
    nodes.forEach(node => {
      const shape = node.shape || defaults.shape || (type === 'decision' ? 'diamond' : 'circle');
      const width = node.width || defaults.width || 50;
      const height = node.height || defaults.height || 50;
      const fill = node.fill || defaults.fill || DiagramUtils.styles.colors.surface;
      const stroke = node.stroke || defaults.stroke || DiagramUtils.styles.colors.primary;
      const strokeWidth = node.strokeWidth || defaults.strokeWidth || 2;

      const g = DiagramUtils.createGroup('node');
      g.setAttribute('transform', `translate(${node.x}, ${node.y})`);

      // Draw shape
      let shapeEl;
      const halfW = width / 2;
      const halfH = height / 2;

      switch (shape) {
        case 'diamond':
          shapeEl = DiagramUtils.createPath(
            `M0,${-halfH} L${halfW},0 L0,${halfH} L${-halfW},0 Z`
          );
          break;
        case 'rectangle':
        case 'box':
          shapeEl = DiagramUtils.createRect(-halfW, -halfH, width, height, {
            'rx': 6,
            'ry': 6
          });
          break;
        case 'ellipse':
        case 'oval':
          shapeEl = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
          shapeEl.setAttribute('cx', 0);
          shapeEl.setAttribute('cy', 0);
          shapeEl.setAttribute('rx', halfW);
          shapeEl.setAttribute('ry', halfH);
          break;
        case 'circle':
        default:
          shapeEl = DiagramUtils.createCircle(0, 0, Math.min(halfW, halfH), {});
          break
      }

      shapeEl.setAttribute('fill', fill);
      shapeEl.setAttribute('stroke', stroke);
      shapeEl.setAttribute('stroke-width', strokeWidth);
      g.appendChild(shapeEl);

      // Node label
      const label = node.label || node.id || '';
      const lines = this.wrapText(label, width - 10);
      lines.forEach((line, i) => {
        const textEl = DiagramUtils.createText(0, -(lines.length - 1) * 6 + i * 12, line, {
          'text-anchor': 'middle',
          'dominant-baseline': 'middle',
          'font-size': '10',
          'font-family': 'Inter, sans-serif',
          'font-weight': '600',
          'fill': DiagramUtils.styles.colors.text
        });
        g.appendChild(textEl);
      });

      // Node value (for parse trees, etc.)
      if (node.value !== undefined) {
        const valEl = DiagramUtils.createText(0, (lines.length - 1) * 6 + 14, String(node.value), {
          'text-anchor': 'middle',
          'dominant-baseline': 'middle',
          'font-size': '9',
          'font-family': 'JetBrains Mono, monospace',
          'fill': DiagramUtils.styles.colors.accent
        });
        g.appendChild(valEl);
      }

      // Node type indicator (for parse trees: terminal vs non-terminal)
      if (node.nodeType) {
        const typeColors = {
          terminal: '#27ae60',
          nonterminal: '#3498db',
          epsilon: '#e67e22'
        };
        const indicator = DiagramUtils.createCircle(0, -halfH - 8, 5, {
          'fill': typeColors[node.nodeType] || '#999'
        });
        g.appendChild(indicator);
      }

      svg.appendChild(g);
    });
  },

  /**
   * Wrap text
   */
  wrapText(text, maxWidth) {
    const words = text.split(' ');
    const lines = [];
    let current = '';

    words.forEach(word => {
      if ((current + ' ' + word).length > maxWidth / 5) {
        lines.push(current);
        current = word;
      } else {
        current += (current ? ' ' : '') + word;
      }
    });
    if (current) lines.push(current);
    return lines.length > 0 ? lines : [text];
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = TreeGenerator;
}

window.DiagramGenerators = window.DiagramGenerators || {};
window.DiagramGenerators.tree = TreeGenerator.generate.bind(TreeGenerator);