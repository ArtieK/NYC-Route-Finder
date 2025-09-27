import React from 'react';
import './TransitResults.css';

/**
 * Component to display public transit route options.
 * Shows subway, bus, and rail routes with fares, transfers, and timing.
 */
const TransitResults = ({ transitData }) => {
  if (!transitData) {
    return null;
  }

  const { status, routes, provider } = transitData;

  // Handle unavailable transit
  if (status === 'unavailable') {
    return (
      <div className="transit-results unavailable">
        <div className="transit-header">
          <h3>🚇 Public Transit</h3>
          <span className="provider">{provider}</span>
        </div>
        <p className="unavailable-message">
          No public transit routes available for this trip
        </p>
      </div>
    );
  }

  // Handle error state
  if (status === 'error') {
    return (
      <div className="transit-results error">
        <div className="transit-header">
          <h3>🚇 Public Transit</h3>
          <span className="provider">{provider}</span>
        </div>
        <p className="error-message">
          Unable to fetch transit routes. Please try again.
        </p>
      </div>
    );
  }

  return (
    <div className="transit-results">
      <div className="transit-header">
        <h3>🚇 Public Transit Options</h3>
        <span className="provider">{provider}</span>
      </div>

      <div className="routes-container">
        {routes && routes.length > 0 ? (
          routes.map((route) => (
            <TransitRoute key={route.route_id} route={route} />
          ))
        ) : (
          <p className="no-routes">No routes available</p>
        )}
      </div>
    </div>
  );
};

/**
 * Individual transit route display component.
 */
const TransitRoute = ({ route }) => {
  const {
    route_id,
    summary,
    duration,
    distance,
    pricing,
    transit_lines,
    transfers,
    walking_distance,
    departure_time,
    arrival_time,
    steps,
  } = route;

  return (
    <div className="transit-route">
      {/* Route Header */}
      <div className="route-header">
        <div className="route-title">
          <span className="route-number">Route {route_id + 1}</span>
          <h4>{summary}</h4>
        </div>
        <div className="route-fare">
          ${pricing.total_fare.toFixed(2)}
        </div>
      </div>

      {/* Route Summary Stats */}
      <div className="route-stats">
        <div className="stat">
          <span className="stat-icon">⏱️</span>
          <span className="stat-value">{duration}</span>
        </div>
        <div className="stat">
          <span className="stat-icon">📍</span>
          <span className="stat-value">{distance}</span>
        </div>
        <div className="stat">
          <span className="stat-icon">🔄</span>
          <span className="stat-value">
            {transfers === 0 ? 'Direct' : `${transfers} transfer${transfers > 1 ? 's' : ''}`}
          </span>
        </div>
        <div className="stat">
          <span className="stat-icon">🚶</span>
          <span className="stat-value">{walking_distance}</span>
        </div>
      </div>

      {/* Transit Lines */}
      {transit_lines && transit_lines.length > 0 && (
        <div className="transit-lines">
          <span className="lines-label">Lines:</span>
          {transit_lines.map((line, idx) => (
            <span key={idx} className="transit-line-badge">
              {line}
            </span>
          ))}
        </div>
      )}

      {/* Timing */}
      <div className="route-timing">
        <span className="timing-item">
          <strong>Depart:</strong> {departure_time}
        </span>
        <span className="timing-separator">→</span>
        <span className="timing-item">
          <strong>Arrive:</strong> {arrival_time}
        </span>
      </div>

      {/* Fare Details */}
      <div className="fare-details">
        <span className="fare-type">{pricing.fare_type}</span>
        <span className="fare-note">{pricing.note}</span>
      </div>

      {/* Detailed Steps (collapsible) */}
      {steps && steps.length > 0 && (
        <details className="route-steps">
          <summary>View detailed directions ({steps.length} steps)</summary>
          <div className="steps-list">
            {steps.map((step, idx) => (
              <TransitStep key={idx} step={step} stepNumber={idx + 1} />
            ))}
          </div>
        </details>
      )}
    </div>
  );
};

/**
 * Individual transit step component.
 */
const TransitStep = ({ step, stepNumber }) => {
  const { mode, duration, distance, instructions, transit } = step;

  // Get icon based on mode
  const getModeIcon = (mode) => {
    switch (mode) {
      case 'transit':
        return '🚇';
      case 'walking':
        return '🚶';
      default:
        return '📍';
    }
  };

  return (
    <div className={`transit-step mode-${mode}`}>
      <div className="step-number">{stepNumber}</div>
      <div className="step-content">
        <div className="step-header">
          <span className="step-icon">{getModeIcon(mode)}</span>
          <span className="step-mode">{mode === 'transit' ? 'Transit' : 'Walk'}</span>
          <span className="step-duration">{duration}</span>
          <span className="step-distance">({distance})</span>
        </div>

        {/* Transit-specific details */}
        {mode === 'transit' && transit && (
          <div className="transit-details">
            <div className="transit-line">
              <strong>{transit.line_short_name || transit.line_name}</strong>
              {transit.headsign && <span className="headsign"> to {transit.headsign}</span>}
            </div>
            <div className="transit-stops">
              <div className="stop departure">
                <span className="stop-label">From:</span>
                <span className="stop-name">{transit.departure_stop}</span>
              </div>
              <div className="stop-info">
                {transit.num_stops} stop{transit.num_stops !== 1 ? 's' : ''}
              </div>
              <div className="stop arrival">
                <span className="stop-label">To:</span>
                <span className="stop-name">{transit.arrival_stop}</span>
              </div>
            </div>
          </div>
        )}

        {/* Walking instructions */}
        {mode === 'walking' && instructions && (
          <div
            className="step-instructions"
            dangerouslySetInnerHTML={{ __html: instructions }}
          />
        )}
      </div>
    </div>
  );
};

export default TransitResults;
