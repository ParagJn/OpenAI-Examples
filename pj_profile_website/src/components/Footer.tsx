import React from 'react';

const Footer: React.FC = () => (
  <footer className="w-full bg-white border-t mt-16 py-6 text-center text-sm text-slate-500 flex flex-col items-center gap-2">
    <div className="flex gap-4 justify-center mb-2">
      <a href="#" aria-label="GitHub" className="hover:text-blue-600 transition-colors">
        <svg width="20" height="20" fill="currentColor" className="inline"><path d="M10 .3a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.15-1.1-1.46-1.1-1.46-.9-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.89 1.52 2.34 1.08 2.91.83.09-.65.35-1.08.63-1.33-2.22-.25-4.56-1.11-4.56-4.95 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02A9.56 9.56 0 0 1 10 5.8c.85.004 1.7.11 2.5.32 1.9-1.29 2.74-1.02 2.74-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.85-2.34 4.7-4.57 4.95.36.31.68.92.68 1.86v2.76c0 .27.18.58.69.48A10 10 0 0 0 10 .3"/></svg>
      </a>
      <a href="#" aria-label="LinkedIn" className="hover:text-blue-600 transition-colors">
        <svg width="20" height="20" fill="currentColor" className="inline"><path d="M16.5 2A2.5 2.5 0 0 1 19 4.5v11A2.5 2.5 0 0 1 16.5 18h-13A2.5 2.5 0 0 1 1 15.5v-11A2.5 2.5 0 0 1 3.5 2h13zm-8.75 13V8.75H5.25V15h2.5zm-1.25-7.25a1.25 1.25 0 1 0 0-2.5 1.25 1.25 0 0 0 0 2.5zm9.25 7.25v-3.25c0-1.1-.9-2-2-2s-2 .9-2 2V15h2.5zm-1.25-7.25a1.25 1.25 0 1 0 0-2.5 1.25 1.25 0 0 0 0 2.5z"/></svg>
      </a>
    </div>
    <div>Copyright © 2025 Parag</div>
  </footer>
);

export default Footer;
