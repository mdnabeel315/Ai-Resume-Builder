/**
 * PDF Generation Service
 * Converts resume JSON → styled HTML → PDF using Puppeteer.
 */

const puppeteer = require('puppeteer');

/**
 * Build HTML for a given resume and template style.
 */
function buildResumeHTML(resume, templateStyle = 'Standard Corporate') {
  const themes = {
    'Standard Corporate': {
      fontFamily: "'Georgia', serif",
      accentColor: '#1a365d',
      headingColor: '#1a365d',
      borderColor: '#2b6cb0',
    },
    'Modern Creative': {
      fontFamily: "'Arial", "sans-serif'",
      accentColor: '#6b21a8',
      headingColor: '#4c1d95',
      borderColor: '#7c3aed',
    },
    'Minimal Clean': {
      fontFamily: "'Helvetica Neue', Arial, sans-serif",
      accentColor: '#111827',
      headingColor: '#111827',
      borderColor: '#9ca3af',
    },
  };

  const t = themes[templateStyle] || themes['Standard Corporate'];
  const exp = resume.experience || [];
  const edu = resume.education || [];
  const projects = resume.projects || [];
  const skills = resume.skills || {};
  const contact = resume.contact || {};

  const experienceHTML = exp.map(e => `
    <div class="entry">
      <div class="entry-header">
        <strong>${e.title}</strong> — ${e.company}
        <span class="duration">${e.duration}</span>
      </div>
      <ul>${(e.bullets || []).map(b => `<li>${b}</li>`).join('')}</ul>
    </div>
  `).join('');

  const educationHTML = edu.map(e => `
    <div class="entry">
      <div class="entry-header">
        <strong>${e.degree}</strong> — ${e.institution}
        <span class="duration">${e.year}</span>
      </div>
    </div>
  `).join('');

  const projectsHTML = projects.map(p => `
    <div class="entry">
      <strong>${p.name}</strong>
      <p>${p.description}</p>
      <span class="tech">${(p.tech || []).join(' · ')}</span>
    </div>
  `).join('');

  const technicalSkills = (skills.technical || []).join(' · ');
  const softSkills = (skills.soft || []).join(' · ');

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: ${t.fontFamily};
      color: #1a1a1a;
      font-size: 11px;
      line-height: 1.5;
      padding: 40px 50px;
    }
    h1 {
      font-size: 24px;
      color: ${t.headingColor};
      letter-spacing: 0.5px;
    }
    .contact-line {
      font-size: 10px;
      color: #555;
      margin: 4px 0 16px;
    }
    .contact-line a { color: ${t.accentColor}; text-decoration: none; }
    h2 {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      color: ${t.headingColor};
      border-bottom: 1.5px solid ${t.borderColor};
      padding-bottom: 3px;
      margin: 18px 0 10px;
    }
    .summary { font-size: 11px; color: #333; margin-bottom: 4px; }
    .entry { margin-bottom: 10px; }
    .entry-header {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
    }
    .duration { color: #666; font-style: italic; }
    ul { margin-left: 16px; margin-top: 4px; }
    li { margin-bottom: 2px; }
    .tech { font-size: 10px; color: ${t.accentColor}; }
    .skills-block { font-size: 11px; color: #333; }
    .skills-label { font-weight: bold; margin-right: 4px; }
  </style>
</head>
<body>
  <h1>${resume.name || 'Your Name'}</h1>
  <div class="contact-line">
    ${contact.email ? `<a href="mailto:${contact.email}">${contact.email}</a>` : ''}
    ${contact.phone ? ` · ${contact.phone}` : ''}
    ${contact.linkedin ? ` · <a href="${contact.linkedin}">LinkedIn</a>` : ''}
    ${contact.github ? ` · <a href="${contact.github}">GitHub</a>` : ''}
  </div>

  ${resume.summary ? `<h2>Summary</h2><p class="summary">${resume.summary}</p>` : ''}

  ${(skills.technical?.length || skills.soft?.length) ? `
  <h2>Skills</h2>
  <div class="skills-block">
    ${technicalSkills ? `<span class="skills-label">Technical:</span>${technicalSkills}<br>` : ''}
    ${softSkills ? `<span class="skills-label">Soft:</span>${softSkills}` : ''}
  </div>` : ''}

  ${exp.length ? `<h2>Experience</h2>${experienceHTML}` : ''}
  ${edu.length ? `<h2>Education</h2>${educationHTML}` : ''}
  ${projects.length ? `<h2>Projects</h2>${projectsHTML}` : ''}
</body>
</html>`;
}

/**
 * Generate a PDF buffer from resume JSON.
 * @returns {Buffer}
 */
async function generateResumePDF(resume, templateStyle = 'Standard Corporate') {
  const html = buildResumeHTML(resume, templateStyle);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'networkidle0' });

  const pdfBuffer = await page.pdf({
    format: 'A4',
    printBackground: true,
    margin: { top: '0', right: '0', bottom: '0', left: '0' },
  });

  await browser.close();
  return pdfBuffer;
}

/**
 * Generate a plain-text PDF for a cover letter.
 */
async function generateCoverLetterPDF(coverLetterText, applicantName) {
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      font-family: 'Georgia', serif;
      font-size: 12px;
      line-height: 1.8;
      padding: 60px 70px;
      color: #1a1a1a;
    }
    .name { font-size: 18px; font-weight: bold; margin-bottom: 30px; }
    .date { color: #666; margin-bottom: 30px; }
    p { margin-bottom: 16px; }
  </style>
</head>
<body>
  <div class="name">${applicantName}</div>
  <div class="date">${new Date().toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' })}</div>
  ${coverLetterText.split('\n\n').map(p => `<p>${p}</p>`).join('')}
</body>
</html>`;

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: 'networkidle0' });
  const pdfBuffer = await page.pdf({ format: 'A4', printBackground: true });
  await browser.close();
  return pdfBuffer;
}

module.exports = { generateResumePDF, generateCoverLetterPDF };
