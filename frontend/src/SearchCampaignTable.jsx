const formatMoney = (value) => `$${value.toFixed(2)}`;
const formatNumber = (value) => value.toLocaleString('en-US');

const SearchCampaignTable = ({ plan, estimated }) => {
  if (!plan || !plan.ad_groups) return null;
  const { ad_groups: adGroups, ranking } = plan;

  return (
    <section className="result-card card">
      <h3>
        Search campaigns
        {estimated && <span className="badge badge-estimated">Estimated figures</span>}
      </h3>
      <p className="method-note">
        Keywords with at least {formatNumber(ranking.min_avg_monthly_searches)} average monthly searches are ranked by
        score = {ranking.weight_volume} × volume + {ranking.weight_bid} × average top-of-page bid −{' '}
        {ranking.weight_competition} × competition, each scaled to 0 to 1 across the candidates. The top{' '}
        {ranking.max_keywords} are kept ({ranking.kept} of {ranking.candidates} here). The language model names the ad
        groups and assigns keywords to them. The CPC range is the mean low to mean high top-of-page bid of the
        group&apos;s keywords.
      </p>

      {adGroups.length === 0 && (
        <p>
          No keyword reached {formatNumber(ranking.min_avg_monthly_searches)} average monthly searches, so no ad groups
          were built.
        </p>
      )}

      {adGroups.map((group, index) => (
        <div className="ad-group" key={`${index}-${group.ad_group_name}`}>
          <div className="ad-group-header">
            <h4>{group.ad_group_name}</h4>
            <span>
              Suggested CPC: {formatMoney(group.cpc_range_low)} to {formatMoney(group.cpc_range_high)}
            </span>
            <span>Match types: {group.suggested_match_types.join(', ')}</span>
          </div>
          <div className="table-container">
            <table className="search-campaign-table">
              <thead>
                <tr>
                  <th>Keyword</th>
                  <th className="num">Avg. monthly searches</th>
                  <th className="num">Competition (0 to 100)</th>
                  <th className="num">Top-of-page bid</th>
                  <th className="num">Score</th>
                </tr>
              </thead>
              <tbody>
                {group.keywords.map((keyword) => (
                  <tr key={keyword.text}>
                    <td>{keyword.text}</td>
                    <td className="num">{formatNumber(keyword.avg_monthly_searches)}</td>
                    <td className="num">{keyword.competition_index}</td>
                    <td className="num">
                      {formatMoney(keyword.low_top_of_page_bid)} to {formatMoney(keyword.high_top_of_page_bid)}
                    </td>
                    <td className="num">{keyword.score.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </section>
  );
};

export default SearchCampaignTable;
