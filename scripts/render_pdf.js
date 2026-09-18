/**
 * PDF Renderer using Playwright + Chromium
 * Renders the HTML study guide to PDF
 */

const fs = require('fs');
const path = require('path');

async function renderPDF(options = {}) {
  const {
    htmlPath = 'study-guide-output/study-guide.html',
    pdfPath = 'study-guide-output/study-guide.pdf',
    workDir = '.study-guide-work',
    format = 'A4',
    margin = { top: '20mm', right: '18mm', bottom: '20mm', left: '18mm' },
    printBackground = true,
    preferCSSPageSize = true,
    waitForSelector = '#app',
    waitForEvent = 'study-guide-ready',
    timeout = 120000,
    headless = true
  } = options;

  const { chromium } = require('playwright');

  console.log('Starting PDF generation...');
  console.log(`HTML: ${htmlPath}`);
  console.log(`PDF: ${pdfPath}`);

  // Verify HTML exists
  if (!fs.existsSync(htmlPath)) {
    throw new Error(`HTML file not found: ${htmlPath}`);
  }

  // Read HTML to check for content
  const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
  if (!htmlContent.includes('STUDY_GUIDE_DATA')) {
    console.warn('Warning: HTML may not have content data injected');
  }

  const browser = await chromium.launch({ headless });
  const context = await browser.newContext();

  // Enable console logging from page
  const page = await context.newPage();
  page.on('console', msg => {
    if (msg.type() === 'log' || msg.type() === 'warn') {
      console.log(`[Page] ${msg.text()}`);
    } else if (msg.type() === 'error') {
      console.error(`[Page Error] ${msg.text()}`);
    }
  });

  page.on('pageerror', error => {
    console.error(`[Page Error] ${error.message}`);
  });

  try {
    // Load the HTML file
    const fileUrl = `file://${path.resolve(htmlPath)}`;
    console.log(`Loading: ${fileUrl}`);

    await page.goto(fileUrl, {
      waitUntil: 'networkidle',
      timeout
    });

    // Wait for MathJax to be ready
    console.log('Waiting for MathJax...');
    await page.waitForFunction(() => {
      return window.MathJax && window.MathJax.startup && window.MathJax.startup.promise;
    }, { timeout: 30000 });

    await page.evaluate(() => window.MathJax.startup.promise);
    console.log('MathJax ready');

    // Wait for study guide ready event
    console.log('Waiting for study guide ready...');
    await page.waitForFunction(() => {
      return document.readyState === 'complete';
    }, { timeout: 10000 });

    // Wait for custom event
    await page.waitForFunction(() => {
      return new Promise(resolve => {
        if (window.studyGuideReady) return resolve(true);
        document.addEventListener('study-guide-ready', () => resolve(true), { once: true });
        setTimeout(() => resolve(true), 5000); // fallback
      });
    }, { timeout: 15000 });

    console.log('Study guide ready, rendering PDF...');

    // Add a small delay for any final rendering
    await page.waitForTimeout(1000);

    // Generate PDF
    await page.pdf({
      path: pdfPath,
      format,
      margin,
      printBackground,
      preferCSSPageSize,
      displayHeaderFooter: true,
      headerTemplate: `
        <div style="font-size: 8px; color: #999; width: 100%; padding: 0 18mm; font-family: Inter, sans-serif;">
          <span class="title"></span>
          <span style="float: right;" class="section"></span>
        </div>
      `,
      footerTemplate: `
        <div style="font-size: 9px; color: #666; width: 100%; padding: 0 18mm; font-family: Inter, sans-serif; text-align: center;">
          <span class="pageNumber"></span> / <span class="totalPages"></span>
        </div>
      `
    });

    console.log(`PDF generated successfully: ${pdfPath}`);

    // Get page count
    const pdfInfo = await getPDFPageCount(pdfPath);
    console.log(`Page count: ${pdfInfo.pages}`);

    return {
      success: true,
      pdfPath,
      pages: pdfInfo.pages,
      fileSize: fs.statSync(pdfPath).size
    };

  } catch (error) {
    console.error('PDF generation failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

async function getPDFPageCount(pdfPath) {
  try {
    const { PDFDocument } = require('pdf-lib');
    const pdfBytes = fs.readFileSync(pdfPath);
    const pdfDoc = await PDFDocument.load(pdfBytes);
    return { pages: pdfDoc.getPageCount() };
  } catch (e) {
    // Fallback: use pdfinfo if available
    try {
      const { execSync } = require('child_process');
      const output = execSync(`pdfinfo "${pdfPath}"`, { encoding: 'utf-8' });
      const match = output.match(/Pages:\s+(\d+)/);
      return { pages: match ? parseInt(match[1]) : 0 };
    } catch {
      return { pages: 0 };
    }
  }
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {};

  args.forEach((arg, i) => {
    if (arg === '--html' && args[i + 1]) options.htmlPath = args[i + 1];
    if (arg === '--pdf' && args[i + 1]) options.pdfPath = args[i + 1];
    if (arg === '--work-dir' && args[i + 1]) options.workDir = args[i + 1];
    if (arg === '--format' && args[i + 1]) options.format = args[i + 1];
    if (arg === '--headless') options.headless = args[i + 1] !== 'false';
    if (arg === '--timeout' && args[i + 1]) options.timeout = parseInt(args[i + 1]);
  });

  renderPDF(options)
    .then(result => {
      console.log('Success:', JSON.stringify(result, null, 2));
      process.exit(0);
    })
    .catch(err => {
      console.error('Failed:', err.message);
      process.exit(1);
    });
}

module.exports = { renderPDF, getPDFPageCount };