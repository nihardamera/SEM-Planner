import React from 'react';

const SearchCampaignTable = ({ plan }) => {
  if (!plan || !plan.ad_groups) return null;

  return (
    <div className="result-card card">
      <h3>Deliverable 1: Search Campaign Structure</h3>
      <table className="search-campaign-table">
        <thead>
          <tr>
            <th>Ad Group</th>
            <th>Theme</th>
            <th>Keywords</th>
            <th>Match Types</th>
            <th>Suggested CPC Range</th>
          </tr>
        </thead>
        <tbody>
          {plan.ad_groups.map((group, idx) => (
            <tr key={idx}>
              <td>{group.ad_group_name}</td>
              <td>{group.theme}</td>
              <td>{group.keywords.join(', ')}</td>
              <td>{group.suggested_match_types.join(', ')}</td>
              <td>{group.suggested_cpc_range}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SearchCampaignTable;
