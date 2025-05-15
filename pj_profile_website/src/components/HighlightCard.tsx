"use client";
import React from 'react';

interface HighlightCardProps {
  text: string;
}

const HighlightCard: React.FC<HighlightCardProps> = ({ text }) => (
  <div className="bg-white border border-slate-100 shadow-sm rounded-lg p-5 flex items-center gap-3 transition-transform hover:scale-105 hover:shadow-md duration-200">
    <span className="text-green-600 text-xl">✅</span>
    <span className="text-slate-700 font-medium">{text}</span>
  </div>
);

export default HighlightCard;
