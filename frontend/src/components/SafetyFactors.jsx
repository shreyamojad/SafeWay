function SafetyFactors({ factors }) {
  return (
    <div className="safety-factors">
      <h2>🔍 Risk Factors</h2>

      <ul>
        {factors.map((factor, index) => (
          <li key={index}>{factor}</li>
        ))}
      </ul>
    </div>
  );
}

export default SafetyFactors;