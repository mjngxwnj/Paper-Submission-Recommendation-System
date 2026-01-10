import { RecommendationRequest, Venue, SearchResult } from '../types';

export const fetchRecommendations = async (request: RecommendationRequest): Promise<Venue[]> => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1500));

  return [
    {
      id: 'v1',
      name: 'Journal of Artificial Intelligence Research',
      coverColor: '#E50914',
      impactFactor: 5.2,
      indexing: ['SCIE', 'Scopus'],
      openAccess: true,
      matchScore: 98
    },
    {
      id: 'v2',
      name: 'IEEE Transactions on Pattern Analysis',
      coverColor: '#0F172A',
      impactFactor: 14.5,
      indexing: ['SCIE', 'IEEE'],
      openAccess: false,
      matchScore: 92
    },
    {
      id: 'v3',
      name: 'Neurocomputing',
      coverColor: '#F59E0B', // Amber
      impactFactor: 6.0,
      indexing: ['SCIE', 'Scopus'],
      openAccess: true,
      matchScore: 88
    },
    {
      id: 'v4',
      name: 'Applied Soft Computing',
      coverColor: '#10B981', // Emerald
      impactFactor: 8.7,
      indexing: ['SCIE'],
      openAccess: false,
      matchScore: 85
    }
  ];
};

export const searchGlobal = async (query: string): Promise<SearchResult[]> => {
  // Simulate network delay (faster than full recommendation)
  await new Promise(resolve => setTimeout(resolve, 300));

  if (!query || query.trim().length === 0) {
    return [];
  }

  const lowerQuery = query.toLowerCase();

  // Mock Data
  const mockResults: SearchResult[] = [
    {
      id: 'j1',
      type: 'venue',
      title: 'Knowledge-based Systems',
      subtitle: 'Journal • IF: 5.01',
    },
    {
      id: 'j2',
      type: 'venue',
      title: 'Neural Computing and Applications',
      subtitle: 'Journal • IF: 4.66',
    },
    {
      id: 'j3',
      type: 'venue',
      title: 'Neural Processing Letters',
      subtitle: 'Journal • IF: 2.64',
    },
    {
      id: 'j4',
      type: 'venue',
      title: 'Knowledge and Information Systems',
      subtitle: 'Journal • IF: 2.55',
    },
    {
      id: 'p1',
      type: 'paper',
      title: 'Optimizing Neural Networks with Gradient Descent',
      subtitle: 'Paper • 2024',
    },
    {
      id: 'p2',
      type: 'paper',
      title: 'A Survey on Graph Neural Networks',
      subtitle: 'Paper • 2024',
    },
    {
      id: 'p3',
      type: 'paper',
      title: 'Blockchain in Supply Chain Management',
      subtitle: 'Paper • 2024',
    },
    {
      id: 'p4',
      type: 'paper',
      title: 'Edge Computing Frameworks',
      subtitle: 'Paper • 2024',
    }
  ];

  return mockResults.filter(item =>
    item.title.toLowerCase().includes(lowerQuery) ||
    (item.subtitle && item.subtitle.toLowerCase().includes(lowerQuery))
  );
};
