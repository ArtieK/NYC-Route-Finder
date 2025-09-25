/**
 * Utility functions for formatting data for display.
 */

/**
 * Format currency value to USD string.
 * @param {number} amount - Amount in dollars
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) {
    return 'N/A';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

/**
 * Format price range for display.
 * @param {number} min - Minimum price
 * @param {number} max - Maximum price
 * @returns {string} Formatted price range
 */
export const formatPriceRange = (min, max) => {
  if (!min && !max) return 'N/A';
  if (!max || min === max) return formatCurrency(min);
  return `${formatCurrency(min)} - ${formatCurrency(max)}`;
};

/**
 * Format duration in minutes to readable string.
 * @param {number} minutes - Duration in minutes
 * @returns {string} Formatted duration
 */
export const formatDuration = (minutes) => {
  if (!minutes) return 'N/A';

  if (minutes < 60) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (remainingMinutes === 0) {
    return `${hours} hr`;
  }

  return `${hours} hr ${remainingMinutes} min`;
};

/**
 * Format distance in miles.
 * @param {number} miles - Distance in miles
 * @returns {string} Formatted distance
 */
export const formatDistance = (miles) => {
  if (!miles) return 'N/A';
  return `${miles.toFixed(1)} mi`;
};

/**
 * Capitalize first letter of string.
 * @param {string} str - Input string
 * @returns {string} Capitalized string
 */
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

/**
 * Format vehicle type for display.
 * @param {string} vehicleType - Vehicle type identifier
 * @returns {string} Formatted vehicle type
 */
export const formatVehicleType = (vehicleType) => {
  if (!vehicleType) return 'Unknown';

  const typeMap = {
    'uberx': 'UberX',
    'uber_bike': 'Uber Bike',
    'uber_scooter': 'Uber Scooter',
    'lyft': 'Lyft',
    'lyft_bike': 'Lyft Bike',
    'lyft_scooter': 'Lyft Scooter',
    'transit': 'Public Transit',
  };

  return typeMap[vehicleType.toLowerCase()] || capitalize(vehicleType);
};

export default {
  formatCurrency,
  formatPriceRange,
  formatDuration,
  formatDistance,
  capitalize,
  formatVehicleType,
};
