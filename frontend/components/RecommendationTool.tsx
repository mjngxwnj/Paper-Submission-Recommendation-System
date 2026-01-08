'use client';
import React, { useState } from 'react';
import { Search, X, BookOpen, Lock, LockOpen } from 'lucide-react';
import { RecommendationRequest, Venue } from '../types';
import { fetchRecommendations } from '../services/api';

export const RecommendationTool = () => {
  const [formData, setFormData] = useState<RecommendationRequest>({
    title: '',
    abstract: '',
    keywords: ''
  });
  const [results, setResults] = useState<Venue[] | null>(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (field: keyof RecommendationRequest, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const clearForm = () => {
    setFormData({ title: '', abstract: '', keywords: '' });
    setResults(null);
  };

  const handleSearch = async () => {
    if (!formData.title || !formData.abstract) return; // Simple validation

    setLoading(true);
    setResults(null);
    try {
      const data = await fetchRecommendations(formData);
      setResults(data);
    } catch (error) {
      console.error("Failed to fetch recommendations", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FDFBF7] dark:bg-slate-950 py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
      <div className="max-w-7xl mx-auto space-y-12">

        {/* Input Section */}
        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-gray-100 dark:border-slate-800 p-6 md:p-8 animate-fade-in-up">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center space-x-3">
              <Search className="w-6 h-6 text-[#E50914]" />
              <h2 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-white">
                Find the right journals for your submissions
              </h2>
            </div>
            <button onClick={clearForm} className="text-sm text-gray-500 hover:text-[#E50914] underline">
              Clear All
            </button>
          </div>

          <div className="space-y-6">
            {/* Title Input */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
              <label className="md:col-span-2 text-sm font-semibold text-slate-700 dark:text-slate-300 pt-2">
                Title
              </label>
              <div className="md:col-span-10 relative">
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className="w-full p-3 bg-gray-50 dark:bg-slate-800 border-none rounded-md focus:ring-2 focus:ring-[#E50914] text-slate-900 dark:text-white"
                  placeholder="Enter paper title..."
                />
                {formData.title && (
                  <button onClick={() => handleInputChange('title', '')} className="absolute right-3 top-3 text-gray-400 hover:text-gray-600">
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Abstract Input */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
              <label className="md:col-span-2 text-sm font-semibold text-slate-700 dark:text-slate-300 pt-2">
                Abstract
              </label>
              <div className="md:col-span-10 relative">
                <textarea
                  rows={6}
                  value={formData.abstract}
                  onChange={(e) => handleInputChange('abstract', e.target.value)}
                  className="w-full p-3 bg-gray-50 dark:bg-slate-800 border-none rounded-md focus:ring-2 focus:ring-[#E50914] text-slate-900 dark:text-white resize-none"
                  placeholder="Paste your abstract here (min 50 words)..."
                />
                {formData.abstract && (
                  <button onClick={() => handleInputChange('abstract', '')} className="absolute right-3 top-3 text-gray-400 hover:text-gray-600">
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Keywords Input */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
              <label className="md:col-span-2 text-sm font-semibold text-slate-700 dark:text-slate-300 pt-2">
                Keywords
              </label>
              <div className="md:col-span-10 relative">
                <input
                  type="text"
                  value={formData.keywords}
                  onChange={(e) => handleInputChange('keywords', e.target.value)}
                  className="w-full p-3 bg-gray-50 dark:bg-slate-800 border-none rounded-md focus:ring-2 focus:ring-[#E50914] text-slate-900 dark:text-white"
                  placeholder="e.g. deep learning; recommender systems; collaborative filtering"
                />
                {formData.keywords && (
                  <button onClick={() => handleInputChange('keywords', '')} className="absolute right-3 top-3 text-gray-400 hover:text-gray-600">
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Placeholder Space
            <div className="px-0 pb-0">
              <div className="h-32 border-2 border-dashed border-gray-200 dark:border-slate-700 rounded-lg flex items-center justify-center text-gray-400 text-sm bg-gray-50 dark:bg-slate-800/50">
                <span className="italic">Additional details or file upload area (placeholder)</span>
              </div>
            </div> */}

            <div className="flex justify-end pt-4 border-t border-gray-100 dark:border-slate-800">
              <button
                onClick={handleSearch}
                disabled={loading || !formData.title}
                className={`px-8 py-3 rounded-md font-bold text-white transition-all shadow-md ${loading || !formData.title
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-[#E50914] hover:bg-red-700 hover:shadow-lg transform hover:-translate-y-0.5'
                  }`}
              >
                {loading ? 'Analyzing...' : 'Search'}
              </button>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {results && (
          <div className="animate-fade-in">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-6">
              Here is the list of the most relevant journals for your submission:
              <span className="text-sm font-normal text-gray-500 ml-2">({results.length} results)</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {results.map((venue) => (
                <div key={venue.id} className="bg-white dark:bg-slate-900 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden border border-gray-100 dark:border-slate-800 flex flex-col h-full">
                  {/* Card Header with Color Gradient */}
                  <div
                    className="h-32 p-4 relative"
                    style={{ background: `linear-gradient(135deg, ${venue.coverColor}dd 0%, ${venue.coverColor}88 100%)` }}
                  >
                    <h4 className="text-white font-bold text-lg leading-tight drop-shadow-md">
                      {venue.name}
                    </h4>
                    <div className="absolute bottom-[-16px] left-4">
                      <div className="w-12 h-12 bg-white dark:bg-slate-800 rounded shadow-md flex items-center justify-center">
                        <BookOpen className="w-6 h-6 text-slate-700 dark:text-slate-300" />
                      </div>
                    </div>
                  </div>

                  {/* Card Body */}
                  <div className="pt-8 pb-4 px-4 flex-1 flex flex-col justify-between space-y-4">

                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between items-center border-b border-gray-100 dark:border-slate-800 pb-2">
                        <span className="font-semibold text-slate-700 dark:text-slate-300">Impact Factor</span>
                        <span className="text-slate-900 dark:text-white font-bold">{venue.impactFactor.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between items-center border-b border-gray-100 dark:border-slate-800 pb-2">
                        <span className="font-semibold text-slate-700 dark:text-slate-300">Index</span>
                        <span className="text-slate-500 dark:text-slate-400 text-xs text-right">
                          {venue.indexing.join(', ')}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="font-semibold text-slate-700 dark:text-slate-300">Open Access</span>
                        <span className={`flex items-center text-xs font-bold ${venue.openAccess ? 'text-green-600' : 'text-gray-500'}`}>
                          {venue.openAccess ? <LockOpen className="w-3 h-3 mr-1" /> : <Lock className="w-3 h-3 mr-1" />}
                          {venue.openAccess ? 'Yes' : 'No'}
                        </span>
                      </div>
                    </div>

                    <div className="pt-2">
                      <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-2.5 mb-1">
                        <div className="bg-[#E50914] h-2.5 rounded-full" style={{ width: `${venue.matchScore}%` }}></div>
                      </div>
                      <p className="text-xs text-right text-[#E50914] font-bold">{venue.matchScore}% Match</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationTool;
