const ShoppingBidCard = ({ plan }) => {
  if (!plan) return null;
  return (
    <section className="result-card card">
      <h3>Shopping bids</h3>
      <p>Calculated from the product price and target ROAS with a fixed formula. The language model is not involved.</p>
      <div className="shopping-bid-details">
        <div className="metric-item">
          <h4>Target CPA</h4>
          <p className="metric-value">${plan.target_cpa.toFixed(2)}</p>
          <span>Most you can pay per sale and still meet the ROAS target.</span>
        </div>
        <div className="metric-item">
          <h4>Suggested target CPC</h4>
          <p className="metric-value">${plan.suggested_target_cpc.toFixed(2)}</p>
          <span>Target CPA multiplied by the assumed conversion rate.</span>
        </div>
        <div className="metric-item">
          <h4>Assumed conversion rate</h4>
          <p className="metric-value">{(plan.assumed_conversion_rate * 100).toFixed(1)}%</p>
          <span>An assumption, not measured from your account.</span>
        </div>
      </div>
      <div className="explanation">
        <strong>How it is calculated</strong>
        <p>{plan.explanation}</p>
      </div>
    </section>
  );
};

export default ShoppingBidCard;
