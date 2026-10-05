const PMaxThemesList = ({ plan }) => {
  if (!plan || !plan.search_themes) return null;
  return (
    <section className="result-card card">
      <h3>Performance Max themes</h3>
      <p>
        Written by the language model from the ad group names and their top keywords. Review them before adding them
        as search themes to a Performance Max asset group.
      </p>
      {plan.search_themes.length === 0 ? (
        <p>No themes, because no ad groups were built.</p>
      ) : (
        <ul>
          {plan.search_themes.map((theme, index) => (
            <li key={index}>{theme}</li>
          ))}
        </ul>
      )}
    </section>
  );
};

export default PMaxThemesList;
