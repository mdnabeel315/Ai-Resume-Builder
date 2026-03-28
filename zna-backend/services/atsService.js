/**
 * ATS Match Engine Service
 * Semantic NLP-based keyword matching between resume and job description.
 */

const { complete } = require('./llmService');

/**
 * Run a deep ATS scan comparing resume data against a job description.
 * Returns a score, matched keywords, missing keywords, and improvement tips.
 */
async function runATSScan(resumeData, jobDescription) {
  const system = `You are an expert ATS (Applicant Tracking System) analyst with deep knowledge of
semantic keyword matching, role-specific terminology, and recruiter patterns.
Return ONLY a valid JSON object — no markdown, no commentary.`;

  const user = `Perform a deep ATS analysis. Compare this resume against the job description.

RESUME:
${JSON.stringify(resumeData, null, 2)}

JOB DESCRIPTION:
${jobDescription}

Return JSON:
{
  "overallScore": 0-100,
  "breakdown": {
    "keywordMatch": 0-100,
    "skillsAlignment": 0-100,
    "experienceRelevance": 0-100,
    "titleMatch": 0-100
  },
  "matchedKeywords": [],
  "missingKeywords": [],
  "missingSkills": [],
  "strengths": [],
  "improvements": [{ "section": "", "suggestion": "" }],
  "verdict": "Strong Match | Good Match | Partial Match | Weak Match"
}`;

  return await complete(system, user, { jsonMode: true, temperature: 0.2 });
}

/**
 * Extract the top keywords from a job description.
 */
async function extractJobKeywords(jobDescription) {
  const system = `You are a technical recruiter. Extract key skills, technologies, and requirements.
Return ONLY a valid JSON object.`;

  const user = `Extract keywords from this job description:

${jobDescription}

Return:
{
  "hardSkills": [],
  "softSkills": [],
  "tools": [],
  "qualifications": [],
  "niceToHave": []
}`;

  return await complete(system, user, { jsonMode: true, temperature: 0.1 });
}

module.exports = { runATSScan, extractJobKeywords };
