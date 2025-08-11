import React, { useState } from 'react';
import './SearchForm.css';

const SearchForm = ({ onSearch, loading }) => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Basic validation
    if (!origin.trim() || !destination.trim()) {
      setError('Please enter both origin and destination');
      return;
    }

    if (origin.trim() === destination.trim()) {
      setError('Origin and destination must be different');
      return;
    }

    // Call the parent component's search function
    try {
      await onSearch(origin.trim(), destination.trim());
    } catch (err) {
      setError('Failed to search routes. Please try again.');
    }
  };

  const handleSwapLocations = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  return (
    <div className="search-form-container">
      <div className="search-form-header">
        <h1>🚇 NYC Transportation Optimizer</h1>
        <p>Find the fastest, cheapest way to get around NYC</p>
      </div>

      <form onSubmit={handleSubmit} className="search-form">
        <div className="input-group">
          <div className="input-field">
            <label htmlFor="origin">From</label>
            <input
              type="text"
              id="origin"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              placeholder="Enter starting location (e.g., Times Square)"
              disabled={loading}
            />
          </div>

          <button
            type="button"
            className="swap-button"
            onClick={handleSwapLocations}
            disabled={loading}
            title="Swap locations"
          >
            ⇅
          </button>

          <div className="input-field">
            <label htmlFor="destination">To</label>
            <input
              type="text"
              id="destination"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder="Enter destination (e.g., Brooklyn Bridge)"
              disabled={loading}
            />
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          type="submit"
          className="search-button"
          disabled={loading || !origin.trim() || !destination.trim()}
        >
          {loading ? 'Searching Routes...' : 'Find Routes'}
        </button>
      </form>

      <div className="search-tips">
        <h3>💡 Search Tips:</h3>
        <ul>
          <li>Use specific addresses or landmarks (e.g., "Central Park", "JFK Airport")</li>
          <li>Include neighborhood names for better results</li>
          <li>Try both street addresses and popular locations</li>
        </ul>
      </div>
    </div>
  );
};

export default SearchForm;