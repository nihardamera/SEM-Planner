import React, { useState } from 'react';

const InputForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    brand_url: 'https://www.allbirds.com',
    competitor_url: 'https://www.rothys.com',
    service_locations: 'USA',
    search_ads_budget: 5000,
    shopping_ads_budget: 7000,
    pmax_ads_budget: 8000,
    average_product_price: 110,
    target_roas_percentage: 400,
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prevData) => ({
     ...prevData,
      [name]: type === 'number'? parseFloat(value) : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="form-container card">
      <h2>Configuration</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="brand_url">Your Website URL</label>
            <input
              type="text"
              id="brand_url"
              name="brand_url"
              value={formData.brand_url}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="competitor_url">Competitor's Website URL</label>
            <input
              type="text"
              id="competitor_url"
              name="competitor_url"
              value={formData.competitor_url}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="service_locations">Service Locations</label>
            <input
              type="text"
              id="service_locations"
              name="service_locations"
              value={formData.service_locations}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="average_product_price">Average Product Price ($)</label>
            <input
              type="number"
              id="average_product_price"
              name="average_product_price"
              value={formData.average_product_price}
              onChange={handleChange}
              min="1"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="target_roas_percentage">Target ROAS (%)</label>
            <input
              type="number"
              id="target_roas_percentage"
              name="target_roas_percentage"
              value={formData.target_roas_percentage}
              onChange={handleChange}
              min="1"
              required
            />
          </div>
        </div>
        
        <h3>Monthly Ad Budgets ($)</h3>
        <div className="form-grid budget-grid">
          <div className="form-group">
            <label htmlFor="search_ads_budget">Search Ads</label>
            <input
              type="number"
              id="search_ads_budget"
              name="search_ads_budget"
              value={formData.search_ads_budget}
              onChange={handleChange}
              min="1"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="shopping_ads_budget">Shopping Ads</label>
            <input
              type="number"
              id="shopping_ads_budget"
              name="shopping_ads_budget"
              value={formData.shopping_ads_budget}
              onChange={handleChange}
              min="1"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="pmax_ads_budget">Performance Max</label>
            <input
              type="number"
              id="pmax_ads_budget"
              name="pmax_ads_budget"
              value={formData.pmax_ads_budget}
              onChange={handleChange}
              min="1"
              required
            />
          </div>
        </div>
        
        <button type="submit" disabled={isLoading}>
          {isLoading? 'Generating Plan...' : 'Generate SEM Plan'}
        </button>
      </form>
    </div>
  );
};

export default InputForm;
