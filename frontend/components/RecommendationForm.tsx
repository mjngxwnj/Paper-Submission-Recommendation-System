'use client';
import { useState } from 'react';
import { Search, X } from 'lucide-react';
import { getRecommendations, Paper } from '../lib/api';

const MOCK_RESULTS: Paper[] = [
  {
    doi: '10.1016/j.knosys.2023.111111',
    title: 'Knowledge-based Systems',
    year: 2025,
    month: 1,
    day: 1,
    venue: 'SCIE, ISI',
    abstract_link: '#'
  },
  {
    doi: '10.1007/s00521-023-08888-8',
    title: 'Neural Computing and Applications',
    year: 2025,
    month: 2,
    day: 1,
    venue: 'SCIE, ISI',
    abstract_link: '#'
  },
  {
    doi: '10.1007/s10489-023-04444-4',
    title: 'Applied Intelligence',
    year: 2025,
    month: 3,
    day: 1,
    venue: 'SCIE, ISI',
    abstract_link: '#'
  },
  {
    doi: '10.1007/s10994-023-06666-6',
    title: 'Machine Learning',
    year: 2025,
    month: 4,
    day: 1,
    venue: 'SCIE, ISI',
    abstract_link: '#'
  }
];

export default function RecommendationForm() {
  const [title, setTitle] = useState('');
  const [abstract, setAbstract] = useState('');
  const [keywords, setKeywords] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Paper[]>([]); // Start with empty, or use MOCK for demo
  const [showResults, setShowResults] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      // const data = await getRecommendations({ title, abstract, keywords: keywords.split(';') });
      // setResults(data.papers || []);

      // Using MOCK results for now to match visual requirements as backend might not have data populated
      setTimeout(() => {
        setResults(MOCK_RESULTS);
        setShowResults(true);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error("Failed to fetch recommendations", error);
      setLoading(false);
    }
  };

  const clearAll = () => {
    setTitle('');
    setAbstract('');
    setKeywords('');
    setShowResults(false);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Input Form */}
      <div className="bg-white dark:bg-neutral-900 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-800 overflow-hidden">
        <div className="p-4 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between">
          <div className="flex items-center gap-2 text-lg font-semibold text-neutral-800 dark:text-neutral-200">
            <Search className="w-5 h-5" />
            <h2>Find the right journals for your submissions</h2>
          </div>
          <button onClick={clearAll} className="text-sm text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300">
            Clear All
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Title Input */}
          <div className="grid grid-cols-12 gap-4">
            <label className="col-span-2 text-sm font-medium text-neutral-600 dark:text-neutral-400 pt-2">Title</label>
            <div className="col-span-10 relative">
              <textarea
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full resize-none bg-transparent border-b border-neutral-200 dark:border-neutral-800 focus:border-blue-500 focus:outline-none py-2 text-neutral-800 dark:text-neutral-200"
                placeholder="Enter paper title..."
                rows={1}
              />
              {title && <button onClick={() => setTitle('')} className="absolute right-0 top-2 text-neutral-300 hover:text-neutral-500"><X className="w-4 h-4" /></button>}
            </div>
          </div>

          {/* Abstract Input */}
          <div className="grid grid-cols-12 gap-4">
            <label className="col-span-2 text-sm font-medium text-neutral-600 dark:text-neutral-400 pt-2">Abstract</label>
            <div className="col-span-10 relative">
              <textarea
                value={abstract}
                onChange={(e) => setAbstract(e.target.value)}
                className="w-full resize-none bg-transparent border-b border-neutral-200 dark:border-neutral-800 focus:border-blue-500 focus:outline-none py-2 text-neutral-800 dark:text-neutral-200 min-h-[100px]"
                placeholder="Enter paper abstract..."
              />
              {abstract && <button onClick={() => setAbstract('')} className="absolute right-0 top-2 text-neutral-300 hover:text-neutral-500"><X className="w-4 h-4" /></button>}
            </div>
          </div>

          {/* Keyword Input */}
          <div className="grid grid-cols-12 gap-4">
            <label className="col-span-2 text-sm font-medium text-neutral-600 dark:text-neutral-400 pt-2">Keyword</label>
            <div className="col-span-10 relative">
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                className="w-full bg-transparent border-b border-dashed border-neutral-200 dark:border-neutral-800 focus:border-blue-500 focus:outline-none py-2 text-neutral-800 dark:text-neutral-200"
                placeholder="Enter keywords separated by semicolon..."
              />
              {keywords && <button onClick={() => setKeywords('')} className="absolute right-0 top-2 text-neutral-300 hover:text-neutral-500"><X className="w-4 h-4" /></button>}
            </div>
          </div>
        </div>

        <div className="p-4 bg-neutral-50 dark:bg-neutral-950 flex justify-end gap-3">
          <button
            onClick={clearAll}
            className="px-6 py-2 text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            onClick={handleSearch}
            disabled={loading}
            className="bg-red-600 hover:bg-red-700 text-white px-8 py-2 rounded font-medium transition-colors disabled:opacity-50 shadow-lg shadow-red-600/20"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {showResults && (
        <div className="space-y-6">
          <h3 className="text-xl font-bold text-neutral-800 dark:text-neutral-200">
            Here is the list of the most relevant journals for your submission:
          </h3>
          <p className="text-neutral-500 text-sm">{results.length} results</p>

          <div className="grid md:grid-cols-4 gap-6">
            {results.map((paper, idx) => (
              <div key={idx} className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm overflow-hidden flex flex-col h-full border border-neutral-200 dark:border-neutral-700">
                {/* Header Card Color */}
                <div className={`h-24 p-4 flex flex-col justify-between ${idx % 4 === 0 ? 'bg-gradient-to-br from-yellow-100 to-yellow-400 text-yellow-900' :
                  idx % 4 === 1 ? 'bg-gradient-to-br from-indigo-100 to-indigo-400 text-indigo-900' :
                    idx % 4 === 2 ? 'bg-gradient-to-br from-purple-100 to-purple-800 text-white' :
                      'bg-gradient-to-br from-yellow-400 to-white text-yellow-900'
                  }`}>
                  <h4 className="font-bold leading-tight line-clamp-2">{paper.title}</h4>
                  {/* Placeholder Icon */}
                  <div className="w-10 h-10 bg-white/30 rounded backdrop-blur-sm self-start mt-2"></div>
                </div>

                <div className="p-4 flex-1 space-y-4 text-sm">
                  <div className="flex justify-between items-center py-1 border-b border-dashed border-neutral-200 dark:border-neutral-700">
                    <span className="font-semibold text-neutral-700 dark:text-neutral-300">Impact Factor</span>
                    <span className="text-neutral-500">{(Math.random() * 5).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-dashed border-neutral-200 dark:border-neutral-700">
                    <span className="font-semibold text-neutral-700 dark:text-neutral-300">Index</span>
                    <span className="text-neutral-500">{paper.venue}</span>
                  </div>
                  <div className="flex justify-between items-center py-1">
                    <span className="font-semibold text-neutral-700 dark:text-neutral-300">Open Access</span>
                    <span className="text-neutral-500">{idx % 2 === 0 ? 'Yes' : 'No'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
