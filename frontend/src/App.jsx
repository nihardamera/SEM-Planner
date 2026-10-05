import { useState } from 'react';
import InputForm from './InputForm.jsx';
import ResultsDisplay from './ResultsDisplay.jsx';
import LoadingSpinner from './LoadingSpinner.jsx';
import { generatePlan } from './PlanApi.js';

function App() {
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFormSubmit = async (formData) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      setResults(await generatePlan(formData));
    } catch (err) {
      setError(err.message || 'The plan could not be generated.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>SEM Planner</h1>
        <p>
          Drafts a Google Ads plan for Search, Performance Max and Shopping campaigns from a brand website, a
          competitor website, a product price and a target ROAS.
        </p>
      </header>
      <main>
        <InputForm onSubmit={handleFormSubmit} isLoading={isLoading} />
        {isLoading && <LoadingSpinner />}
        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}
        {results && <ResultsDisplay results={results} />}
      </main>
    </div>
  );
}

export default App;
