/**
 * Cover Letter Service
 * Generates highly personalized cover letters from resume + job description.
 */

const { complete } = require('./llmService');

/**
 * Generate a tailored cover letter.
 * @param {object} resumeData - structured resume from resumeService
 * @param {string} jobDescription - target job description
 * @param {string} tone - 'professional' | 'enthusiastic' | 'concise'
 */
async function generateCoverLetter(resumeData, jobDescription, tone = 'professional') {
  const toneGuide = {
    professional: 'Formal, confident, achievement-focused. No fluff.',
    enthusiastic: 'Warm, energetic, passionate about the role. Show genuine excitement.',
    concise: 'Ultra-brief, 3 tight paragraphs. Every sentence earns its place.',
  };

  const system = `You are an elite cover letter writer.
Tone: ${toneGuide[tone] || toneGuide['professional']}
Rules:
- Never start with "I am writing to..."
- Lead with a strong, specific hook about the role or company
- Reference 2-3 concrete achievements with numbers from the resume
- End with a confident, non-desperate call to action
- Maximum 350 words`;

  const user = `Write a tailored cover letter for:

APPLICANT RESUME:
Name: ${resumeData.name}
Target Role: ${resumeData.targetJobTitle || 'the position'}
Key Experience: ${JSON.stringify(resumeData.experience?.slice(0, 2))}
Top Skills: ${JSON.stringify(resumeData.skills)}

JOB DESCRIPTION:
${jobDescription}

Return ONLY the cover letter text — no subject lines, no metadata.`;

  const letterText = await complete(system, user, { temperature: 0.75 });

  return {
    text: letterText,
    wordCount: letterText.split(' ').length,
    tone,
    generatedAt: new Date().toISOString(),
  };
}

module.exports = { generateCoverLetter };
