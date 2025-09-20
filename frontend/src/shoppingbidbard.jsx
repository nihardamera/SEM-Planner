import React from 'react';

const ShoppingBidCard = ({ plan }) => {
  if (!plan) return null;
  return (
    <div className="result-card card">
      <h3>Deliverable 3: Shopping Campaign Bid Strategy</h3>
      <p>This data-driven bid suggestion is calculated to align with your profitability goals.</p>
      <div className="shopping-bid-details">
        <div className="metric-item">
          <h4>Target CPA</h4>
          <p className="metric-value">${plan.target_cpa.toFixed(2)}</p>
          <span>Max cost per sale to meet ROAS goal.</span>
        </div>
        <div className="metric-item">
          <h4>Suggested Target CPC</h4>
          <p className="metric-value">${plan.suggested_target_cpc.toFixed(2)}</p>
          <span>Recommended bid per click.</span>
        </div>
      </div>
      <div className="explanation">
        <strong>Calculation Explained:</strong>
        <p>{plan.explanation}</p>
      </div>
    </div>
  );
};

export default ShoppingBidCard;
