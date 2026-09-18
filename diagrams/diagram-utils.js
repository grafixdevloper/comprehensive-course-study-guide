/**
 * Diagram Utilities
 * Shared utilities for all diagram generators
 */

const DiagramUtils = {
  /**
   * Create an SVG element with proper namespace
   */
  createSVG(width, height, viewBox = null) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    if (viewBox) {
      svg.setAttribute('viewBox', viewBox);
    } else {
      svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    }
    svg.style.maxWidth = '100%';
    svg.style.height = 'auto';
    return svg;
  },

  /**
   * Create a group element
   */
  createGroup(className = '') {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    if (className) g.setAttribute('class', className);
    return g;
  },

  /**
   * Create a circle (for states)
   */
  createCircle(cx, cy, r, attrs = {}) {
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', cx);
    circle.setAttribute('cy', cy);
    circle.setAttribute('r', r);
    Object.entries(attrs).forEach(([key, value]) => {
      circle.setAttribute(key, value);
    });
    return circle;
  },

  /**
   * Create a rectangle
   */
  createRect(x, y, width, height, attrs = {}) {
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', width);
    rect.setAttribute('height', height);
    Object.entries(attrs).forEach(([key, value]) => {
      rect.setAttribute(key, value);
    });
    return rect;
  },

  /**
   * Create a line
   */
  createLine(x1, y1, x2, y2, attrs = {}) {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    Object.entries(attrs).forEach(([key, value]) => {
      line.setAttribute(key, value);
    });
    return line;
  },

  /**
   * Create a path
   */
  createPath(d, attrs = {}) {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', d);
    Object.entries(attrs).forEach(([key, value]) => {
      path.setAttribute(key, value);
    });
    return path;
  },

  /**
   * Create text element
   */
  createText(x, y, content, attrs = {}) {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', x);
    text.setAttribute('y', y);
    text.textContent = content;
    Object.entries(attrs).forEach(([key, value]) => {
      text.setAttribute(key, value);
    });
    return text;
  },

  /**
   * Create an arrowhead marker
   */
  createArrowMarker(svg, id, color = '#333', size = 8) {
    const defs = svg.querySelector('defs') || document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    if (!svg.querySelector('defs')) svg.appendChild(defs);

    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', id);
    marker.setAttribute('markerWidth', size);
    marker.setAttribute('markerHeight', size);
    marker.setAttribute('refX', size - 1);
    marker.setAttribute('refY', size / 2);
    marker.setAttribute('orient', 'auto');
    marker.setAttribute('markerUnits', 'strokeWidth');

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M0,0 L${size},${size/2} L0,${size} Z`);
    path.setAttribute('fill', color);
    marker.appendChild(path);
    defs.appendChild(marker);

    return `url(#${id})`;
  },

  /**
   * Calculate arrow path between two circles (for automata transitions)
   */
  calculateArrowPath(x1, y1, x2, y2, r1, r2, offset = 0, curve = 0) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist === 0) return '';

    const ux = dx / dist;
    const uy = dy / dist;

    // Start and end points on circle perimeters
    const startX = x1 + ux * r1;
    const startY = y1 + uy * r1;
    const endX = x2 - ux * r2;
    const endY = y2 - uy * r2;

    if (curve === 0) {
      // Straight line
      return `M${startX},${startY} L${endX},${endY}`;
    } else {
      // Curved line
      const midX = (startX + endX) / 2 - uy * curve;
      const midY = (startY + endY) / 2 + ux * curve;
      return `M${startX},${startY} Q${midX},${midY} ${endX},${endY}`;
    }
  },

  /**
   * Calculate self-loop path
   */
  calculateSelfLoopPath(x, y, r, direction = 'top', size = 40) {
    const angles = {
      top: { start: -Math.PI / 4, end: -3 * Math.PI / 4, cx: 0, cy: -1 },
      right: { start: Math.PI / 4, end: 3 * Math.PI / 4, cx: 1, cy: 0 },
      bottom: { start: 3 * Math.PI / 4, end: 5 * Math.PI / 4, cx: 0, cy: 1 },
      left: { start: -3 * Math.PI / 4, end: -5 * Math.PI / 4, cx: -1, cy: 0 }
    };

    const dir = angles[direction] || angles.top;
    const centerX = x + dir.cx * (r + size);
    const centerY = y + dir.cy * (r + size);

    const startX = x + Math.cos(dir.start) * r;
    const startY = y + Math.sin(dir.start) * r;
    const endX = x + Math.cos(dir.end) * r;
    const endY = y + Math.sin(dir.end) * r;

    const largeArc = 1;
    const sweep = direction === 'top' || direction === 'left' ? 0 : 1;

    return `M${startX},${startY} A${size},${size} 0 ${largeArc},${sweep} ${endX},${endY}`;
  },

  /**
   * Layout nodes in a grid
   */
  layoutGrid(nodes, cols, spacing = 150, startX = 100, startY = 100) {
    return nodes.map((node, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      return {
        ...node,
        x: startX + col * spacing,
        y: startY + row * spacing
      };
    });
  },

  /**
   * Layout nodes in a circle
   */
  layoutCircle(nodes, centerX, centerY, radius, startAngle = -Math.PI / 2) {
    const angleStep = (2 * Math.PI) / nodes.length;
    return nodes.map((node, i) => {
      const angle = startAngle + i * angleStep;
      return {
        ...node,
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius,
        angle
      };
    });
  },

  /**
   * Layout nodes using force-directed algorithm (simple)
   */
  layoutForce(nodes, edges, width, height, iterations = 100) {
    // Initialize random positions
    nodes.forEach(node => {
      node.x = node.x || Math.random() * width;
      node.y = node.y || Math.random() * height;
      node.vx = 0;
      node.vy = 0;
    });

    const k = Math.sqrt((width * height) / nodes.length); // optimal distance

    for (let iter = 0; iter < iterations; iter++) {
      // Repulsion between all nodes
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const n1 = nodes[i];
          const n2 = nodes[j];
          const dx = n1.x - n2.x;
          const dy = n1.y - n2.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
          const force = (k * k) / dist;
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          n1.vx += fx;
          n1.vy += fy;
          n2.vx -= fx;
          n2.vy -= fy;
        }
      }

      // Attraction along edges
      edges.forEach(edge => {
        const source = nodes.find(n => n.id === edge.source);
        const target = nodes.find(n => n.id === edge.target);
        if (!source || !target) return;

        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
        const force = (dist * dist) / k;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        source.vx += fx;
        source.vy += fy;
        target.vx -= fx;
        target.vy -= fy;
      });

      // Apply velocities with damping
      nodes.forEach(node => {
        node.x += node.vx * 0.1;
        node.y += node.vy * 0.1;
        node.vx *= 0.9;
        node.vy *= 0.9;

        // Keep in bounds
        const margin = 50;
        node.x = Math.max(margin, Math.min(width - margin, node.x));
        node.y = Math.max(margin, Math.min(height - margin, node.y));
      });
    }

    return nodes;
  },

  /**
   * Default styles for diagrams
   */
  styles: {
    // Colors
    colors: {
      primary: '#1a3c5e',
      secondary: '#2c6f8a',
      accent: '#c0392b',
      background: '#ffffff',
      surface: '#f8f9fa',
      border: '#d0d0e0',
      text: '#1a1a2e',
      textLight: '#6b6b8a',
      start: '#27ae60',
      accept: '#c0392b',
      arrow: '#333',
      grid: '#e8e8f0'
    },

    // State styles
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
      radius: 28,
      fill: '#ffffff',
      stroke: '#27ae60',
      strokeWidth: 3,
      fontSize: 13,
      fontFamily: 'Inter, sans-serif',
      fontWeight: 600
    },

    acceptState: {
      radius: 28,
      fill: '#ffffff',
      stroke: '#c0392b',
      strokeWidth: 2,
      fontSize: 13,
      fontFamily: 'Inter, sans-serif',
      fontWeight: 600,
      doubleCircle: true
    },

    // Transition styles
    transition: {
      stroke: '#333',
      strokeWidth: 1.5,
      fontSize: 11,
      fontFamily: 'JetBrains Mono, monospace',
      labelOffset: 8,
      labelBackground: 'rgba(255,255,255,0.9)',
      labelPadding: 3
    },

    // Arrow styles
    arrow: {
      size: 8,
      color: '#333'
    }
  },

  /**
   * Apply theme to SVG
   */
  applyTheme(svg, theme = 'light') {
    if (theme === 'dark') {
      svg.style.filter = 'invert(1) hue-rotate(180deg)';
      // Fix images
      svg.querySelectorAll('image').forEach(img => {
        img.style.filter = 'invert(1) hue-rotate(180deg)';
      });
    }
  }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DiagramUtils;
}

// Global for browser
window.DiagramUtils = DiagramUtils;