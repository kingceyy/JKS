import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import { Icon } from "@/components/Icons";
import { useUserData } from "@/hooks/useUserData";
import { hapticFeedback } from "@/utils/telegram";
import { ADSGRAM_BLOCK_ID, MONETAG_ZONE_ID } from "@/utils/constants";
import type { TabKey } from "@/components/BottomNav";

type AdState = "idle" | "loading" | "ad_playing" | "success" | "error";

// ── FAQ ────────────────────────────────────────────────────────────────────────

function Faq({ items }: { items: { q: string; a: string }[] }) {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <div className="space-y-2">
      {items.map((it, i) => {
        const isOpen = open === i;

        return (
          <div
            key={i}
            className="rounded-xl bg-white/[0.02] overflow-hidden"
          >
            <button
              onClick={() => setOpen(isOpen ? null : i)}
              className="w-full flex items-center justify-between gap-3 p-3 text-left text-sm font-medium"
            >
              <span>{it.q}</span>

              <motion.span
                animate={{ rotate: isOpen ? 180 : 0 }}
                className="opacity-60 flex-shrink-0"
              >
                <Icon.ChevronDown size={18} />
              </motion.span>
            </button>

            <AnimatePresence initial={false}>
              {isOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25 }}
                  className="overflow-hidden"
                >
                  <div className="px-3 pb-3 text-xs opacity-60 leading-relaxed">
                    {it.a}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}

// ── Countdown ──────────────────────────────────────────────────────────────────

function CountdownCircle({ expiry }: { expiry: string }) {
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);

  const total = 3_600_000;
  const remaining = Math.max(
    0,
    new Date(expiry).getTime() - now
  );

  const pct = remaining / total;

  const r = 70;
  const c = 2 * Math.PI * r;

  const h = Math.floor(remaining / 3_600_000);
  const m = Math.floor((remaining % 3_600_000) / 60_000);
  const s = Math.floor((remaining % 60_000) / 1_000);

  const fmt = (n: number) => n.toString().padStart(2, "0");

  return (
    <div
      className="relative flex items-center justify-center"
      style={{ width: 160, height: 160 }}
    >
      <svg width="160" height="160" className="-rotate-90">
        <circle
          cx="80"
          cy="80"
          r={r}
          stroke="rgba(255,255,255,0.04)"
          strokeWidth="6"
          fill="none"
        />

        <circle
          cx="80"
          cy="80"
          r={r}
          stroke="var(--success)"
          strokeWidth="6"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - pct)}
          style={{
            transition: "stroke-dashoffset 1s linear",
          }}
        />
      </svg>

      <div className="absolute text-center">
        <div
          className="font-mono text-2xl font-bold"
          style={{ color: "var(--success)" }}
        >
          {fmt(h)}:{fmt(m)}:{fmt(s)}
        </div>

        <div className="text-xs opacity-50 mt-1">
          restant
        </div>
      </div>
    </div>
  );
}

// ── Page principale ────────────────────────────────────────────────────────────

