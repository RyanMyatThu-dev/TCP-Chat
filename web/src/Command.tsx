import { useEffect, useRef, useState } from "react";
export default function Command({
  text,
  label = "Copy command",
}: {
  text: string;
  label?: string;
}) {
  const [status, setStatus] = useState("");
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);
  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setStatus("Copied");
    } catch {
      setStatus("Select the command to copy it manually.");
    }
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setStatus(""), 3000);
  }
  return (
    <div className="command-wrap">
      <div className="command">
        <span aria-hidden="true">$</span>
        <code>{text}</code>
        <button onClick={copy} aria-label={label} title={label}>
          {status === "Copied" ? "✓" : "⧉"}
        </button>
      </div>
      <span className="copy-status" role="status">
        {status}
      </span>
    </div>
  );
}
