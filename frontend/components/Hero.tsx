'use client';
import React, { useState, useEffect } from 'react';
import { ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react';
import { HERO_PAPERS } from '../constants';
import Link from 'next/link';

export const Hero = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % HERO_PAPERS.length);
    }, 5000); // 5 seconds for better readability
    return () => clearInterval(interval);
  }, []);

  const paper = HERO_PAPERS[currentIndex];

  const nextSlide = () => setCurrentIndex((prev) => (prev + 1) % HERO_PAPERS.length);
  const prevSlide = () => setCurrentIndex((prev) => (prev - 1 + HERO_PAPERS.length) % HERO_PAPERS.length);

  return (
    <div className="relative w-full h-[500px] md:h-[600px] overflow-hidden bg-[#F5F2EB] dark:bg-slate-900 transition-colors duration-300">

      {/* Background Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-[#FDFBF7] via-[#FDFBF7]/80 to-transparent dark:from-slate-950 dark:via-slate-950/80 dark:to-transparent z-10 w-full md:w-2/3" />

      {/* Content Container */}
      <div className="relative z-20 max-w-7xl mx-auto h-full px-4 sm:px-6 lg:px-8 flex items-center">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">

          {/* Text Content */}
          <div className="flex flex-col justify-center space-y-6 animate-fade-in">
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 text-xs font-bold uppercase tracking-wider text-white bg-[#E50914] rounded-sm">
                Featured Paper
              </span>
              <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
                {paper.year} • {paper.category}
              </span>
            </div>

            <h2 className="text-4xl md:text-5xl lg:text-6xl font-black text-slate-900 dark:text-white leading-tight line-clamp-3">
              {paper.title.toUpperCase()}
            </h2>

            <p className="text-lg text-slate-600 dark:text-slate-300 line-clamp-3 max-w-xl">
              {paper.abstract}
            </p>

            <div className="pt-4">
              <Link
                href="/recommendations"
                className="group inline-flex items-center space-x-2 bg-[#E50914] text-white px-8 py-3 rounded-md font-bold text-lg hover:bg-red-700 transition-all shadow-lg hover:shadow-red-500/30"
              >
                <span>Explore Paper</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>

          {/* Image Content - Absolute on Mobile, Relative on Desktop */}
          <div className="absolute md:relative inset-y-0 right-0 w-2/3 md:w-full h-full -z-10 md:z-auto opacity-40 md:opacity-100">
            <div className="h-full w-full flex items-center justify-end p-8">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={paper.imageUrl}
                alt={paper.title}
                className="rounded-xl shadow-2xl object-cover h-3/4 w-full md:w-4/5 transform rotate-3 hover:rotate-0 transition-transform duration-700 ease-out"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Controls */}
      <div className="absolute bottom-8 left-8 md:left-auto md:right-8 z-30 flex space-x-4">
        <button onClick={prevSlide} className="p-3 rounded-full border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors">
          <ChevronLeft className="w-6 h-6" />
        </button>
        <button onClick={nextSlide} className="p-3 rounded-full border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors">
          <ChevronRight className="w-6 h-6" />
        </button>
        <div className="flex items-center space-x-2 text-sm font-mono text-slate-500 ml-4">
          <span>{currentIndex + 1 < 10 ? `0${currentIndex + 1}` : currentIndex + 1}</span>
          <span className="w-8 h-px bg-slate-400"></span>
          <span>{HERO_PAPERS.length < 10 ? `0${HERO_PAPERS.length}` : HERO_PAPERS.length}</span>
        </div>
      </div>

    </div>
  );
};

export default Hero;
