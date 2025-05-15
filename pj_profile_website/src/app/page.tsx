import React from 'react';
import { HighlightCard, Timeline } from '../components';

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Header Section */}
      <header className="mb-10 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold text-slate-800 mb-2" style={{ fontFamily: 'Aptos Display, sans-serif' }}>Parag Jain</h1>
        <h2 className="text-xl md:text-2xl text-blue-700 font-semibold mb-2">Generative AI Architect | Technology Strategist</h2>
        <p className="text-slate-600 italic mb-4">"Shaping intelligent automations   with AI-driven innovation."</p>
      </header>
      {/* Highlights Section */}
      <section className="mb-12 grid gap-6 md:grid-cols-2">
        <HighlightCard text="Led development of AI agent orchestration framework at scale." />
        <HighlightCard text="Speaker at multiple Generative AI conferences." />
        <HighlightCard text="Architected enterprise-grade NLP solutions for healthcare." />
        <HighlightCard text="Built scalable ML pipelines for real-time analytics." />
      </section>
      {/* Timeline Section */}
      <section>
        <h3 className="text-2xl font-bold text-slate-800 mb-6">Professional Timeline</h3>
        <Timeline />
      </section>
    </div>
  );
}
