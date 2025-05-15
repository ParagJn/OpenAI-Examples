"use client";
import React, { useState } from 'react';
import Link from 'next/link';

const navLinks = [
  { name: 'Home', href: '/' },
  { name: 'Projects', href: '/projects' },
  { name: 'Work History', href: '/work-history' },
];

const Navbar: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [contactOpen, setContactOpen] = useState(false);

  React.useEffect(() => {
    if (!contactOpen) return;
    const handleClick = (e: MouseEvent) => {
      // Only close if click is outside the popover
      setContactOpen(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [contactOpen]);

  return (
    <nav className="w-full bg-white dark:bg-slate-900 shadow-sm fixed top-0 left-0 z-50">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-16 relative">
        <div className="relative flex items-center">
          <Link href="#" onClick={e => { e.preventDefault(); setContactOpen(true); }} className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-blue-400" aria-label="Open contact card">
            <img src="/home_icon.png" alt="Home" className="w-8 h-8 rounded-full shadow bg-slate-100 dark:bg-slate-800" />
          </Link>
          {/* Contact Card Popover */}
          {contactOpen && (
            <div
              className="absolute left-0 top-12 z-50 animate-slideDown bg-white dark:bg-slate-900 rounded-xl shadow-2xl p-6 w-72 border border-slate-100 dark:border-slate-800 flex flex-col items-start gap-4 transition-transform duration-300"
              style={{ minWidth: '260px' }}
              onClick={e => e.stopPropagation()}
            >
              <button className="absolute top-2 right-2 text-slate-400 hover:text-blue-600 dark:hover:text-white" onClick={() => setContactOpen(false)} aria-label="Close contact card">✕</button>
              <img src="/home_icon.png" alt="Profile" className="w-14 h-14 rounded-full shadow mb-2 bg-slate-100 dark:bg-slate-800 self-start" />
              <h2 className="text-lg font-bold text-slate-800 dark:text-white text-left w-full">Parag Jain</h2>
              <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300 w-full text-left">
                <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 5.5A2.5 2.5 0 0 1 5.5 3h9A2.5 2.5 0 0 1 17 5.5v9A2.5 2.5 0 0 1 14.5 17h-9A2.5 2.5 0 0 1 3 14.5v-9Z"/><path d="M8 7h4M8 10h4M8 13h2"/></svg>
                <span>+91-9876543210</span>
              </div>
              <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300 w-full text-left">
                <svg width="20" height="20" fill="currentColor" className="inline"><path d="M10 .3a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.15-1.1-1.46-1.1-1.46-.9-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.89 1.52 2.34 1.08 2.91.83.09-.65.35-1.08.63-1.33-2.22-.25-4.56-1.11-4.56-4.95 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02A9.56 9.56 0 0 1 10 5.8c.85.004 1.7.115 2.5.337 1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.85-2.34 4.7-4.57 4.95.36.31.68.92.68 1.85v2.75c0 .27.18.58.69.48A10 10 0 0 0 10 .3Z"/></svg>
                <a href="https://github.com/paragjain" target="_blank" rel="noopener noreferrer" className="hover:underline">@paragjain</a>
              </div>
              <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300 w-full text-left">
                <svg width="20" height="20" fill="currentColor" className="inline"><path d="M16.5 2A2.5 2.5 0 0 1 19 4.5v11A2.5 2.5 0 0 1 16.5 18h-13A2.5 2.5 0 0 1 1 15.5v-11A2.5 2.5 0 0 1 3.5 2h13zm-8.75 13V8.75H5.25V15h2.5zm-1.25-7.25a1.25 1.25 0 1 0 0-2.5 1.25 1.25 0 0 0 0 2.5zm9.25 7.25v-3.25c0-1.1-.9-2-2-2s-2 .9-2 2V15h2.5zm-4.25 0V8.75H10.5V15h2.5z"/></svg>
                <a href="https://linkedin.com/in/paragjain" target="_blank" rel="noopener noreferrer" className="hover:underline">LinkedIn</a>
              </div>
              <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300 w-full text-left">
                <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="4"/><path d="M6 16c0-2.21 3.58-4 8-4s8 1.79 8 4"/></svg>
                <span>India</span>
              </div>
            </div>
          )}
        </div>
        <div className="hidden md:flex gap-8">
          {navLinks.map(link => (
            <Link key={link.name} href={link.href} className="text-slate-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-300 font-medium transition-colors duration-200">
              {link.name}
            </Link>
          ))}
        </div>
        <div className="md:hidden">
          <button
            aria-label="Open menu"
            className="p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-700 dark:text-white"><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="18" x2="21" y2="18" /></svg>
          </button>
        </div>
      </div>
      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden bg-white dark:bg-slate-900 shadow-lg border-t border-slate-100 dark:border-slate-800">
          <div className="flex flex-col items-center gap-6 py-6">
            {navLinks.map(link => (
              <Link
                key={link.name}
                href={link.href}
                className="text-slate-700 dark:text-white hover:text-blue-600 dark:hover:text-blue-300 font-medium text-lg"
                onClick={() => setMenuOpen(false)}
              >
                {link.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
