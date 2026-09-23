import { useEffect, useRef } from "react";
export default function Cursor() {
  const ring = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const media = matchMedia(
      "(pointer: fine) and (prefers-reduced-motion: no-preference)",
    );
    let frame = 0;
    function move(event: PointerEvent) {
      if (!media.matches) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        if (!ring.current) return;
        ring.current.style.transform = `translate(${event.clientX - 14}px, ${event.clientY - 14}px)`;
        ring.current.style.opacity = "1";
      });
    }
    function hide() {
      if (ring.current) ring.current.style.opacity = "0";
    }
    window.addEventListener("pointermove", move);
    document.addEventListener("pointerleave", hide);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("pointermove", move);
      document.removeEventListener("pointerleave", hide);
    };
  }, []);
  return <div ref={ring} className="cursor-ring" aria-hidden="true" />;
}
