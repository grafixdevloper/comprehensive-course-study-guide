/**
 * PDF Page Renderer for Visual QA
 * Renders each PDF page as a PNG image for visual inspection
 */

const fs = require('fs');
const path = require('path');

async function renderPDFPages(options = {}) {
  const {
    pdfPath = 'study-guide-output/study-guide.pdf',
    outputDir = '.study-guide-work/qa/pages',
    dpi = 300,
    format = 'png',
    prefix = 'page-',
    maxPages = 0 // 0 = all pages
  } = options;

  const { chromium } = require('playwright');

  console.log('Starting PDF page rendering for visual QA...');
  console.log(`PDF: ${pdfPath}`);
  console.log(`Output: ${outputDir}`);

  if (!fs.existsSync(pdfPath)) {
    throw new Error(`PDF file not found: ${pdfPath}`);
  }

  // Ensure output directory exists
  fs.mkdirSync(outputDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();

  try {
    // First, get page count using pdf-lib
    let pageCount = 0;
    try {
      const { PDFDocument } = require('pdf-lib');
      const pdfBytes = fs.readFileSync(pdfPath);
      const pdfDoc = await PDFDocument.load(pdfBytes);
      pageCount = pdfDoc.getPageCount();
    } catch (e) {
      // Fallback to pdfinfo
      try {
        const { execSync } = require('child_process');
        const output = execSync(`pdfinfo "${pdfPath}"`, { encoding: 'utf-8' });
        const match = output.match(/Pages:\s+(\d+)/);
        pageCount = match ? parseInt(match[1]) : 0;
      } catch {
        throw new Error('Could not determine PDF page count');
      }
    }

    if (pageCount === 0) {
      throw new Error('PDF has no pages');
    }

    console.log(`PDF has ${pageCount} pages`);

    const pagesToRender = maxPages > 0 ? Math.min(pageCount, maxPages) : pageCount;
    const results = [];

    for (let pageNum = 1; pageNum <= pagesToRender; pageNum++) {
      console.log(`Rendering page ${pageNum}/${pagesToRender}...`);

      const page = await context.newPage();

      // Create an HTML page that displays the PDF page
      const pdfUrl = `file://${path.resolve(pdfPath)}#page=${pageNum}`;

      // Use a simple viewer page
      const viewerHTML = `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background: #ccc; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .page-container { background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
            .page-image { display: block; }
          </style>
        </head>
        <body>
          <div class="page-container">
            <embed class="page-image" src="${pdfUrl}" type="application/pdf" width="100%" height="100%" />
          </div>
        </body>
        </html>
      `;

      // Write temporary viewer
      const viewerPath = path.join(outputDir, `viewer-${pageNum}.html`);
      fs.writeFileSync(viewerPath, viewerHTML);

      await page.goto(`file://${path.resolve(viewerPath)}`, {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      // Wait for PDF to render
      await page.waitForTimeout(2000);

      // Take screenshot of the page container
      const container = await page.$('.page-container');
      if (container) {
        const outputPath = path.join(outputDir, `${prefix}${pageNum.toString().padStart(4, '0')}.${format}`);
        await container.screenshot({ path: outputPath });
        console.log(`  Saved: ${outputPath}`);
        results.push({ page: pageNum, path: outputPath });
      } else {
        console.warn(`  Could not find page container for page ${pageNum}`);
      }

      await page.close();

      // Clean up viewer
      try { fs.unlinkSync(viewerPath); } catch {}
    }

    console.log(`\nRendered ${results.length} pages to ${outputDir}`);

    return {
      success: true,
      pageCount,
      renderedPages: results.length,
      outputDir,
      pages: results
    };

  } catch (error) {
    console.error('Page rendering failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

// Alternative method: use pdf.js or direct PDF rendering
async function renderPDFPagesDirect(options = {}) {
  const {
    pdfPath = 'study-guide-output/study-guide.pdf',
    outputDir = '.study-guide-work/qa/pages',
    scale = 3.0, // 3x = ~300 DPI for 72 DPI base
    format = 'png',
    prefix = 'page-'
  } = options;

  // This method uses pdf-lib to get page count and pdf.js for rendering
  // For now, we'll use the Playwright embed method above
  return renderPDFPages(options);
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {};

  args.forEach((arg, i) => {
    if (arg === '--pdf' && args[i + 1]) options.pdfPath = args[i + 1];
    if (arg === '--output' && args[i + 1]) options.outputDir = args[i + 1];
    if (arg === '--dpi' && args[i + 1]) options.dpi = parseInt(args[i + 1]);
    if (arg === '--max-pages' && args[i + 1]) options.maxPages = parseInt(args[i + 1]);
  });

  renderPDFPages(options)
    .then(result => {
      console.log('Success:', JSON.stringify(result, null, 2));
      process.exit(0);
    })
    .catch(err => {
      console.error('Failed:', err.message);
      process.exit(1);
    });
}

module.exports = { renderPDFPages, renderPDFPagesDirect };