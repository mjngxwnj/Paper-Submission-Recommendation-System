'use client';
import Link from 'next/link';
import { useState } from 'react';
import { useSearch } from './SearchProvider';
import { Search, Moon, Sun } from 'lucide-react';

export default function Navbar() {
  const [darkMode, setDarkMode] = useState(false);
  const { openSearch } = useSearch();

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <nav className="flex items-center justify-between px-8 py-4 bg-[#FDFBF7] dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 transition-colors duration-500 ease-in-out">
      {/* Left: Logo */}
      <div className="flex flex-col">
        <Link href="/" className="text-2xl font-bold text-[#E50914] tracking-tighter">
          PRS
        </Link>
        <span className="text-xs text-slate-500 dark:text-slate-400">
          Paper Recommendation System
        </span>
      </div>

      {/* Center/Right: Search */}
      <div className="hidden md:flex flex-1 max-w-md mx-8 relative">
        <div
          onClick={openSearch}
          className="relative w-full group cursor-pointer"
        >
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 group-hover:text-[#E50914] w-4 h-4 transition-colors duration-300" />
          <div
            className="w-full pl-10 pr-4 py-2 bg-slate-100 dark:bg-slate-800 rounded-full text-sm text-slate-500 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white group-hover:ring-2 group-hover:ring-[#E50914]/20 transition-all duration-300"
          >
            Search papers, authors, journals...
          </div>
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 hidden group-hover:block transition-opacity duration-300">
            <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-bold text-slate-400 border border-slate-300 rounded-md bg-white ml-2">⌘K</kbd>
          </div>
        </div>
      </div>

      {/* Action Items */}
      <div className="flex items-center gap-4">
        <Link
          href="/recommendations"
          className="hidden md:block px-4 py-2 text-sm font-medium text-[#E50914] border border-[#E50914] rounded hover:bg-[#E50914] hover:text-white dark:hover:bg-[#E50914] transition-colors"
        >
          Try Recommendations
        </Link>
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors"
        >
          {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        <div className="w-8 h-8 rounded-full bg-slate-300 dark:bg-slate-700 overflow-hidden text-slate-700 dark:text-slate-200">
          {/* User Avatar Placeholder */}
          <div className="w-full h-full flex items-center justify-center text-xs font-bold">U</div>
        </div>
      </div>
    </nav>
  );
}
