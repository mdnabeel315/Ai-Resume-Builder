/**
 * Resume Service
 * Handles: auto-parse from raw text, structured data extraction,
 *          AI resume generation in 3 template styles.
 */

const { complete } = require('./llmService');

const TEMPLATES = {
  'Standard Corporate': 'professional, formal, ATS-optimized, conservative layout',
  'Modern Creative': 'modern, visually distinctive, tech-forward, bold section headers',
  'Minimal Clean': 'ultra-minimal, white space focused, clean typography, executive tone',
};

/**
 * Parse raw LinkedIn/resume text into a structured JSON object.
 */
async function parseRawData(rawText) {
  const system = `You are an expert resume parser. Extract structured data from any pasted resume or LinkedIn text.
Return ONLY a valid JSON object — no markdown, no commentary.`;

  const user = `Parse this text into structured JSON with these exact keys:
{
  "name": "",
  "email": "",
  "phone": "",
  "github": "",
  "linkedin": "",
  "summary": "",
  "skills": [],
  "experience": [{ "title": "", "company": "", "duration": "", "bullets": [] }],
  "education": [{ "degree": "", "institution": "", "year": "" }],
  "projects": [{ "name": "", "description": "", "tech": [] }],
  "certifications": []
}

RAW TEXT:
${rawText}`;

  return await complete(system, user, { jsonMode: true, temperature: 0.2 });
}

/**
 * Generate a polished AI resume from structured data.
 */
async function generateResume(parsedData, targetJobTitle, templateStyle = 'Standard Corporate') {
  const templateDesc = TEMPLATES[templateStyle] || TEMPLATES['Standard Corporate'];

  const system = `You are a world-class resume writer specializing in ATS-optimized resumes.
Style: ${templateDesc}.
Write bullet points starting with strong action verbs. Quantify achievements wherever possible.
Return ONLY a valid JSON object — no markdown fences.`;

  const user = `Generate a complete, polished resume for the target role: "${targetJobTitle}".

Candidate Data:
${JSON.stringify(parsedData, null, 2)}

Return JSON with this structure:
{
  "name": "",
  "contact": { "email": "", "phone": "", "github": "", "linkedin": "" },
  "summary": "3-4 sentences tailored to ${targetJobTitle}",
  "skills": { "technical": [], "soft": [] },
  "experience": [{ "title": "", "company": "", "duration": "", "bullets": [] }],
  "education": [{ "degree": "", "institution": "", "year": "" }],
  "projects": [{ "name": "", "description": "", "tech": [] }],
  "certifications": [],
  "atsScore": 0,
  "templateStyle": "${templateStyle}"
}`;

  return await complete(system, user, { jsonMode: true, temperature: 0.5 });
}

module.exports = { parseRawData, generateResume };
