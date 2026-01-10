'use client';
import React, { useRef } from 'react';
import { ChevronLeft, ChevronRight, Star } from 'lucide-react';
import { NEW_RELEASES } from '../constants';

export const NewReleases = () => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const scrollAmount = 300;
      scrollContainerRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  return (
    <section className="py-12 bg-[#FDFBF7] dark:bg-slate-950 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-black uppercase italic tracking-tighter text-slate-900 dark:text-white">
            New Releases
          </h2>
          <div className="flex space-x-2">
            <button 
              onClick={() => scroll('left')} 
              className="p-2 rounded-full bg-slate-200 dark:bg-black hover:bg-[#E50914] hover:text-white transition-colors">
              <ChevronLeft className="w-5 h-5 text-slate-900 dark:text-white" />
            </button>

            <button 
              onClick={() => scroll('right')} 
              className="p-2 rounded-full bg-slate-200 dark:bg-black hover:bg-[#E50914] hover:text-white transition-colors">
              <ChevronRight className="w-5 h-5 text-slate-900 dark:text-white" />
            </button>
          </div>
        </div>

        {/* Horizontal Scroll Container */}
        <div
          ref={scrollContainerRef}
          className="flex overflow-x-auto gap-6 pb-8 no-scrollbar snap-x"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          <style jsx>{`
                        .no-scrollbar::-webkit-scrollbar {
                            display: none;
                        }
                    `}</style>
          {NEW_RELEASES.map((paper) => (
            <div
              key={paper.id}
              className="flex-none w-[200px] sm:w-[220px] snap-start group cursor-pointer"
            >
              <div className="relative aspect-[2/3] overflow-hidden rounded-md mb-3 shadow-lg">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={paper.imageUrl}
                  alt={paper.title}
                  className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />

                {/* Hover Play/View Icon */}
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="w-12 h-12 rounded-full bg-[#E50914] flex items-center justify-center text-white shadow-xl">
                    <ChevronRight className="w-6 h-6 ml-0.5" />
                  </div>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex items-center space-x-1 text-amber-500 text-xs font-bold">
                  <Star className="w-3 h-3 fill-current" />
                  <span>{paper.rating}</span>
                  <span className="text-slate-400 dark:text-slate-500 font-normal ml-2">{paper.year}</span>
                </div>
                <h3 className="font-bold text-slate-900 dark:text-white leading-tight group-hover:text-[#E50914] transition-colors line-clamp-2">
                  {paper.title}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1">
                  {paper.category}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default NewReleases;
