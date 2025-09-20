import React from 'react';

const PMaxThemesList = ({ plan }) => {
  if (!plan || !plan.search_themes) return null;
  return (
    <div className="result-card card">
      <h3>Deliverable 2: Performance Max Search Themes</h3>
      <p>Use these themes as signals in your PMax asset groups to guide Google's AI towards your most valuable customer queries.</p>
      <ul>
        {plan.search_themes.map((theme, index) => (
          <li key={index}>{theme}</li>
        ))}
      </ul>
    </div>
  );
};

export default PMaxThemesList;
