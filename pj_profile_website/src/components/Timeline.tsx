"use client";
import React, { useState } from 'react';

const timelineData = [
  {
    year: 2000,
    title: 'Emids Technologies',
    subtitle: 'Software Engineer',
    description: 'Dummy description for Emids Technologies.'
  },
  {
    year: 2003,
    title: 'Placeholder',
    subtitle: '',
    description: 'To be added later.'
  },
  {
    year: 2005,
    title: 'Placeholder',
    subtitle: '',
    description: 'To be added later.'
  },
  {
    year: 2011,
    title: 'Placeholder',
    subtitle: '',
    description: 'To be added later.'
  },
  {
    year: 2025,
    title: "What's next?",
    subtitle: '',
    description: 'Stay tuned.',
    future: true
  }
];

const Timeline: React.FC = () => {
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <div className="relative flex flex-col items-center">
      <div className="border-l-2 border-slate-200 absolute left-6 top-0 h-full z-0" />
      <ul className="space-y-12 w-full">
        {timelineData.map((item, idx) => (
          <li key={item.year} className="relative flex items-center group">
            <button
              className={`z-10 w-12 h-12 flex items-center justify-center rounded-full border-2 ${item.future ? 'border-slate-300 bg-slate-100 text-slate-400 blur-[1px]' : 'border-blue-500 bg-white text-blue-700'} shadow transition-all duration-200 group-hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-400`}
              onClick={() => !item.future && setSelected(idx)}
              disabled={!!item.future}
              aria-label={`Show details for ${item.year}`}
            >
              <span className="font-bold text-lg">{item.year}</span>
            </button>
            <div className="ml-6">
              <div className={`font-semibold ${item.future ? 'text-slate-400' : 'text-slate-800'}`}>{item.title}</div>
              {item.subtitle && <div className="text-slate-500 text-sm">{item.subtitle}</div>}
            </div>
            {/* Modal/Panel */}
            {selected === idx && !item.future && (
              <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={() => setSelected(null)}>
                <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full relative" onClick={e => e.stopPropagation()}>
                  <button className="absolute top-2 right-2 text-slate-400 hover:text-blue-600" onClick={() => setSelected(null)} aria-label="Close">✕</button>
                  <h4 className="text-xl font-bold mb-2">{item.title} <span className="text-slate-500 font-normal">({item.year})</span></h4>
                  <div className="text-slate-600 mb-1">{item.subtitle}</div>
                  <div className="text-slate-700">{item.description}</div>
                </div>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Timeline;
