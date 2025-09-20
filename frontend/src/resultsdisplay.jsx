import React from 'react';
import SearchCampaignTable from './Searchcampaigntable.jsx';
import PMaxThemesList from './Pmaxthemeslist.jsx';
import ShoppingBidCard from './shoppingbidbard.jsx';

const ResultsDisplay = ({ results }) => {
  if (!results) return null;

  const { search_campaign_plan, pmax_plan, shopping_campaign_plan } = results;

  return (
    <div className="results-container">
      <h2 className="results-title">Your Generated SEM Plan</h2>
      <SearchCampaignTable plan={search_campaign_plan} />
      <PMaxThemesList plan={pmax_plan} />
      <ShoppingBidCard plan={shopping_campaign_plan} />
    </div>
  );
};

export default ResultsDisplay;
