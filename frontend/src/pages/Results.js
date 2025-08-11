import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { transportationAPI } from '../services/api';
import './Results.css';

const Results = () => {
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const location = useLocation();
  const navigate = useNavigate();

  // Get search parameters from navigation state or sessionStorage
  const getSearchParams = () => {
    if (location.state?.origin && location.state?.destination) {
      return {
        origin: location.state.origin,
        destination: location.state.destination
      };
    }
    
    // Fallback to sessionStorage
    const origin = sessionStorage.getItem('searchOrigin');
    const destination = sessionStorage.getItem('searchDestination');
    
    if (origin && destination) {
      return { origin, destination };
    }
    
    return null;
  };

  const fetchRoutes = async (origin, destination) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log(`🔍 Fetching routes: ${origin} → ${destination}`);
      
      // Try POST method first (matches backend structure better)
      const data = await transportationAPI.getRoutesPost(origin, destination);
      
      setRouteData(data);
      console.log('✅ Route data received:', data);
      
    } catch (err) {
      console.error('❌ Failed to fetch routes:', err);
      setError(err.userMessage || 'Failed to find transportation options');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const params = getSearchParams();
    
    if (!params) {
      // No search parameters, redirect to home
      console.log('No search parameters found, redirecting to home');
      navigate('/');
      return;
    }
    
    fetchRoutes(params.origin, params.destination);
  }, [location.state, navigate]);

  const handleNewSearch = () => {
    navigate('/');
  };

  const handleRetry = () => {
    const params = getSearchParams();
    if (params) {
      fetchRoutes(params.origin, params.destination);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="results-page">
        <div className="results-container">
          <div className="loading-section">
            <div className="loading-spinner"></div>
            <h2>🔍 Finding Transportation Options...</h2>
            <p>Comparing routes, prices, and availability across all NYC transportation modes</p>
            <div className="loading-steps">
              <div className="loading-step">📍 Analyzing route options</div>
              <div className="loading-step">🚗 Checking rideshare availability</div>
              <div className="loading-step">🚇 Getting transit schedules</div>
              <div className="loading-step">🚲 Finding nearby bike stations</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="results-page">
        <div className="results-container">
          <div className="error-section">
            <h2>❌ Unable to Find Routes</h2>
            <p>{error}</p>
            <div className="error-actions">
              <button onClick={handleRetry} className="retry-button">
                Try Again
              </button>
              <button onClick={handleNewSearch} className="new-search-button">
                New Search
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Success state with route data
  return (
    <div className="results-page">
      <div className="results-container">
        {/* Search Summary Header */}
        <div className="search-summary">
          <h1>🗺️ Transportation Options</h1>
          <div className="route-info">
            <span className="route-from">📍 {routeData.origin}</span>
            <span className="route-arrow">→</span>
            <span className="route-to">🏁 {routeData.destination}</span>
          </div>
          <button onClick={handleNewSearch} className="new-search-button">
            New Search
          </button>
        </div>

        {/* Available Routes */}
        <div className="routes-section">
          <h2>🛣️ Available Routes</h2>
          <div className="routes-grid">
            {Object.entries(routeData.routes || {}).map(([mode, routeInfo]) => (
              <div key={mode} className="route-card">
                <div className="route-header">
                  <span className="route-icon">
                    {mode === 'driving' && '🚗'}
                    {mode === 'transit' && '🚇'}
                    {mode === 'walking' && '🚶'}
                    {mode === 'bicycling' && '🚲'}
                  </span>
                  <h3>{mode.charAt(0).toUpperCase() + mode.slice(1)}</h3>
                </div>
                <div className="route-details">
                  <div className="route-stat">
                    <span className="stat-label">Duration:</span>
                    <span className="stat-value">{routeInfo.duration}</span>
                  </div>
                  <div className="route-stat">
                    <span className="stat-label">Distance:</span>
                    <span className="stat-value">{routeInfo.distance}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Pricing Information */}
        <div className="pricing-section">
          <h2>💰 Pricing Comparison</h2>
          <div className="pricing-grid">
            {Object.entries(routeData.pricing || {}).map(([category, providers]) => (
              <div key={category} className="pricing-category">
                <h3>{category.charAt(0).toUpperCase() + category.slice(1)}</h3>
                <div className="providers-list">
                  {Object.entries(providers).map(([provider, info]) => (
                    <div key={provider} className="provider-card">
                      <div className="provider-header">
                        <span className="provider-name">{provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
                        <span className={`status-badge status-${info.status}`}>
                          {info.status}
                        </span>
                      </div>
                      <div className="provider-details">
                        {info.price && (
                          <div className="price">
                            ${(info.price / 100).toFixed(2)}
                          </div>
                        )}
                        {info.duration && (
                          <div className="duration">
                            {info.duration} min
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Debug Information (Development only) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="debug-section">
            <h3>🔧 Debug Information</h3>
            <pre>{JSON.stringify(routeData, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default Results;