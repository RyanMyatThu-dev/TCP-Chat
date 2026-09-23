import { useEffect, useState } from "react";
const lines = [
  ["muted", "$ neon-chat host"],
  ["cyan", "◈  NEON / CHAT"],
  ["muted", "Creating your room…"],
  ["white", "ROOM  ABCD-1234-EFGH"],
  ["muted", "Invite → neon-chat join ABCD-1234-EFGH"],
  ["cyan", "23:04  ◇  Nova has joined the chat"],
  ["white", "23:04  Raven  ›  You made it."],
  ["white", "23:04  Nova   ›  Same time, different city."],
];
export default function Terminal() {
  const [count, setCount] = useState(0);
  const [replay, setReplay] = useState(0);
  useEffect(() => {
    const media = matchMedia("(prefers-reduced-motion: reduce)");
    if (media.matches) {
      setCount(lines.length);
      return;
    }
    setCount(0);
    const timer = setInterval(
      () =>
        setCount((n) => {
          if (n >= lines.length) {
            clearInterval(timer);
            return n;
          }
          return n + 1;
        }),
      440,
    );
    return () => clearInterval(timer);
  }, [replay]);
  return (
    <div className="terminal">
      <div className="terminal-bar">
        <span>
          <i /> SESSION PREVIEW
        </span>
        <button onClick={() => setReplay((n) => n + 1)}>Replay ↻</button>
      </div>
      <div
        className="terminal-body"
        aria-label="Illustrative terminal conversation, not a live room"
      >
        {lines.map(([style, text], i) => (
          <div
            key={text}
            className={style}
            style={{ visibility: i < count ? "visible" : "hidden" }}
          >
            {text}
          </div>
        ))}
        <div className="terminal-prompt">
          you <span>❯</span> <b className="caret" />
        </div>
      </div>
      <div className="terminal-bottom">
        <span>ENCRYPTED CONNECTION</span>
        <span>EXAMPLE ROOM / 02 PEOPLE</span>
      </div>
    </div>
  );
}
