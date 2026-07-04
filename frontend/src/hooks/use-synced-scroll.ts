import { useEffect, useRef, type RefObject } from "react";

/** Keep two scroll containers aligned by scroll percentage (either direction). */
export function useSyncedScroll(
  leftRef: RefObject<HTMLElement | null>,
  rightRef: RefObject<HTMLElement | null>,
  enabled = true
) {
  const syncing = useRef(false);

  useEffect(() => {
    if (!enabled) return;

    const left = leftRef.current;
    const right = rightRef.current;
    if (!left || !right) return;

    const applyScroll = (source: HTMLElement, target: HTMLElement) => {
      const sourceMax = source.scrollHeight - source.clientHeight;
      const targetMax = target.scrollHeight - target.clientHeight;
      if (sourceMax <= 0 || targetMax <= 0) return;

      const ratio = source.scrollTop / sourceMax;
      target.scrollTop = ratio * targetMax;
    };

    const onLeftScroll = () => {
      if (syncing.current) return;
      syncing.current = true;
      applyScroll(left, right);
      requestAnimationFrame(() => {
        syncing.current = false;
      });
    };

    const onRightScroll = () => {
      if (syncing.current) return;
      syncing.current = true;
      applyScroll(right, left);
      requestAnimationFrame(() => {
        syncing.current = false;
      });
    };

    left.addEventListener("scroll", onLeftScroll, { passive: true });
    right.addEventListener("scroll", onRightScroll, { passive: true });

    return () => {
      left.removeEventListener("scroll", onLeftScroll);
      right.removeEventListener("scroll", onRightScroll);
    };
  }, [leftRef, rightRef, enabled]);
}
