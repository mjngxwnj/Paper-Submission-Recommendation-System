'use client';
import { Paper } from '../lib/api';
import { Star, ChevronLeft, ChevronRight } from 'lucide-react';

interface PaperGridProps {
  papers: Paper[];
}

export default function PaperGrid({ papers }: PaperGridProps) {
  return (
    <div className="py-12 bg-neutral-950 px-8 text-white relative overflow-hidden">
      {/* Background stars effect could go here */}
      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-20 pointer-events-none"></div>

      <div className="flex items-center justify-between mb-8 max-w-7xl mx-auto">
        <h2 className="text-2xl font-bold uppercase tracking-wider italic">
          New Releases
        </h2>
        <div className="flex gap-2">
          <button className="p-2 rounded-full bg-neutral-800 hover:bg-neutral-700 transition-colors">
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button className="p-2 rounded-full bg-neutral-800 hover:bg-neutral-700 transition-colors">
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 max-w-7xl mx-auto">
        {papers.map((paper, idx) => (
          <div key={idx} className="group relative flex flex-col gap-2">
            {/* Card Image */}
            <div className="aspect-[2/3] w-full overflow-hidden rounded-lg bg-neutral-800 relative">
              <img
                src={`https://picsum.photos/seed/${paper.doi}/300/450`}
                alt={paper.title}
                className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>

            {/* Card Info */}
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-xs text-orange-500 font-bold">
                <Star className="w-3 h-3 fill-current" />
                <span>{(Math.random() * 5 + 5).toFixed(1)}</span>
                <span className="text-neutral-500 font-normal">{paper.year}</span>
              </div>
              <h3 className="text-sm font-bold leading-tight text-white line-clamp-2">
                {paper.title}
              </h3>
              <p className="text-xs text-neutral-500">
                {paper.venue || "Journal"}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
