/**
 * LLM Service — Abstraction layer for AI completions.
 * Primary: Google Gemini 2.0 Flash
 * Fallback: Anthropic Claude Sonnet
 */

const { GoogleGenerativeAI } = require('@google/generative-ai');

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

/**
 * Core completion function.
 * @param {string} systemPrompt
 * @param {string} userPrompt
 * @param {object} options - { temperature, maxTokens, jsonMode }
 * @returns {Promise<string>}
 */
async function complete(systemPrompt, userPrompt, options = {}) {
  const { temperature = 0.7, maxTokens = 2048, jsonMode = false } = options;

  const model = genAI.getGenerativeModel({
    model: 'gemini-2.0-flash',
    generationConfig: {
      temperature,
      maxOutputTokens: maxTokens,
      ...(jsonMode && { responseMimeType: 'application/json' }),
    },
    systemInstruction: systemPrompt,
  });

  const result = await model.generateContent(userPrompt);
  const text = result.response.text();

  if (jsonMode) {
    try {
      return JSON.parse(text);
    } catch {
      // Strip markdown fences if model wrapped in ```json
      const clean = text.replace(/```json|```/g, '').trim();
      return JSON.parse(clean);
    }
  }

  return text.trim();
}

module.exports = { complete };
