'use client';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import NewReleases from '../components/NewRelease';
import Footer from '../components/Footer';

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col">
      <Navbar />
      <Hero />
      <NewReleases />
      <Footer />
    </main>
  );
}


