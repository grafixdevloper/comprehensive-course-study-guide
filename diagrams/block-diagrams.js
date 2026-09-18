/**
 * Block Diagram Generator
 * Generates system architecture / block diagrams as SVG
 */

const BlockDiagramGenerator = {
  /**
   * Generate a block diagram from specification
   * @param {Object} spec - Diagram specification
   * @returns {SVGElement} SVG diagram
   */
  generate(spec) {
    const {
      blocks = [],
      connections = [],
      layout = 'horizontal', // horizontal, vertical, grid
      width = 900,
      height = 500,
      title = '',
      showLabels = true
    } = spec;

    if (!blocks.length) {
      return DiagramUtils.createPlaceholderDiagram({ type: 'block-diagram', description: 'No blocks defined' });
    }

    const svg = DiagramUtils.createSVG(width, height);
    svg.setAttribute('class', 'block-diagram');

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
    const arrowId = `arrow-bd-${Date.now()}`;
    DiagramUtils.createArrowMarker(svg, arrowId, DiagramUtils.styles.colors.arrow, 8);

    // Layout blocks
    const positionedBlocks = this.layoutBlocks(blocks, connections, layout, width, height);

    // Draw connections
    this.drawConnections(svg, positionedBlocks, connections, arrowId);

    // Draw blocks
    this.drawBlocks(svg, positionedBlocks);

    return svg;
  },

  /**
   * Layout blocks
   */
  layoutBlocks(blocks, connections, layout, width, height) {
    const blockMap = {};
    blocks.forEach(b => blockMap[b.id] = { ...b });

    if (layout === 'horizontal') {
      const spacing = (width - 100) / (blocks.length + 1);
      blocks.forEach((block, i) => {
        blockMap[block.id].x = 50 + (i + 1) * spacing;
        blockMap[block.id].y = height / 2;
      });
    } else if (layout === 'vertical') {
      const spacing = (height - 100) / (blocks.length + 1);
      blocks.forEach((block, i) => {
        blockMap[block.id].x = width / 2;
        blockMap[block.id].y = 50 + (i + 1) * spacing;
      });
    } else if (layout === 'grid') {
      const cols = Math.ceil(Math.sqrt(blocks.length));
      const rows = Math.ceil(blocks.length / cols);
      const colWidth = (width - 100) / (cols + 1);
      const rowHeight = (height - 100) / (rows + 1);

      blocks.forEach((block, i) => {
        const col = i % cols;
        const row = Math.floor(i / cols);
        blockMap[block.id].x = 50 + (col + 1) * colWidth;
        blockMap[block.id].y = 50 + (row + 1) * rowHeight;
      });
    }

    return Object.values(blockMap);
  },

  /**
   * Draw connections between blocks
   */
  drawConnections(svg, blocks, connections, arrowId) {
    const blockMap = {};
    blocks.forEach(b => blockMap[b.id] = b);

    connections.forEach(conn => {
      const from = blockMap[conn.from];
      const to = blockMap[conn.to];
      if (!from || !to) return;

      const fromPort = conn.fromPort || 'right';
      const toPort = conn.toPort || 'left';

      const { x: fromX, y: fromY } = this.getPortPosition(from, fromPort);
      const { x: toX, y: toY } = this.getPortPosition(to, toPort);

      // Create orthogonal path (Manhattan routing)
      const path = this.createOrthogonalPath(fromX, fromY, toX, toY, fromPort, toPort);

      const pathEl = DiagramUtils.createPath(path, {
        'stroke': DiagramUtils.styles.colors.arrow,
        'stroke-width': 1.5,
        'fill': 'none',
        'marker-end': arrowId,
        'stroke-dasharray': conn.style === 'dashed' ? '5,3' : 'none'
      });
      svg.appendChild(pathEl);

      // Connection label
      if (conn.label) {
        this.addConnectionLabel(svg, fromX, fromY, toX, toY, conn.label);
      }
    });
  },

  /**
   * Get port position on block
   */
  getPortPosition(block, port) {
    const w = block.width || 140;
    const h = block.height || 70;
    const x = block.x;
    const y = block.y;

    switch (port) {
      case 'top': return { x, y: y - h/2 };
      case 'bottom': return { x, y: y + h/2 };
      case 'left': return { x: x - w/2, y };
      case 'right': return { x: x + w/2, y };
      default: return { x, y };
    }
  },

  /**
   * Create orthogonal (Manhattan) path
   */
  createOrthogonalPath(x1, y1, x2, y2, port1, port2) {
    // Simple L-shaped path
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;

    // Determine bend direction based on ports
    if (port1 === 'right' && port2 === 'left') {
      return `M${x1},${y1} H${midX} V${y2} H${x2}`;
    } else if (port1 === 'left' && port2 === 'right') {
      return `M${x1},${y1} H${midX} V${y2} H${x2}`;
    } else if (port1 === 'bottom' && port2 === 'top') {
      return `M${x1},${y1} V${midY} H${x2} V${y2}`;
    } else if (port1 === 'top' && port2 === 'bottom') {
      return `M${x1},${y1} V${midY} H${x2} V${y2}`;
    }

    // Default: L-shape
    if (Math.abs(x2 - x1) > Math.abs(y2 - y1)) {
      return `M${x1},${y1} H${midX} V${y2} H${x2}`;
    } else {
      return `M${x1},${y1} V${midY} H${x2} V${y2}`;
    }
  },

  /**
   * Add connection label
   */
  addConnectionLabel(svg, x1, y1, x2, y2, label) {
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2 - 10;

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
   * Draw blocks
   */
  drawBlocks(svg, blocks) {
    blocks.forEach(block => {
      const w = block.width || 140;
      const h = block.height || 70;
      const x = block.x - w/2;
      const y = block.y - h/2;
      const fill = block.fill || DiagramUtils.styles.colors.surface;
      const stroke = block.stroke || DiagramUtils.styles.colors.primary;
      const strokeWidth = block.strokeWidth || 2;
      const radius = block.radius || 8;

      const g = DiagramUtils.createGroup('block');
      g.setAttribute('transform', `translate(${x}, ${y})`);

      // Block background
      const rect = DiagramUtils.createRect(0, 0, w, h, {
        'rx': radius,
        'ry': radius,
        'fill': fill,
        'stroke': stroke,
        'stroke-width': strokeWidth
      });
      g.appendChild(rect);

      // Block type indicator (top bar)
      if (block.type) {
        const typeColors = {
          input: '#3498db',
          process: '#27ae60',
          output: '#e67e22',
          storage: '#8e44ad',
          decision: '#c0392b',
          default: DiagramUtils.styles.colors.primary
        };
        const typeColor = typeColors[block.type] || typeColors.default;

        const typeBar = DiagramUtils.createRect(0, 0, w, 6, {
          'rx': radius,
          'ry': 0,
          'fill': typeColor
        });
        g.appendChild(typeBar);
      }

      // Block label
      const label = block.label || block.id;
      const lines = this.wrapText(label, w - 20);
      lines.forEach((line, i) => {
        const textEl = DiagramUtils.createText(w/2, h/2 - (lines.length - 1) * 7 + i * 14, line, {
          'text-anchor': 'middle',
          'dominant-baseline': 'middle',
          'font-size': '12',
          'font-family': 'Inter, sans-serif',
          'font-weight': '600',
          'fill': DiagramUtils.styles.colors.text
        });
        g.appendChild(textEl);
      });

      // Sub-label / description
      if (block.description) {
        const descLines = this.wrapText(block.description, w - 10);
        descLines.forEach((line, i) => {
          const textEl = DiagramUtils.createText(w/2, h - 15 - (descLines.length - 1 - i) * 11, line, {
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
            'font-size': '9',
            'font-family': 'Inter, sans-serif',
            'fill': DiagramUtils.styles.colors.textLight,
            'font-style': 'italic'
          });
          g.appendChild(textEl);
        });
      }

      // Port indicators
      this.drawPorts(g, w, h, block.ports);

      svg.appendChild(g);
    });
  },

  /**
   * Draw port indicators
   */
  drawPorts(g, w, h, ports) {
    if (!ports) return;

    const portPositions = {
      top: { x: w/2, y: 0 },
      bottom: { x: w/2, y: h },
      left: { x: 0, y: h/2 },
      right: { x: w, y: h/2 }
    };

    ports.forEach(port => {
      const pos = portPositions[port.side] || portPositions.right;
      const circle = DiagramUtils.createCircle(pos.x, pos.y, 4, {
        'fill': DiagramUtils.styles.colors.primary,
        'stroke': 'white',
        'stroke-width': 1
      });
      g.appendChild(circle);

      if (port.label) {
        const offset = port.side === 'left' ? -8 : port.side === 'right' ? 8 : 0;
        const textEl = DiagramUtils.createText(pos.x + offset, pos.y + (port.side === 'top' ? -8 : port.side === 'bottom' ? 14 : 4), port.label, {
          'text-anchor': port.side === 'left' ? 'end' : port.side === 'right' ? 'start' : 'middle',
          'dominant-baseline': 'middle',
          'font-size': '8',
          'font-family': 'Inter, sans-serif',
          'fill': DiagramUtils.styles.colors.textLight
        });
        g.appendChild(textEl);
      }
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
      if ((current + ' ' + word).length > maxWidth / 6) {
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
  module.exports = BlockDiagramGenerator;
}

window.DiagramGenerators = window.DiagramGenerators || {};
window.DiagramGenerators.blockDiagram = BlockDiagramGenerator.generate.bind(BlockDiagramGenerator);