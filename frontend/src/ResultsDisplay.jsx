import SearchCampaignTable from './SearchCampaignTable.jsx';
import PMaxThemesList from './PMaxThemesList.jsx';
import ShoppingBidCard from './ShoppingBidCard.jsx';

const DataSourceBanner = ({ dataSource, reason }) => {
  if (dataSource === 'estimated') {
    return (
      <div className="data-banner data-banner-estimated" role="alert">
        <strong>Estimated data. These figures are not from Google Keyword Planner.</strong>
        <p>
          Search volumes, competition and bids below are placeholders so the rest of the plan can be drafted. Do not
          use them to set budgets or bids.
        </p>
        {reason && <p>Reason: {reason}</p>}
      </div>
    );
  }
  return (
    <div className="data-banner data-banner-live">
      Search volumes, competition and bids come from Google Keyword Planner.
    </div>
  );
};

const ResultsDisplay = ({ results }) => {
  if (!results) return null;

  const {
    data_source,
    estimated_reason,
    seed_keywords,
    seed_source,
    search_campaign_plan,
    pmax_plan,
    shopping_campaign_plan,
  } = results;
  const estimated = data_source === 'estimated';

  return (
    <div className="results-container">
      <h2 className="results-title">Plan</h2>
      <DataSourceBanner dataSource={data_source} reason={estimated_reason} />
      <p className="seed-note">
        <strong>Seed keywords</strong> (
        {seed_source === 'language_model'
          ? 'suggested by the language model'
          : 'Keyword Planner ideas for the brand URL'}
        ): {seed_keywords.join(', ')}
      </p>
      <SearchCampaignTable plan={search_campaign_plan} estimated={estimated} />
      <PMaxThemesList plan={pmax_plan} />
      <ShoppingBidCard plan={shopping_campaign_plan} />
    </div>
  );
};

export default ResultsDisplay;
