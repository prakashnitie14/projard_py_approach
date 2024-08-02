import React from 'react';

function ResultsScreen({ data }) {
  if (!data) {
    return <div>No results to display</div>;
  }

  return (
    <div>
      <h1>Analysis Results</h1>
      {/* Render your results here */}
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export default ResultsScreen;
