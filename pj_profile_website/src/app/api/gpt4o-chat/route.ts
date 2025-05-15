import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

export async function POST(req: NextRequest) {
  const { messages } = await req.json();
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return NextResponse.json({ answer: 'API key not set.' }, { status: 500 });
  }

  // Use the website content as context (dummy for now, can be improved)
  const context = `Parag's profile website. Home: Generative AI Engineer, Technology Strategist. Highlights: Led AI agent orchestration, Speaker at Generative AI conferences, Architected NLP for healthcare. Projects: Titan, Visionary, InsightX, HealthNLP. Work History: XYZ Corp, ABC HealthTech, DEF Innovations.`;

  const systemPrompt = `You are Parag's helpful AI assistant. Use the following website context to answer questions as helpfully as possible.\n\n${context}`;

  const body = {
    model: 'gpt-4o',
    messages: [
      { role: 'system', content: systemPrompt },
      ...messages
    ],
    max_tokens: 300
  };

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    return NextResponse.json({ answer: 'OpenAI API error.' }, { status: 500 });
  }

  const data = await response.json();
  const answer = data.choices?.[0]?.message?.content || 'No answer.';
  return NextResponse.json({ answer });
}
