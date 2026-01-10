import axios from 'axios';
import { RecommendationRequest, Venue } from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface BackendRecommendation {
  conference_name: string;
  venue_id: number;
  match_score: number;
}

interface RecommendationResponse {
  success: boolean;
  message: string;
  total_results: number;
  recommendations: BackendRecommendation[];
  query_info: any;
}

// Deterministic helpers for placeholder data
const COLORS = ['#FFD700', '#4B0082', '#DC143C', '#228B22', '#1E90FF'];
const INDEXES = ['SCIE', 'SCOPUS', 'EI'];

const getDeterministicColor = (id: number) => COLORS[id % COLORS.length];
const getDeterministicImpactFactor = (id: number) => ((id % 50) / 10 + 0.5); // 0.5 to 5.4
const getDeterministicOpenAccess = (id: number) => id % 2 === 0;

export const fetchRecommendations = async (request: RecommendationRequest): Promise<Venue[]> => {
  try {
    const response = await axios.post<RecommendationResponse>(`${API_URL}/api/v1/recommend/`, {
      title: request.title,
      abstract: request.abstract,
      keyword: request.keywords ? request.keywords.split(';') : []
    });

    if (!response.data.success) {
      throw new Error(response.data.message);
    }

    // Map backend response to frontend Venue type with placeholders for missing data
    return response.data.recommendations.map((rec) => ({
      id: rec.venue_id.toString(),
      name: rec.conference_name,
      coverColor: getDeterministicColor(rec.venue_id),
      impactFactor: getDeterministicImpactFactor(rec.venue_id),
      indexing: INDEXES, // Placeholder
      openAccess: getDeterministicOpenAccess(rec.venue_id),
      matchScore: Math.round(rec.match_score * 100) // Convert 0-1 to 0-100
    }));

  } catch (error) {
    console.error("Error fetching recommendations:", error);
    throw error;
  }
};
