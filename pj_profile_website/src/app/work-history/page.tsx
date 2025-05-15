import React from 'react';
import WorkHistoryCard from '../../components/WorkHistoryCard';

const workHistory = [
  {
    years: '2012 – Present',
    title: 'Lead Assest Engineering Services - Generative AI',
    company: 'IBM India Pvt. Ltd.',
    description: 'Led a team of AI engineers building real-time conversational agents.'
  },
  {
    years: '2017 – 2021',
    title: 'Senior NLP Specialist',
    company: 'ABC HealthTech',
    description: 'Developed entity recognition pipelines for patient data analysis.'
  },
  {
    years: '2011 – 2017',
    title: 'ML Engineer',
    company: 'DEF Innovations',
    description: 'Worked on predictive analytics for operational efficiency.'
  }
];

const WorkHistoryPage: React.FC = () => (
  <div className="max-w-4xl mx-auto px-4 py-12">
    <h1 className="text-3xl font-bold text-slate-800 mb-8 text-center">Work History</h1>
    <div>
      {workHistory.map((job, idx) => (
        <WorkHistoryCard key={idx} {...job} />
      ))}
    </div>
  </div>
);

export default WorkHistoryPage;
