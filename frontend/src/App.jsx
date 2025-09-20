import { useState } from 'react';
import './app.css';
import InputForm from './inputform.jsx';
import ResultsDisplay from './resultsdisplay.jsx';
import LoadingSpinner from './loadingspinner.jsx';
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
      const data = await generatePlan(formData);
      setResults(data);
    } catch (err) {
      setError('Failed to generate plan. Please check the backend server and try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI-Powered SEM Planning Engine</h1>
        <p>Enter your brand details to generate a comprehensive multi-channel SEM strategy.</p>
      </header>
      <main>
        <InputForm onSubmit={handleFormSubmit} isLoading={isLoading} />
        {isLoading && <LoadingSpinner />}
        {error && <div className="error-message">{error}</div>}
        {results && <ResultsDisplay results={results} />}
      </main>
      <footer>
        <p>Developed by an AI Writing Assistant</p>
      </footer>
    </div>
  );
}

export default App;
