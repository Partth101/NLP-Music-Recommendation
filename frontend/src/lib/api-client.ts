/**
 * API Client for MoodTune AI Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface EmotionAnalysisRequest {
  text: string;
  include_explanation?: boolean;
  threshold?: number;
}

export interface EmotionAnalysisResponse {
  id?: string;
  emotions: Record<string, number>;
  primary_emotion: string;
  primary_confidence: number;
  secondary_emotions: string[];
  detected_emotions: string[];
  confidence_level: "high" | "medium" | "low";
  emotional_complexity: number;
  explanation?: string;
  word_importance?: Record<string, number>;
  processing_time_ms?: number;
}

export interface Song {
  id: string;
  spotify_track_id: string;
  name: string;
  artists: string;
  emotion_scores: Record<string, number>;
  emotions?: string[];
  times_played: number;
  average_rating?: number;
}

export interface RecommendationResponse {
  id: string;
  song: Song;
  match_score: number;
  matched_emotions: string[];
  explanation?: string;
  why_this_song?: string[];
  emotion_analysis?: EmotionAnalysisResponse;
  created_at: string;
}

export interface UserCredentials {
  email: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

class ApiClient {
  private baseUrl: string;
  private accessToken: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    if (typeof window !== "undefined") {
      this.accessToken = localStorage.getItem("access_token");
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (this.accessToken) {
      (headers as Record<string, string>)["Authorization"] =
        `Bearer ${this.accessToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async register(
    email: string,
    password: string,
    displayName?: string
  ): Promise<any> {
    return this.request("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name: displayName }),
    });
  }

  async login(email: string, password: string): Promise<AuthToken> {
    const token = await this.request<AuthToken>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    this.setToken(token.access_token);
    if (typeof window !== "undefined") {
      localStorage.setItem("refresh_token", token.refresh_token);
    }

    return token;
  }

  async logout(): Promise<void> {
    this.accessToken = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  }

  async getMe(): Promise<any> {
    return this.request("/api/v1/auth/me");
  }

  setToken(token: string | null) {
    this.accessToken = token;
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("access_token", token);
      } else {
        localStorage.removeItem("access_token");
      }
    }
  }

  // Emotions
  async analyzeEmotions(
    request: EmotionAnalysisRequest
  ): Promise<EmotionAnalysisResponse> {
    return this.request("/api/v1/emotions/analyze", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getSupportedEmotions(): Promise<{
    emotions: string[];
    total: number;
    description: string;
  }> {
    return this.request("/api/v1/emotions/supported");
  }

  // Recommendations
  async getRecommendation(text: string): Promise<RecommendationResponse> {
    return this.request("/api/v1/recommendations", {
      method: "POST",
      body: JSON.stringify({
        text,
        include_explanation: true,
        save_to_history: true,
      }),
    });
  }

  async submitFeedback(
    recommendationId: string,
    rating: number,
    feedbackText?: string
  ): Promise<void> {
    return this.request(`/api/v1/recommendations/${recommendationId}/feedback`, {
      method: "POST",
      body: JSON.stringify({
        rating,
        feedback_text: feedbackText,
        was_played: true,
      }),
    });
  }

  async getHistory(
    page: number = 1,
    perPage: number = 10
  ): Promise<{
    recommendations: any[];
    total: number;
    page: number;
    per_page: number;
  }> {
    return this.request(
      `/api/v1/recommendations/history?page=${page}&per_page=${perPage}`
    );
  }

  // Insights
  async getMoodPatterns(days: number = 30): Promise<any> {
    return this.request(`/api/v1/insights/mood-patterns?days=${days}`);
  }

  async getMusicTasteProfile(): Promise<any> {
    return this.request("/api/v1/insights/music-taste");
  }

  // Songs
  async getRandomSong(): Promise<Song> {
    return this.request("/api/v1/songs/random");
  }

  async getSongStats(): Promise<any> {
    return this.request("/api/v1/songs/stats");
  }

  // History Stats
  async getHistoryStats(days: number = 30): Promise<any> {
    return this.request(`/api/v1/history/stats?days=${days}`);
  }
}

export const apiClient = new ApiClient();
export default apiClient;
