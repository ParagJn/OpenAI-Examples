"use client";
import React from 'react';

interface WorkHistoryCardProps {
  years: string;
  title: string;
  company: string;
  description: string;
}

const WorkHistoryCard: React.FC<WorkHistoryCardProps> = ({ years, title, company, description }) => (
  <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 mb-8">
    <div className="md:w-1/4 w-full text-blue-700 font-semibold text-md md:text-right md:pr-4">{years}</div>
    <div className="md:w-3/4 w-full bg-white border border-slate-100 rounded-lg shadow-sm p-5">
      <div className="font-bold text-slate-800 text-lg mb-1">{title} <span className="text-slate-500 font-normal">@ {company}</span></div>
      <div className="text-slate-600 text-sm">{description}</div>
    </div>
  </div>
);

export default WorkHistoryCard;
