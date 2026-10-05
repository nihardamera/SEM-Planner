const LoadingSpinner = () => {
  return (
    <div className="spinner-container" role="status">
      <div className="spinner"></div>
      <p>Generating the plan. This calls Keyword Planner and the language model, so it can take a while.</p>
    </div>
  );
};

export default LoadingSpinner;
