import type { Insight } from "@/lib/api";

export function Alerts({ insights }: { insights: Insight[] }) {
  return (
    <div className="alerts">
      {insights.map((insight) => (
        <div className={`alert ${insight.severity}`} key={`${insight.message}-${insight.recommendation}`}>
          <strong>{insight.message}</strong>
          <span className="muted">{insight.recommendation}</span>
        </div>
      ))}
      {insights.length === 0 ? <div className="alert"><strong>No alerts</strong></div> : null}
    </div>
  );
}
