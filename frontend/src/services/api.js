import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance with enhanced configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout for transportation APIs
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    if (config.data) {
      console.log('📤 Request Data:', config.data);
    }
    if (config.params) {
      console.log('📤 Request Params:', config.params);
    }
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', {
      method: error.config?.method?.toUpperCase(),
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.error || error.message
    });
    
    // Transform error for consistent handling
    const transformedError = {
      message: error.response?.data?.error || error.message || 'Network error occurred',
      status: error.response?.status || 0,
      code: error.code || 'UNKNOWN_ERROR',
      userMessage: formatErrorMessage(error)
    };
    
    return Promise.reject(transformedError);
  }
);

// Utility function to format errors for users
function formatErrorMessage(error) {
  switch (error.response?.status) {
    case 400:
      return 'Please check your input and try again.';
    case 404:
      return 'Location not found. Please try a more specific address.';
    case 429:
      return 'Too many requests. Please wait a moment and try again.';
    case 500:
      return 'Transportation services are temporarily unavailable.';
    case 0:
      return 'Unable to connect to transportation services.';
    default:
      return error.response?.data?.error || error.message || 'Something went wrong. Please try again.';
  }
}

export const transportationAPI = {
  // Get routes for origin and destination
  getRoutes: async (origin, destination) => {
    try {
      const response = await api.get('/routes', {
        params: { 
          origin: origin.trim(), 
          destination: destination.trim() 
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching routes:', error);
      throw {
        ...error,
        context: 'route_comparison',
        userMessage: error.userMessage || 'Unable to find routes between these locations. Please check your addresses and try again.'
      };
    }
  },

  // Alternative POST method for routes (matches backend)
  getRoutesPost: async (origin, destination) => {
    try {
      const response = await api.post('/routes', {
        origin: origin.trim(),
        destination: destination.trim()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching routes via POST:', error);
      throw {
        ...error,
        context: 'route_comparison_post',
        userMessage: error.userMessage || 'Unable to find routes between these locations. Please check your addresses and try again.'
      };
    }
  },

  // Geocode an address
  geocodeAddress: async (address) => {
    try {
      const response = await api.get('/geocode', {
        params: { address: address.trim() }
      });
      return response.data;
    } catch (error) {
      console.error('Error geocoding address:', error);
      throw {
        ...error,
        context: 'geocoding',
        userMessage: error.userMessage || 'Unable to find this location. Please try a more specific address.'
      };
    }
  },

  // Health check (adjusted URL for backend)
  healthCheck: async () => {
    try {
      // Health endpoint is at root level, not under /api/v1
      const healthURL = API_BASE_URL.replace('/api/v1', '') + '/health';
      const response = await axios.get(healthURL);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw {
        ...error,
        context: 'health_check',
        userMessage: 'Unable to connect to transportation services.'
      };
    }
  },

  // Test API connection
  testConnection: async () => {
    try {
      const response = await api.get('/test');
      return response.data;
    } catch (error) {
      console.error('Connection test failed:', error);
      throw {
        ...error,
        context: 'connection_test',
        userMessage: 'Connection to backend services failed.'
      };
    }
  },

  // Get detailed public transit routes
  getTransitRoutes: async (origin, destination, departureTime = 'now') => {
    try {
      const response = await api.get('/transit', {
        params: {
          origin: origin.trim(),
          destination: destination.trim(),
          departure_time: departureTime
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching transit routes:', error);
      throw {
        ...error,
        context: 'transit_routes',
        userMessage: error.userMessage || 'Unable to find public transit routes. Please try again.'
      };
    }
  },

  // Get simplified transit summary for quick comparison
  getTransitSummary: async (origin, destination) => {
    try {
      const response = await api.get('/transit/summary', {
        params: {
          origin: origin.trim(),
          destination: destination.trim()
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching transit summary:', error);
      throw {
        ...error,
        context: 'transit_summary',
        userMessage: error.userMessage || 'Unable to get transit information. Please try again.'
      };
    }
  }
};

// Input validation utilities
export const apiUtils = {
  // Validate search inputs
  validateSearchInputs: (origin, destination) => {
    const errors = [];
    
    if (!origin?.trim()) {
      errors.push('Starting location is required');
    }
    
    if (!destination?.trim()) {
      errors.push('Destination is required');
    }
    
    if (origin?.trim() === destination?.trim()) {
      errors.push('Starting location and destination must be different');
    }
    
    if (origin?.trim().length < 3) {
      errors.push('Starting location should be more specific');
    }
    
    if (destination?.trim().length < 3) {
      errors.push('Destination should be more specific');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  },

  // Check if location appears to be in NYC
  isLikelyNYCLocation: (location) => {
    const nycKeywords = [
      'nyc', 'new york', 'manhattan', 'brooklyn', 'queens', 'bronx', 'staten island',
      'central park', 'times square', 'wall street', 'broadway', 'harlem',
      'williamsburg', 'soho', 'tribeca', 'chelsea', 'midtown', 'downtown'
    ];
    
    const locationLower = location.toLowerCase();
    return nycKeywords.some(keyword => locationLower.includes(keyword));
  }
};

export default api;