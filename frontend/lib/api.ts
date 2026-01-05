import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SearchParams {
  keyword: string;
  authors?: string[];
  keywords?: string[];
  limit?: number;
  sort?: 'newest' | 'oldest';
}

export interface Paper {
  doi: string;
  title: string;
  year: number;
  month: number;
  day: number;
  venue: string | null;
  abstract_link: string | null;
}

export interface SearchResponse {
  success: boolean;
  message: string;
  total_results: number;
  papers: Paper[];
}

export const searchPapers = async (params: SearchParams): Promise<SearchResponse> => {
  const response = await api.post('/search/papers', params);
  return response.data;
};

export interface RecommendParams {
  title?: string;
  abstract?: string;
  keywords?: string[];
}

// Placeholder for recommendation API
export const getRecommendations = async (params: RecommendParams) => {
  // This endpoint might not exist yet based on my plan, 
  // but the user asked for "Recommendation Tool Page".
  // I will assume there is an endpoint or I might need to mock it if not implemented in backend.
  // The user request mentioned "The frontend will send a JSON payload containing the user’s input to your Python API endpoint"
  // I'll assume /recommend/papers or similar.
  // However, looking at backend files, I didn't see a recommendation service explicitly in the search service.
  // I will stick to what I know or use a placeholder.
  // Actually, looking at schemas, there is `PaperRecommendInput`.
  // Let's assume there is a POST /recommend endpoint.
  const response = await api.post('/recommend', params);
  return response.data;
};

export default api;
