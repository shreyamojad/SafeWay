function SafetyScore({ score }) {
  let message = "";

  if (score === null || score === undefined) {
    message = "Waiting for safety analysis";
  } else if (score >= 80) {
    message = "Route is very safe";
  } else if (score >= 60) {
    message = "Route is relatively safe";
  } else if (score >= 40) {
    message = "Route has moderate risk";
  } else {
    message = "Route has high risk";
  }

  return (
    <div className="safety-score">
      <h2>🛡️ Safety Score</h2>

      <div className="score-number">
        {score !== null && score !== undefined
          ? `${score}/100`
          : "--"}
      </div>

      <p>{message}</p>
    </div>
  );
}

export default SafetyScore;