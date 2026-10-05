import { useState } from 'react';

const InputForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    brand_url: 'https://www.allbirds.com',
    competitor_url: 'https://www.rothys.com',
    average_product_price: '110',
    target_roas_percentage: '400',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      brand_url: formData.brand_url.trim(),
      competitor_url: formData.competitor_url.trim(),
      average_product_price: Number(formData.average_product_price),
      target_roas_percentage: Number(formData.target_roas_percentage),
    });
  };

  return (
    <div className="form-container card">
      <h2>Inputs</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="brand_url">Brand website URL</label>
            <input
              type="url"
              id="brand_url"
              name="brand_url"
              value={formData.brand_url}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="competitor_url">Competitor website URL</label>
            <input
              type="url"
              id="competitor_url"
              name="competitor_url"
              value={formData.competitor_url}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="average_product_price">Average product price ($)</label>
            <input
              type="number"
              id="average_product_price"
              name="average_product_price"
              value={formData.average_product_price}
              onChange={handleChange}
              min="0.01"
              step="any"
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
              step="any"
              required
            />
            <span className="field-hint">Revenue per unit of ad spend. 400% means $4 of sales for every $1 spent.</span>
          </div>
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Generating plan...' : 'Generate plan'}
        </button>
      </form>
    </div>
  );
};

export default InputForm;
