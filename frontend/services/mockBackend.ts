import { RecommendationRequest, Venue } from '../types';

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
