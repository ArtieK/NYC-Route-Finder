import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const transportationAPI = {
  // Get routes for origin and destination
  getRoutes: async (origin, destination) => {
    try {
      const response = await api.get('/routes', {
        params: { origin, destination }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching routes:', error);
      throw error;
    }
  },

  // Geocode an address
  geocodeAddress: async (address) => {
    try {
      const response = await api.get('/geocode', {
        params: { address }
      });
      return response.data;
    } catch (error) {
      console.error('Error geocoding address:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};

export default api;