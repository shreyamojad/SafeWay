function RiskLevel({risk}) {

  return (
    <div className="risk-level">
      <h2>⚠️ Risk Level</h2>

      <div className="risk-value">
        {risk}
      </div>

      <p>Low risk detected on this route</p>
    </div>
  );
}

export default RiskLevel;