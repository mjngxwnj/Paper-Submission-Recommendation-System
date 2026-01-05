'use client';
import { Github, Linkedin, Mail, Instagram, ExternalLink } from 'lucide-react';
import Link from 'next/link';

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-white py-16 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">

          {/* Column 1: PRS Info */}
          <div className="space-y-4">
            <h3 className="text-2xl font-black text-white uppercase tracking-tighter">PRS</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Our ultimate goal is to help users discover the most suitable conferences or journals for their research, 
              while also enabling fast and efficient search for academic papers and authors.
            </p>

            <div className="flex flex-col space-y-2 pt-4">
              {/* Member 1*/}
              <div className="flex items-center space-x-4">
                <span className="text-[#E50914] font-bold">Huỳnh Minh Thuận</span>
                <div className="flex space-x-3 text-slate-400">
                  <a href="https://github.com/mjngxwnj" target="_blank" rel="noopener noreferrer">
                    <Github className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a>
                  <a href="https://www.linkedin.com/in/thuan-huynh-nauht429082/" target="_blank" rel="noopener noreferrer">
                    <Linkedin className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a>
                  <a href="huynhminhthuan28092004@gmail.com">
                    <Mail className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a> 
                </div>
              </div>

              {/* Member 2*/}
              <div className="flex items-center space-x-4">
                <span className="text-[#E50914] font-bold">Nguyễn Phạm Anh Trí</span>
                <div className="flex space-x-3 text-slate-400">
                  <a href="https://github.com/laeliaxu" target="_blank" rel="noopener noreferrer">
                    <Github className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a>
                  <a href="https://www.linkedin.com/in/nguyen-pham-anh-tri-634b1630b/" target="_blank" rel="noopener noreferrer">
                    <Linkedin className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a>
                  <a href="nguyenphamanhtri@gmail.com">
                    <Mail className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a> 
                </div>
              </div>

              {/* Member 3*/}
              <div className="flex items-center space-x-4">
                <span className="text-[#E50914] font-bold">Nguyễn Minh Trí</span>
                <div className="flex space-x-3 text-slate-400">
                  <a href="https://github.com/Swuzz123" target="_blank" rel="noopener noreferrer">
                    <Github className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a>
                  <a href="https://www.linkedin.com/in/minh-tr%C3%AD-nguy%E1%BB%85n-16b845327/" target="_blank" rel="noopener noreferrer">
                    <Linkedin className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a>
                  <a href="ngminhtri21102004@gmail.com">
                    <Mail className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a> 
                </div>
              </div>

              {/* Member 4*/}
              <div className="flex items-center space-x-4">
                <span className="text-[#E50914] font-bold">Trương Minh Thuật</span>
                <div className="flex space-x-3 text-slate-400">
                  <a href="https://github.com/MinhThuat" target="_blank" rel="noopener noreferrer">
                    <Github className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a>
                  <a href="" target="_blank" rel="noopener noreferrer">
                    <Linkedin className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a>
                  <a href="thuattruongminh@gmail.com">
                    <Mail className="w-4 h-4 hover:text-white cursor-pointer" />
                  </a> 
                </div>
              </div>
            </div>
          </div>

          {/* Column 2: Recommendation Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white uppercase tracking-wide">Paper Recommendations</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              We are passionate about open-source innovation. Join our growing community of contributors as we build smarter, faster, and 
              more accessible academic paper and venue recommendation technology for the future of research.
            </p>
            <ul className="space-y-2 text-sm text-slate-300">
              <li className="flex items-center space-x-2">
                <span className="text-[#E50914]">♡</span>
                <span>Personalized suggestions</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-[#E50914]">#</span>
                <span>Discover hidden gems</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-[#E50914] text-xs">{'</>'}</span>
                <span>Powered by Advanced Algorithms</span>
              </li>
            </ul>
            <Link
              href="/recommendations"
              className="inline-block mt-4 px-6 py-2 border border-[#E50914] text-[#E50914] hover:bg-[#E50914] hover:text-white transition-colors rounded text-sm font-medium"
            >
              Try Recommendations
            </Link>
          </div>

          {/* Column 3: Github Org */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white uppercase tracking-wide">Our Github Organization</h3>
            <div className="flex items-start space-x-3">
              <div className="text-[#E50914] font-black text-xl">PRS</div>
              <div>
                <p className="font-bold text-white">Team Workspace</p>
                <p className="text-xs text-slate-400">Open Source Team Projects</p>
              </div>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">
              We're passionate about open source development. Join our community of developers building the future of academic technology.
            </p>
            <a href="https://github.com/mjngxwnj/Paper-Submission-Recommendation-System" className="inline-flex items-center text-[#E50914] hover:text-red-400 text-sm font-medium">
              Visit our GitHub <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </div>

        </div>

        <div className="mt-16 pt-8 border-t border-slate-800 flex flex-col md:flex-row justify-between items-center">
          <p className="text-slate-500 text-sm">© 2026 PRS. All rights reserved.</p>
          <div className="flex space-x-6 text-slate-500 text-sm mt-4 md:mt-0">
            <a href="#" className="hover:text-white">Terms</a>
            <a href="#" className="hover:text-white">Privacy</a>
            <a href="#" className="hover:text-white">Cookies</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
