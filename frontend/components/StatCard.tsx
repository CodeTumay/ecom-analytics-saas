type Props = {
  label: string;
  value: string;
  negative?: boolean;
};

export function StatCard({ label, value, negative }: Props) {
  return (
    <div className={`stat ${negative ? "negative" : ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
