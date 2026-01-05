export type PageView = 'home' | 'tool';

export interface Paper {
  id: string;
  title: string;
  year: number;
  category: string;
  abstract: string;
  imageUrl: string;
  rating?: number;
}

export interface RecommendationRequest {
  title: string;
  abstract: string;
  keywords: string;
}

export interface Venue {
  id: string;
  name: string;
  coverColor: string;
  impactFactor: number;
  indexing: string[];
  openAccess: boolean;
  matchScore: number;
}