export function AccessPage({
  onNavigate,
}: {
  onNavigate: (k: TabKey) => void;
}) {
  const { data, activateSession } = useUserData();

  const [adState, setAdState] =
    useState<AdState>("idle");

  if (!data) return null;

  const sessionActive =
    !!data.sessionExpiry &&
    new Date(data.sessionExpiry).getTime() > Date.now();

  // ── Lancement des pubs ───────────────────────────────────────────────────────

  const runAds = useCallback(async () => {
    setAdState("loading");

    try {
      // ── 1. Monetag ──────────────────────────────────────────────────────

      const monetagFn = (
        window as Record<string, unknown>
      )[`show_${MONETAG_ZONE_ID}`] as
        | (() => Promise<void>)
        | undefined;

      if (typeof monetagFn === "function") {
        await monetagFn();
      } else {
        // SDK pas encore prêt
        await new Promise((r) =>
          setTimeout(r, 300)
        );

        const retry = (
          window as Record<string, unknown>
        )[`show_${MONETAG_ZONE_ID}`] as
          | (() => Promise<void>)
          | undefined;

        if (typeof retry === "function") {
          await retry();
        } else {
          console.warn(
            "[Monetag] SDK non chargé — pub ignorée"
          );
        }
      }

      // ── 2. AdsGram ─────────────────────────────────────────────────────

      setAdState("ad_playing");

      if (window.Adsgram) {
        const controller = window.Adsgram.init({
          blockId: ADSGRAM_BLOCK_ID,
        });

        await controller.show();
      } else {
        // Dev fallback
        await new Promise((r) =>
          setTimeout(r, 2000)
        );
      }

      // ── Succès ─────────────────────────────────────────────────────────

      setAdState("success");

      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: [
          "#6c5ce7",
          "#a29bfe",
          "#00b894",
          "#fdcb6e",
        ],
      });

      hapticFeedback("notification", "success");

      // Active la session
      await activateSession();

      // IMPORTANT:
      // On ne refresh PAS ici.
      // On garde le state optimiste.
      // Sinon sessionExpiry peut redevenir null.

      setTimeout(() => {
        setAdState("idle");
      }, 3000);
    } catch (e) {
      console.error("[runAds]", e);

      setAdState("error");

      hapticFeedback("notification", "error");
    }
  }, [activateSession]);

  // ── Session active ───────────────────────────────────────────────────────────

  if (sessionActive) {
    const expiry = new Date(data.sessionExpiry!);

    return (
      <div className="space-y-5">
        <div className="flex justify-center pt-2">
          <div
            className="flex items-center gap-2 px-3 py-1.5 rounded-full"
            style={{
              background: "rgba(0,184,148,0.12)",
              color: "var(--success)",
            }}
          >
            <span
              className="w-2 h-2 rounded-full animate-dot-pulse"
              style={{
                background: "var(--success)",
              }}
            />

            <span className="text-sm font-semibold">
              Session active
            </span>
          </div>
        </div>

        <div className="flex justify-center">
          <CountdownCircle
            expiry={data.sessionExpiry!}
          />
        </div>

        <div className="glass rounded-2xl p-4">
          <div className="divide-y divide-white/[0.04]">
            {[
              ["Type d'acces", "Session gratuite"],
              ["Duree", "1 heure"],
              [
                "Expire a",
                `${expiry
                  .getUTCHours()
                  .toString()
                  .padStart(2, "0")}:${expiry
                  .getUTCMinutes()
                  .toString()
                  .padStart(2, "0")} UTC`,
              ],
            ].map(([l, v], i) => (
              <div
                key={i}
                className="flex justify-between py-2.5 text-sm"
              >
                <span className="opacity-60">
                  {l}
                </span>

                <span className="font-semibold">
                  {v}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-center">
          <button
            onClick={runAds}
            disabled={adState !== "idle"}
            className="px-6 py-2.5 rounded-xl font-semibold text-sm active:scale-95 disabled:opacity-50"
            style={{
              background:
                "rgba(255,255,255,0.06)",
            }}
          >
            {adState === "idle"
              ? "Renouveler maintenant"
              : "En cours..."}
          </button>
        </div>

        <div className="glass rounded-2xl p-4">
          <div className="text-sm font-semibold opacity-70 mb-3">
            Pendant votre session vous pouvez
          </div>

          <div className="space-y-3">
            {(
              [
                [
                  Icon.Download,
                  "Telecharger tous les fichiers sans restriction",
                ],
                [
                  Icon.Search,
                  "Effectuer des recherches illimitees",
                ],
                [
                  Icon.Clock,
                  "Acces valable pendant toute la duree de la session",
                ],
                [
                  Icon.Shield,
                  "Aucune coupure pendant la session active",
                ],
              ] as [typeof Icon.Search, string][]
            ).map(([I, t], i) => (
              <div
                key={i}
                className="flex items-center gap-3"
              >
                <I
                  size={20}
                  style={{
                    color: "var(--accent-light)",
                  }}
                />

                <span className="text-sm opacity-80">
                  {t}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ── Pas de session ───────────────────────────────────────────────────────────

  return (
    <div className="space-y-5">
      <div className="flex justify-center pt-4">
        <div
          className="relative flex items-center justify-center"
          style={{ width: 112, height: 112 }}
        >
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background:
                "rgba(108,92,231,0.08)",
            }}
          />

          <div
            className="absolute rounded-full animate-pulse-ring"
            style={{
              width: 80,
              height: 80,
              background:
                "rgba(108,92,231,0.12)",
            }}
          />

          <Icon.Tv
            size={40}
            style={{
              color: "var(--accent-light)",
            }}
            className="relative"
          />
        </div>
      </div>

      <h2 className="text-xl font-bold text-center">
        Regardez une publicite
      </h2>

      <div className="space-y-3 max-w-sm mx-auto w-full">
        {[
          {
            n: 1,
            t: "Cliquez sur le bouton ci-dessous",
            color: "accent",
          },
          {
            n: 2,
            t: "Regardez les 2 publicites jusqu'a la fin",
            color: "accent",
          },
          {
            n: 3,
            t: (
              <>
                <span className="font-bold">
                  1 heure
                </span>{" "}
                d'acces gratuit debloque
              </>
            ),
            color: "success",
          },
        ].map((s) => (
          <div
            key={s.n}
            className="flex items-start gap-3"
          >
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
              style={{
                background:
                  s.color === "success"
                    ? "rgba(0,184,148,0.15)"
                    : "rgba(108,92,231,0.15)",

                color:
                  s.color === "success"
                    ? "var(--success)"
                    : "var(--accent-light)",
              }}
            >
              {s.n}
            </div>

            <div className="text-sm opacity-70 pt-0.5">
              {s.t}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export { Faq };