const express = require('express');
const router = express.Router();
const { parseRawData, generateResume } = require('../services/resumeService');

// POST /api/resume/parse
// Body: { rawText: string }
router.post('/parse', async (req, res, next) => {
  try {
    const { rawText } = req.body;
    if (!rawText?.trim()) return res.status(400).json({ error: 'rawText is required.' });

    const parsed = await parseRawData(rawText);
    res.json({ success: true, data: parsed });
  } catch (err) {
    next(err);
  }
});

// POST /api/resume/generate
// Body: { parsedData, targetJobTitle, templateStyle }
router.post('/generate', async (req, res, next) => {
  try {
    const { parsedData, targetJobTitle, templateStyle } = req.body;
    if (!parsedData || !targetJobTitle) {
      return res.status(400).json({ error: 'parsedData and targetJobTitle are required.' });
    }

    const resume = await generateResume(parsedData, targetJobTitle, templateStyle);
    res.json({ success: true, data: resume });
  } catch (err) {
    next(err);
  }
});

// POST /api/resume/parse-and-generate
// Convenience: parse raw text + generate resume in one call
// Body: { rawText, targetJobTitle, templateStyle, name, email, phone, github, linkedin }
router.post('/parse-and-generate', async (req, res, next) => {
  try {
    const { rawText, targetJobTitle, templateStyle, name, email, phone, github, linkedin } = req.body;
    if (!rawText?.trim() || !targetJobTitle) {
      return res.status(400).json({ error: 'rawText and targetJobTitle are required.' });
    }

    // Parse raw data
    const parsed = await parseRawData(rawText);

    // Override with explicit form fields if provided
    if (name) parsed.name = name;
    if (email) parsed.email = email;
    if (phone) parsed.phone = phone;
    if (github) parsed.github = github;
    if (linkedin) parsed.linkedin = linkedin;

    // Generate polished resume
    const resume = await generateResume(parsed, targetJobTitle, templateStyle);

    res.json({ success: true, data: { parsed, resume } });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
