import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import type { ComponentType, SVGProps } from "react";
import { Icon } from "./Icons";
import { hapticFeedback } from "@/utils/telegram";

export type TabKey = "home" | "access" | "premium" | "jessikaPay";

type IconCmp = ComponentType<SVGProps<SVGSVGElement> & { size?: number }>;

const TABS: { key: TabKey; label: string; Icon: IconCmp }[] = [
  { key: "home", label: "Accueil", Icon: Icon.Home },
  { key: "access", label: "Acces", Icon: Icon.Access },
  { key: "premium", label: "Premium", Icon: Icon.Crown },
  { key: "jessikaPay", label: "JessiKaPay", Icon: Icon.Wallet },
];

export function BottomNav({ active, onChange }: { active: TabKey; onChange: (k: TabKey) => void }) {
  const [hidden, setHidden] = useState(false);
  const lastY = useRef(0);

  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY;
      const delta = y - lastY.current;
      if (y < 40) setHidden(false);
      else if (delta > 6) setHidden(true);
      else if (delta < -6) setHidden(false);
      lastY.current = y;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.nav
      animate={{ y: hidden ? 120 : 0, rotateX: hidden ? -85 : 0, opacity: hidden ? 0 : 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 28 }}
      className="glass-strong fixed left-0 right-0 bottom-0 z-50 flex justify-around items-stretch"
      style={{
        height: "calc(64px + env(safe-area-inset-bottom))",
        paddingBottom: "env(safe-area-inset-bottom)",
        transformOrigin: "bottom center",
        perspective: 800,
      }}
    >
      {TABS.map(({ key, label, Icon: I }) => {
        const isActive = key === active;
        return (
          <button
            key={key}
            onClick={() => { hapticFeedback("selection"); onChange(key); }}
            className="relative flex-1 flex flex-col items-center justify-center gap-1 active:scale-95 transition-transform"
          >
            {isActive && (
              <motion.span
                layoutId="tab-pill"
                className="absolute top-0 h-[3px] w-8 rounded-full"
                style={{ background: "var(--accent)" }}
                transition={{ type: "spring", stiffness: 400, damping: 30 }}
              />
            )}
            <I size={22} strokeWidth={2.6} style={{ color: isActive ? "var(--accent-light)" : "var(--text-secondary)" }} />
            <span className="text-[10px] font-semibold" style={{ color: isActive ? "var(--accent-light)" : "var(--text-secondary)" }}>{label}</span>
          </button>
        );
      })}
    </motion.nav>
  );
}
