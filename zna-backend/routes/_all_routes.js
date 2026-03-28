// ── Cover Letter Routes ──────────────────────────────────────────────────────
const express = require('express');

// cover-letter router
const clRouter = express.Router();
const { generateCoverLetter } = require('../services/coverLetterService');

// POST /api/cover-letter/generate
// Body: { resumeData, jobDescription, tone }
clRouter.post('/generate', async (req, res, next) => {
  try {
    const { resumeData, jobDescription, tone } = req.body;
    if (!resumeData || !jobDescription) {
      return res.status(400).json({ error: 'resumeData and jobDescription are required.' });
    }
    const result = await generateCoverLetter(resumeData, jobDescription, tone);
    res.json({ success: true, data: result });
  } catch (err) {
    next(err);
  }
});

module.exports.coverLetterRouter = clRouter;


// ── ATS Routes ───────────────────────────────────────────────────────────────
const atsRouter = express.Router();
const { runATSScan, extractJobKeywords } = require('../services/atsService');

// POST /api/ats/scan
// Body: { resumeData, jobDescription }
atsRouter.post('/scan', async (req, res, next) => {
  try {
    const { resumeData, jobDescription } = req.body;
    if (!resumeData || !jobDescription) {
      return res.status(400).json({ error: 'resumeData and jobDescription are required.' });
    }
    const result = await runATSScan(resumeData, jobDescription);
    res.json({ success: true, data: result });
  } catch (err) {
    next(err);
  }
});

// POST /api/ats/keywords
// Body: { jobDescription }
atsRouter.post('/keywords', async (req, res, next) => {
  try {
    const { jobDescription } = req.body;
    if (!jobDescription) return res.status(400).json({ error: 'jobDescription is required.' });
    const keywords = await extractJobKeywords(jobDescription);
    res.json({ success: true, data: keywords });
  } catch (err) {
    next(err);
  }
});

module.exports.atsRouter = atsRouter;


// ── PDF Routes ───────────────────────────────────────────────────────────────
const pdfRouter = express.Router();
const { generateResumePDF, generateCoverLetterPDF } = require('../services/pdfService');

// POST /api/pdf/resume
// Body: { resumeData, templateStyle }
pdfRouter.post('/resume', async (req, res, next) => {
  try {
    const { resumeData, templateStyle } = req.body;
    if (!resumeData) return res.status(400).json({ error: 'resumeData is required.' });

    const pdfBuffer = await generateResumePDF(resumeData, templateStyle);

    const filename = `${(resumeData.name || 'resume').replace(/\s+/g, '_')}_resume.pdf`;
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.send(pdfBuffer);
  } catch (err) {
    next(err);
  }
});

// POST /api/pdf/cover-letter
// Body: { coverLetterText, applicantName }
pdfRouter.post('/cover-letter', async (req, res, next) => {
  try {
    const { coverLetterText, applicantName } = req.body;
    if (!coverLetterText) return res.status(400).json({ error: 'coverLetterText is required.' });

    const pdfBuffer = await generateCoverLetterPDF(coverLetterText, applicantName || 'Applicant');

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="cover_letter.pdf"`);
    res.send(pdfBuffer);
  } catch (err) {
    next(err);
  }
});

module.exports.pdfRouter = pdfRouter;


// ── Job Portal Routes ────────────────────────────────────────────────────────
const jobRouter = express.Router();
const { complete } = require('../services/llmService');

// POST /api/jobs/search-suggestions
// Body: { targetJobTitle, skills }
// Returns AI-generated LinkedIn search query + tips
jobRouter.post('/search-suggestions', async (req, res, next) => {
  try {
    const { targetJobTitle, skills } = req.body;
    if (!targetJobTitle) return res.status(400).json({ error: 'targetJobTitle is required.' });

    const system = `You are a job search strategist. Return ONLY valid JSON.`;
    const user = `Generate LinkedIn job search tips for:
Role: ${targetJobTitle}
Skills: ${(skills || []).join(', ')}

Return JSON:
{
  "linkedinSearchURL": "https://www.linkedin.com/jobs/search/?keywords=...",
  "alternativeTitles": [],
  "topCompanies": [],
  "salaryRange": "",
  "searchTips": []
}`;

    const data = await complete(system, user, { jsonMode: true, temperature: 0.3 });
    res.json({ success: true, data });
  } catch (err) {
    next(err);
  }
});

module.exports.jobRouter = jobRouter;
