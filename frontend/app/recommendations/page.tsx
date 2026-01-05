'use client';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import RecommendationTool from '../../components/RecommendationTool';

export default function RecommendationsPage() {
  return (
    <main className="min-h-screen flex flex-col bg-[#FDFBF7] dark:bg-slate-950">
      <Navbar />
      <div className="flex-1">
        <RecommendationTool />
      </div>
      <Footer />
    </main>
  );
}
