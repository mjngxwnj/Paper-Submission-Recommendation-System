'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Loader2, FileText, BookOpen, User } from 'lucide-react';
import { searchGlobal } from '../services/mockBackend';
import { SearchResult } from '../types';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      // Focus input when modal opens
      setTimeout(() => inputRef.current?.focus(), 100);
      document.body.style.overflow = 'hidden'; // Prevent scrolling
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev < results.length - 1 ? prev + 1 : prev));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : prev));
      } else if (e.key === 'Enter' && selectedIndex >= 0) {
        // Handle selection (for now just log or alert)
        // console.log('Selected:', results[selectedIndex]);
        // In a real app, router.push(results[selectedIndex].url)
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex, onClose]);

  useEffect(() => {
    const fetchResults = async () => {
      if (!query.trim()) {
        setResults([]);
        return;
      }

      setIsLoading(true);
      try {
        const data = await searchGlobal(query);
        setResults(data);
        setSelectedIndex(-1); // Reset selection
      } catch (error) {
        console.error('Search failed', error);
      } finally {
        setIsLoading(false);
      }
    };

    const debounce = setTimeout(fetchResults, 300);
    return () => clearTimeout(debounce);
  }, [query]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4">
      {/* Backdrop with blur */}
      <div
        className="fixed inset-0 bg-white/60 dark:bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Content */}
      <div className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-lg shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[80vh] animate-in fade-in zoom-in-95 duration-200">

        {/* Search Header */}
        <div className="flex items-center px-4 py-4 border-b border-slate-100 dark:border-slate-800">
          <Search className="w-5 h-5 text-slate-400 mr-3" />
          <input
            ref={inputRef}
            type="text"
            className="flex-1 bg-transparent text-lg text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none"
            placeholder="Search papers, authors, journals..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            onClick={onClose}
            className="flex items-center text-xs text-slate-500 border border-slate-200 dark:border-slate-700 rounded px-2 py-1 ml-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <span className="mr-1">ESC</span>
            <X className="w-3 h-3" />
          </button>
        </div>

        {/* Results or Loading or Empty State */}
        <div className="flex-1 overflow-y-auto min-h-[100px] p-2">
          {isLoading ? (
            <div className="flex items-center justify-center py-12 text-slate-500">
              <Loader2 className="w-6 h-6 animate-spin mr-2" />
              <span>Searching...</span>
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-1">
              {results.map((result, index) => (
                <div
                  key={result.id}
                  className={`flex items-center px-4 py-3 rounded-md cursor-pointer transition-colors ${index === selectedIndex
                      ? 'bg-slate-100 dark:bg-slate-800 text-[#E50914]'
                      : 'hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-700 dark:text-slate-200'
                    }`}
                  onClick={() => {
                    // console.log('Clicked:', result);
                    onClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(index)}
                >
                  <div className={`p-2 rounded mr-4 ${result.type === 'venue' ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400' :
                      result.type === 'paper' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' :
                        'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}>
                    {result.type === 'venue' && <BookOpen className="w-5 h-5" />}
                    {result.type === 'paper' && <FileText className="w-5 h-5" />}
                    {result.type === 'author' && <User className="w-5 h-5" />}
                  </div>
                  <div>
                    <div className="font-medium text-sm sm:text-base">
                      {result.title}
                    </div>
                    {result.subtitle && (
                      <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        {result.subtitle}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : query ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <p className="text-sm">No results found for "{query}"</p>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <p className="text-sm">Start typing to search...</p>
            </div>
          )}
        </div>

        {/* Footer */}
        {results.length > 0 && (
          <div className="px-4 py-2 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center text-xs text-slate-400">
            <div className="flex gap-4">
              <span className="flex items-center">
                <span className="font-bold mr-1">↵</span> to select
              </span>
              <span className="flex items-center">
                <span className="font-bold mr-1">↑↓</span> to navigate
              </span>
            </div>
            <div>
              Search powered by <span className="text-[#E50914] font-medium">PRS AI</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
