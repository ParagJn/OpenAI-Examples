"use client";
import React from 'react';

interface ProjectCardProps {
  name: string;
  description: string;
  tech: string[];
  link?: string;
  onLearnMore?: () => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ name, description, tech, link, onLearnMore }) => (
  <div className="bg-white border border-slate-100 shadow-sm rounded-lg p-6 flex flex-col gap-3 hover:shadow-md transition-shadow duration-200">
    <h4 className="text-lg font-bold text-slate-800 mb-1">{name}</h4>
    <p className="text-slate-600 text-sm mb-2">{description}</p>
    <div className="flex flex-wrap gap-2 mb-2">
      {tech.map(t => (
        <span key={t} className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-1 rounded-full">{t}</span>
      ))}
    </div>
    {link && (
      <button
        className="text-blue-600 text-sm font-medium hover:underline self-start"
        onClick={onLearnMore}
        type="button"
      >
        Learn more
      </button>
    )}
  </div>
);

export default ProjectCard;
