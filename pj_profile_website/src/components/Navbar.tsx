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

  return (
    <nav className="w-full bg-white dark:bg-slate-900 shadow-sm fixed top-0 left-0 z-50">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-16">
        <Link href="/" className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white flex items-center gap-2">
          <span className="rounded-full bg-slate-100 dark:bg-slate-800 px-3 py-1 text-blue-600 dark:text-white font-extrabold text-lg shadow">P</span>
        </Link>
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
