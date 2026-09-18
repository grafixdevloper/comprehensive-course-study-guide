/**
 * Process Diagram / Timeline Generator
 * Generates timeline, process flow, and sequence diagrams as SVG
 */

const ProcessDiagramGenerator = {
  /**
   * Generate a process/timeline diagram from specification
   * @param {Object} spec - Diagram specification
   * @returns {SVGElement} SVG diagram
   */
  generate(spec) {
    const {
      events = [],
      steps = [],
      type = 'timeline', // timeline, process, sequence
      orientation = 'vertical', // vertical, horizontal
      width = 800,
      height = 600,
      title = '',
      showTime = true
    } = spec;

    const items = events.length ? events : steps;

    if (!items.length) {
      return DiagramUtils.createPlaceholderDiagram({ type: 'process', description: 'No events/steps defined' });
    }

    const svg = DiagramUtils.createSVG(width, height);
    svg.setAttribute('class', 'process-diagram');

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

    if (type === 'timeline') {
      this.drawTimeline(svg, items, orientation, width, height, showTime);
    } else if (type === 'process') {
      this.drawProcess(svg, items, orientation, width, height);
    } else if (type === 'sequence') {
      this.drawSequence(svg, items, width, height);
    }

    return svg;
  },

  /**
   * Draw vertical/horizontal timeline
   */
  drawTimeline(svg, events, orientation, width, height, showTime) {
    const sorted = [...events].sort((a, b) => (a.time || 0) - (b.time || 0));
    const count = sorted.length;

    if (orientation === 'vertical') {
      // Vertical timeline with central line
      const lineX = width / 2;
      const startY = 60;
      const endY = height - 40;
      const spacing = count > 1 ? (endY - startY) / (count - 1) : 0;

      // Central line
      const line = DiagramUtils.createLine(lineX, startY, lineX, endY, {
        'stroke': DiagramUtils.styles.colors.primary,
        'stroke-width': 3
      });
      svg.appendChild(line);

      sorted.forEach((event, i) => {
        const y = startY + i * spacing;
        const isLeft = i % 2 === 0;
        const boxX = isLeft ? lineX - 200 : lineX + 50;
        const boxWidth = 180;
        const boxHeight = 80;

        // Connector line
        const connector = DiagramUtils.createLine(lineX, y, isLeft ? lineX - 10 : lineX + 10, y, {
          'stroke': DiagramUtils.styles.colors.primary,
          'stroke-width': 2
        });
        svg.appendChild(connector);

        // Circle on main line
        const circle = DiagramUtils.createCircle(lineX, y, 8, {
          'fill': DiagramUtils.styles.colors.primary,
          'stroke': 'white',
          'stroke-width': 2
        });
        svg.appendChild(circle);

        // Event box
        const g = DiagramUtils.createGroup('event');
        g.setAttribute('transform', `translate(${boxX}, ${y - boxHeight/2})`);

        // Box background
        const rect = DiagramUtils.createRect(0, 0, boxWidth, boxHeight, {
          'rx': 8,
          'ry': 8,
          'fill': DiagramUtils.styles.colors.surface,
          'stroke': DiagramUtils.styles.colors.border,
          'stroke-width': 1
        });
        g.appendChild(rect);

        // Time label
        if (showTime && event.time !== undefined) {
          const timeEl = DiagramUtils.createText(10, 20, String(event.time), {
            'font-size': '10',
            'font-family': 'JetBrains Mono, monospace',
            'fill': DiagramUtils.styles.colors.primary,
            'font-weight': 'bold'
          });
          g.appendChild(timeEl);
        }

        // Event title
        const titleEl = DiagramUtils.createText(10, showTime && event.time !== undefined ? 40 : 25, event.title || event.label || 'Event', {
          'font-size': '12',
          'font-family': 'Inter, sans-serif',
          'font-weight': '600',
          'fill': DiagramUtils.styles.colors.text
        });
        g.appendChild(titleEl);

        // Event description
        if (event.description) {
          const lines = this.wrapText(event.description, boxWidth - 20);
          lines.forEach((line, j) => {
            const descEl = DiagramUtils.createText(10, (showTime && event.time !== undefined ? 55 : 40) + j * 14, line, {
              'font-size': '9',
              'font-family': 'Inter, sans-serif',
              'fill': DiagramUtils.styles.colors.textLight
            });
            g.appendChild(descEl);
          });
        }

        svg.appendChild(g);
      });
    } else {
      // Horizontal timeline
      const lineY = height / 2;
      const startX = 60;
      const endX = width - 60;
      const spacing = count > 1 ? (endX - startX) / (count - 1) : 0;

      // Central line
      const line = DiagramUtils.createLine(startX, lineY, endX, lineY, {
        'stroke': DiagramUtils.styles.colors.primary,
        'stroke-width': 3
      });
      svg.appendChild(line);

      sorted.forEach((event, i) => {
        const x = startX + i * spacing;
        const isTop = i % 2 === 0;
        const boxY = isTop ? lineY - 150 : lineY + 50;
        const boxWidth = 160;
        const boxHeight = 90;

        // Connector
        const connector = DiagramUtils.createLine(x, lineY, x, isTop ? lineY - 10 : lineY + 10, {
          'stroke': DiagramUtils.styles.colors.primary,
          'stroke-width': 2
        });
        svg.appendChild(connector);

        // Circle
        const circle = DiagramUtils.createCircle(x, lineY, 8, {
          'fill': DiagramUtils.styles.colors.primary,
          'stroke': 'white',
          'stroke-width': 2
        });
        svg.appendChild(circle);

        // Event box
        const g = DiagramUtils.createGroup('event');
        g.setAttribute('transform', `translate(${x - boxWidth/2}, ${boxY})`);

        const rect = DiagramUtils.createRect(0, 0, boxWidth, boxHeight, {
          'rx': 8, 'ry': 8,
          'fill': DiagramUtils.styles.colors.surface,
          'stroke': DiagramUtils.styles.colors.border,
          'stroke-width': 1
        });
        g.appendChild(rect);

        if (showTime && event.time !== undefined) {
          const timeEl = DiagramUtils.createText(boxWidth/2, 20, String(event.time), {
            'text-anchor': 'middle',
            'font-size': '10',
            'font-family': 'JetBrains Mono, monospace',
            'fill': DiagramUtils.styles.colors.primary,
            'font-weight': 'bold'
          });
          g.appendChild(timeEl);
        }

        const titleEl = DiagramUtils.createText(boxWidth/2, showTime && event.time !== undefined ? 40 : 25, event.title || event.label || 'Event', {
          'text-anchor': 'middle',
          'font-size': '11',
          'font-family': 'Inter, sans-serif',
          'font-weight': '600',
          'fill': DiagramUtils.styles.colors.text
        });
        g.appendChild(titleEl);

        if (event.description) {
          const lines = this.wrapText(event.description, boxWidth - 20);
          lines.forEach((line, j) => {
            const descEl = DiagramUtils.createText(boxWidth/2, (showTime && event.time !== undefined ? 55 : 40) + j * 14, line, {
              'text-anchor': 'middle',
              'font-size': '9',
              'font-family': 'Inter, sans-serif',
              'fill': DiagramUtils.styles.colors.textLight
            });
            g.appendChild(descEl);
          });
        }

        svg.appendChild(g);
      });
    }
  },

  /**
   * Draw process flow diagram
   */
  drawProcess(svg, steps, orientation, width, height) {
    const count = steps.length;

    if (orientation === 'vertical') {
      const stepHeight = (height - 100) / count;
      const startX = width / 2;

      steps.forEach((step, i) => {
        const y = 50 + i * stepHeight + stepHeight / 2;
        const boxWidth = Math.min(400, width - 100);
        const boxHeight = Math.min(stepHeight - 20, 100);

        const g = DiagramUtils.createGroup('step');
        g.setAttribute('transform', `translate(${startX - boxWidth/2}, ${y - boxHeight/2})`);

        // Step number badge
        const badge = DiagramUtils.createCircle(20, boxHeight/2, 18, {
          'fill': DiagramUtils.styles.colors.primary,
          'stroke': 'white',
          'stroke-width': 2
        });
        g.appendChild(badge);

        const badgeText = DiagramUtils.createText(20, boxHeight/2 + 4, String(i + 1), {
          'text-anchor': 'middle',
          'dominant-baseline': 'middle',
          'font-size': '12',
          'font-family': 'Inter, sans-serif',
          'font-weight': 'bold',
          'fill': 'white'
        });
        g.appendChild(badgeText);

        // Step box
        const rect = DiagramUtils.createRect(50, 0, boxWidth - 60, boxHeight, {
          'rx': 8, 'ry': 8,
          'fill': DiagramUtils.styles.colors.surface,
          'stroke': DiagramUtils.styles.colors.primary,
          'stroke-width': 2
        });
        g.appendChild(rect);

        // Step title
        const titleEl = DiagramUtils.createText(65, 25, step.title || step.label || `Step ${i + 1}`, {
          'font-size': '13',
          'font-family': 'Inter, sans-serif',
          'font-weight': '600',
          'fill': DiagramUtils.styles.colors.text
        });
        g.appendChild(titleEl);

        // Step description
        if (step.description) {
          const lines = this.wrapText(step.description, boxWidth - 80);
          lines.forEach((line, j) => {
            const descEl = DiagramUtils.createText(65, 45 + j * 16, line, {
              'font-size': '10',
              'font-family': 'Inter, sans-serif',
              'fill': DiagramUtils.styles.colors.textLight
            });
            g.appendChild(descEl);
          });
        }

        // Arrow to next step
        if (i < count - 1) {
          const arrowY = boxHeight/2;
          const arrow = DiagramUtils.createPath(
            `M${20},${arrowY} V${boxHeight + 10}`,
            { 'stroke': DiagramUtils.styles.colors.primary, 'stroke-width': 2, 'fill': 'none', 'marker-end': 'url(#arrow-process)' }
          );
          g.appendChild(arrow);
        }

        svg.appendChild(g);
      });

      // Add arrow marker
      DiagramUtils.createArrowMarker(svg, 'arrow-process', DiagramUtils.styles.colors.primary, 8);
    } else {
      // Horizontal process flow
      const stepWidth = (width - 100) / count;
      const startY = height / 2;

      steps.forEach((step, i) => {
        const x = 50 + i * stepWidth + stepWidth / 2;
        const boxHeight = Math.min(150, height - 100);
        const boxWidth = Math.min(stepWidth - 20, 180);

        const g = DiagramUtils.createGroup('step');
        g.setAttribute('transform', `translate(${x - boxWidth/2}, ${startY - boxHeight/2})`);

        // Step number
        const badge = DiagramUtils.createCircle(boxWidth/2, 20, 16, {
          'fill': DiagramUtils.styles.colors.primary
        });
        g.appendChild(badge);

        const badgeText = DiagramUtils.createText(boxWidth/2, 24, String(i + 1), {
          'text-anchor': 'middle', 'dominant-baseline': 'middle',
          'font-size': '11', 'font-family': 'Inter, sans-serif', 'font-weight': 'bold', 'fill': 'white'
        });
        g.appendChild(badgeText);

        // Box
        const rect = DiagramUtils.createRect(0, 40, boxWidth, boxHeight - 50, {
          'rx': 8, 'ry': 8,
          'fill': DiagramUtils.styles.colors.surface,
          'stroke': DiagramUtils.styles.colors.primary,
          'stroke-width': 2
        });
        g.appendChild(rect);

        const titleEl = DiagramUtils.createText(boxWidth/2, 60, step.title || step.label || `Step ${i + 1}`, {
          'text-anchor': 'middle',
          'font-size': '12', 'font-family': 'Inter, sans-serif', 'font-weight': '600', 'fill': DiagramUtils.styles.colors.text
        });
        g.appendChild(titleEl);

        if (step.description) {
          const lines = this.wrapText(step.description, boxWidth - 20);
          lines.forEach((line, j) => {
            const descEl = DiagramUtils.createText(boxWidth/2, 80 + j * 14, line, {
              'text-anchor': 'middle', 'font-size': '9', 'font-family': 'Inter, sans-serif', 'fill': DiagramUtils.styles.colors.textLight
            });
            g.appendChild(descEl);
          });
        }

        // Arrow to next
        if (i < count - 1) {
          const arrow = DiagramUtils.createPath(
            `M${boxWidth},${boxHeight/2} H${stepWidth - boxWidth/2}`,
            { 'stroke': DiagramUtils.styles.colors.primary, 'stroke-width': 2, 'fill': 'none', 'marker-end': 'url(#arrow-process-h)' }
          );
          g.appendChild(arrow);
        }

        svg.appendChild(g);
      });

      DiagramUtils.createArrowMarker(svg, 'arrow-process-h', DiagramUtils.styles.colors.primary, 8);
    }
  },

  /**
   * Draw sequence diagram
   */
  drawSequence(svg, participants, width, height) {
    // Participants are the actors/lifelines
    const actors = participants.filter(p => p.type === 'actor' || p.actor);
    const messages = participants.filter(p => p.type === 'message' || p.from);

    if (actors.length === 0) {
      // Create actors from messages
      const actorSet = new Set();
      messages.forEach(m => { actorSet.add(m.from); actorSet.add(m.to); });
      actors.push(...Array.from(actorSet).map(name => ({ id: name, label: name })));
    }

    const actorCount = actors.length;
    const laneWidth = (width - 100) / actorCount;
    const startY = 60;
    const endY = height - 40;

    // Draw lifelines
    actors.forEach((actor, i) => {
      const x = 50 + (i + 0.5) * laneWidth;

      // Lifeline
      const line = DiagramUtils.createLine(x, startY + 40, x, endY, {
        'stroke': DiagramUtils.styles.colors.border,
        'stroke-width': 2,
        'stroke-dasharray': '8,4'
      });
      svg.appendChild(line);

      // Actor box at top
      const boxWidth = Math.min(laneWidth - 20, 120);
      const g = DiagramUtils.createGroup('actor');
      g.setAttribute('transform', `translate(${x - boxWidth/2}, ${startY})`);

      const rect = DiagramUtils.createRect(0, 0, boxWidth, 35, {
        'rx': 6, 'ry': 6,
        'fill': DiagramUtils.styles.colors.surface,
        'stroke': DiagramUtils.styles.colors.primary,
        'stroke-width': 2
      });
      g.appendChild(rect);

      const label = DiagramUtils.createText(boxWidth/2, 22, actor.label || actor.id, {
        'text-anchor': 'middle', 'dominant-baseline': 'middle',
        'font-size': '11', 'font-family': 'Inter, sans-serif', 'font-weight': '600', 'fill': DiagramUtils.styles.colors.text
      });
      g.appendChild(label);

      svg.appendChild(g);

      // Store position for messages
      actor._x = x;
    });

    // Draw messages
    messages.forEach((msg, i) => {
      const fromActor = actors.find(a => a.id === msg.from);
      const toActor = actors.find(a => a.id === msg.to);
      if (!fromActor || !toActor) return;

      const y = startY + 60 + i * 50;
      const fromX = fromActor._x;
      const toX = toActor._x;

      // Message arrow
      const isReturn = msg.type === 'return' || msg.return;
      const color = isReturn ? DiagramUtils.styles.colors.accent : DiagramUtils.styles.colors.primary;

      const path = DiagramUtils.createLine(fromX, y, toX, y, {
        'stroke': color,
        'stroke-width': isReturn ? 1 : 2,
        'stroke-dasharray': isReturn ? '4,2' : 'none',
        'marker-end': `url(#arrow-seq-${isReturn ? 'ret' : 'norm'})`
      });
      svg.appendChild(path);

      // Message label
      if (msg.label) {
        const labelX = (fromX + toX) / 2;
        const labelEl = DiagramUtils.createText(labelX, y - 8, msg.label, {
          'text-anchor': 'middle', 'dominant-baseline': 'middle',
          'font-size': '10', 'font-family': 'Inter, sans-serif', 'fill': color
        });
        svg.appendChild(labelEl);
      }

      // Activation boxes (optional)
      if (msg.activate) {
        // Add activation rectangle on lifeline
      }
    });

    // Arrow markers
    DiagramUtils.createArrowMarker(svg, 'arrow-seq-norm', DiagramUtils.styles.colors.primary, 7);
    DiagramUtils.createArrowMarker(svg, 'arrow-seq-ret', DiagramUtils.styles.colors.accent, 5);
  },

  /**
   * Wrap text
   */
  wrapText(text, maxWidth) {
    const words = text.split(' ');
    const lines = [];
    let current = '';

    words.forEach(word => {
      if ((current + ' ' + word).length > maxWidth / 5.5) {
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
  module.exports = ProcessDiagramGenerator;
}

window.DiagramGenerators = window.DiagramGenerators || {};
window.DiagramGenerators.timeline = ProcessDiagramGenerator.generate.bind(ProcessDiagramGenerator);
window.DiagramGenerators.process = ProcessDiagramGenerator.generate.bind(ProcessDiagramGenerator);
window.DiagramGenerators.sequence = ProcessDiagramGenerator.generate.bind(ProcessDiagramGenerator);