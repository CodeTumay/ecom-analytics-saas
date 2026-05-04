"use client";

import type { AnalysisResponse } from "@/lib/api";
import { Save } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

const FIELDS = [
  "product_name",
  "revenue",
  "cost",
  "commission",
  "shipping",
  "ads_spend"
];

type MappingAnalysis = {
  columns: string[];
  missing_required: string[];
  missing_optional: string[];
};

function isMappingAnalysis(value: AnalysisResponse["analysis"]): value is MappingAnalysis {
  return Boolean(value && "columns" in value);
}

export function MappingForm({
  response,
  onSubmit
}: {
  response: AnalysisResponse;
  onSubmit: (mapping: Record<string, string>) => Promise<void>;
}) {
  const mappingAnalysis = isMappingAnalysis(response.analysis) ? response.analysis : undefined;
  const columns = mappingAnalysis?.columns || [];
  const [mapping, setMapping] = useState<Record<string, string>>(response.mapping || {});
  const [saving, setSaving] = useState(false);

  const missing = useMemo(
    () => [...(mappingAnalysis?.missing_required || []), ...(mappingAnalysis?.missing_optional || [])],
    [mappingAnalysis]
  );

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    try {
      await onSubmit(mapping);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="panel form" onSubmit={submit}>
      <div className="panel-header">
        <h2>Column Mapping</h2>
        <span className="status">{missing.length} fields need review</span>
      </div>
      <div className="mapping-grid">
        {FIELDS.map((field) => (
          <label className="field" key={field}>
            <span>{field}</span>
            <select
              value={mapping[field] || ""}
              onChange={(event) => setMapping((current) => ({
                ...current,
                [field]: event.target.value
              }))}
            >
              <option value="">Not available</option>
              {columns.map((column) => (
                <option value={column} key={column}>{column}</option>
              ))}
            </select>
          </label>
        ))}
      </div>
      <button className="primary-button" type="submit" disabled={saving}>
        <Save size={17} />
        {saving ? "Saving" : "Save mapping"}
      </button>
    </form>
  );
}
