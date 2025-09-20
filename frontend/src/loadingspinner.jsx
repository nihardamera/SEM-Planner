import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      <p>Generating your strategic plan... this may take a moment.</p>
    </div>
  );
};

export default LoadingSpinner;
