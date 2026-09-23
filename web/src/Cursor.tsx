import { useEffect, useRef } from "react";

/** Decorative pointer feedback. Native cursors and hit targets stay intact. */
export default function Cursor() {
  const ring = useRef<HTMLDivElement>(null);
  const effects = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const media = matchMedia(
      "(pointer: fine) and (prefers-reduced-motion: no-preference)",
    );
    let frame = 0;
    let lastTime = 0;
    let visible = false;
    let x = 0,
      y = 0,
      targetX = 0,
      targetY = 0;
    const bursts = new Set<HTMLDivElement>();

    function animate(time: number) {
      const elapsed = Math.min(time - lastTime, 64);
      lastTime = time;
      // Time-based damping stays consistent across 60 Hz and 144 Hz displays.
      const blend = 1 - Math.exp(-elapsed / 65);
      x += (targetX - x) * blend;
      y += (targetY - y) * blend;
      if (ring.current) {
        ring.current.style.transform = `translate3d(${x - 14}px, ${y - 14}px, 0)`;
      }
      if (Math.hypot(targetX - x, targetY - y) > 0.1) {
        frame = requestAnimationFrame(animate);
      } else {
        frame = 0;
      }
    }

    function move(event: PointerEvent) {
      if (!media.matches || event.pointerType === "touch") return;
      targetX = event.clientX;
      targetY = event.clientY;
      if (!visible) {
        x = targetX;
        y = targetY;
        visible = true;
        if (ring.current) ring.current.style.opacity = "1";
      }
      const interactive = (event.target as Element | null)?.closest(
        "a, button, input, summary",
      );
      ring.current?.classList.toggle(
        "cursor-interactive",
        Boolean(interactive),
      );
      if (!frame) {
        lastTime = performance.now();
        frame = requestAnimationFrame(animate);
      }
    }

    function click(event: PointerEvent) {
      if (
        !media.matches ||
        event.pointerType === "touch" ||
        event.button !== 0 ||
        !effects.current
      )
        return;
      // Bound work even during rapid repeated clicks.
      if (bursts.size >= 8) {
        const oldest = bursts.values().next().value;
        if (oldest) {
          oldest.remove();
          bursts.delete(oldest);
        }
      }
      const burst = document.createElement("div");
      burst.className = "pixel-burst";
      burst.style.left = `${event.clientX}px`;
      burst.style.top = `${event.clientY}px`;
      for (let i = 0; i < 8; i++) {
        const pixel = document.createElement("i");
        const angle = (i * Math.PI) / 4;
        const distance = i % 2 ? 30 : 42;
        pixel.style.setProperty(
          "--dx",
          `${Math.round(Math.cos(angle) * distance)}px`,
        );
        pixel.style.setProperty(
          "--dy",
          `${Math.round(Math.sin(angle) * distance)}px`,
        );
        burst.append(pixel);
      }
      burst.addEventListener(
        "animationend",
        () => {
          burst.remove();
          bursts.delete(burst);
        },
        { once: true },
      );
      bursts.add(burst);
      effects.current.append(burst);
    }

    function hide() {
      visible = false;
      cancelAnimationFrame(frame);
      frame = 0;
      if (ring.current) ring.current.style.opacity = "0";
    }
    function reset() {
      hide();
      bursts.forEach((burst) => burst.remove());
      bursts.clear();
    }
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerdown", click);
    window.addEventListener("blur", reset);
    document.addEventListener("pointerleave", hide);
    document.addEventListener("visibilitychange", reset);
    media.addEventListener("change", reset);
    return () => {
      reset();
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerdown", click);
      window.removeEventListener("blur", reset);
      document.removeEventListener("pointerleave", hide);
      document.removeEventListener("visibilitychange", reset);
      media.removeEventListener("change", reset);
    };
  }, []);

  return (
    <div className="cursor-effects" ref={effects} aria-hidden="true">
      <div ref={ring} className="cursor-ring">
        <span />
      </div>
    </div>
  );
}
