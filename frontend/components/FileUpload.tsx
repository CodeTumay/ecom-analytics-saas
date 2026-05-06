"use client";

import { Upload } from "lucide-react";
import { ChangeEvent, useRef, useState } from "react";

export function FileUpload({
  disabled,
  labels,
  onFile
}: {
  disabled?: boolean;
  labels?: {
    title: string;
    subtitle: string;
    button: string;
  };
  onFile: (file: File) => Promise<void>;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState("");

  async function handleChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    await onFile(file);
    event.target.value = "";
  }

  return (
    <div className="upload-box">
      <div className="upload-copy">
        <strong>{fileName || labels?.title || "Retail Health data file"}</strong>
        <span>{labels?.subtitle || "CSV or Excel"}</span>
      </div>
      <input
        className="hidden-file"
        type="file"
        accept=".csv,.xlsx"
        ref={inputRef}
        onChange={handleChange}
      />
      <button
        className="primary-button"
        type="button"
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
      >
        <Upload size={17} />
        {labels?.button || "Upload"}
      </button>
    </div>
  );
}
