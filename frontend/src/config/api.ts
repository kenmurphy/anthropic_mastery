// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:10000';

export const apiConfig = {
  baseUrl: API_BASE_URL,
  endpoints: {
    conversations: `${API_BASE_URL}/api/conversations`,
    health: `${API_BASE_URL}/health`,
  }
};

// Helper function to build API URLs
export const buildApiUrl = (path: string): string => {
  return `${API_BASE_URL}${path}`;
};
