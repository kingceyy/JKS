import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import { Icon } from "@/components/Icons";
import { useUserData, formatRemaining } from "@/hooks/useUserData";
import { hapticFeedback, sendData } from "@/utils/telegram";
import { ADSGRAM_BLOCK_ID, MONETAG_ZONE_ID } from "@/utils/constants";
import type { TabKey } from "@/components/BottomNav";

type AdState = "idle" | "loading" | "ad_playing" | "success" | "error";

function Faq({ items }: { items: { q: string; a: string }[] }) {
  const [open, setOpen] = useState<number | null>(null);
  return (
    <div className="space-y-2">
      {items.map((it, i) => {
        const isOpen = open === i;
        return (
          <div key={i} className="rounded-xl bg-white/[0.02] overflow-hidden">
            <button
              onClick={() => setOpen(isOpen ? null : i)}
              className="w-full flex items-center justify-between gap-3 p-3 text-left text-sm font-medium"
            >
              <span>{it.q}</span>
              <motion.span animate={{ rotate: isOpen ? 180 : 0 }} className="opacity-60 flex-shrink-0">
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
                  <div className="px-3 pb-3 text-xs opacity-60 leading-relaxed">{it.a}</div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}

function CountdownCircle({ expiry }: { expiry: string }) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => { const t = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(t); }, []);
  const total = 3600000;
  const remaining = Math.max(0, new Date(expiry).getTime() - now);
  const pct = remaining / total;
  const r = 70, c = 2 * Math.PI * r;
  const h = Math.floor(remaining / 3600000);
  const m = Math.floor((remaining % 3600000) / 60000);
  const s = Math.floor((remaining % 60000) / 1000);
  const fmt = (n: number) => n.toString().padStart(2, "0");

  return (
    <div className="relative flex items-center justify-center" style={{ width: 160, height: 160 }}>
      <svg width="160" height="160" className="-rotate-90">
        <circle cx="80" cy="80" r={r} stroke="rgba(255,255,255,0.04)" strokeWidth="6" fill="none" />
        <circle cx="80" cy="80" r={r} stroke="var(--success)" strokeWidth="6" fill="none"
          strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - pct)}
          style={{ transition: "stroke-dashoffset 1s linear" }} />
      </svg>
      <div className="absolute text-center">
        <div className="font-mono text-2xl font-bold" style={{ color: "var(--success)" }}>{fmt(h)}:{fmt(m)}:{fmt(s)}</div>
        <div className="text-xs opacity-50 mt-1">restant</div>
      </div>
    </div>
  );
}

export function AccessPage({ onNavigate }: { onNavigate: (k: TabKey) => void }) {
  const { data, activateSession } = useUserData();
  const [adState, setAdState] = useState<AdState>("idle");

  if (!data) return null;
  const sessionActive = data.sessionExpiry && new Date(data.sessionExpiry).getTime() > Date.now();

  const runAds = async () => {
    setAdState("loading");
    try {
      if (typeof window.show_interstitial === "function") {
        await window.show_interstitial(MONETAG_ZONE_ID);
      } else {
        await new Promise(r => setTimeout(r, 1500));
      }
      setAdState("ad_playing");
      if (window.Adsgram) {
        await window.Adsgram.init({ blockId: ADSGRAM_BLOCK_ID }).show();
      } else {
        await new Promise(r => setTimeout(r, 2000));
      }
      setAdState("success");
      confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 }, colors: ["#6c5ce7","#a29bfe","#00b894","#fdcb6e"] });
      hapticFeedback("notification", "success");
      sendData({ action: "ad_watched" });
      activateSession();
      setTimeout(() => setAdState("idle"), 2500);
    } catch {
      setAdState("error");
      hapticFeedback("notification", "error");
    }
  };

  if (sessionActive) {
    const expiry = new Date(data.sessionExpiry!);
    return (
      <div className="space-y-5">
        <div className="flex justify-center pt-2">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full" style={{ background: "rgba(0,184,148,0.12)", color: "var(--success)" }}>
            <span className="w-2 h-2 rounded-full animate-dot-pulse" style={{ background: "var(--success)" }} />
            <span className="text-sm font-semibold">Session active</span>
          </div>
        </div>
        <div className="flex justify-center"><CountdownCircle expiry={data.sessionExpiry!} /></div>

        <div className="glass rounded-2xl p-4">
          <div className="divide-y divide-white/[0.04]">
            {[
              ["Type d'acces", "Session gratuite"],
              ["Duree", "1 heure"],
              ["Expire a", `${expiry.getUTCHours().toString().padStart(2,"0")}:${expiry.getUTCMinutes().toString().padStart(2,"0")} UTC`],
            ].map(([l,v],i) => (
              <div key={i} className="flex justify-between py-2.5 text-sm">
                <span className="opacity-60">{l}</span><span className="font-semibold">{v}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-center">
          <button onClick={runAds} className="px-6 py-2.5 rounded-xl font-semibold text-sm active:scale-95"
            style={{ background: "rgba(255,255,255,0.06)" }}>
            Renouveler maintenant
          </button>
        </div>

        <div className="glass rounded-2xl p-4">
          <div className="text-sm font-semibold opacity-70 mb-3">Pendant votre session vous pouvez</div>
          <div className="space-y-3">
            {[
              [Icon.Download, "Telecharger tous les fichiers sans restriction"],
              [Icon.Search, "Effectuer des recherches illimitees"],
              [Icon.Clock, "Acces valable pendant toute la duree de la session"],
              [Icon.Shield, "Aucune coupure pendant la session active"],
            ].map(([I, t], i) => {
              const C = I as typeof Icon.Search;
              return (
                <div key={i} className="flex items-center gap-3">
                  <C size={20} style={{ color: "var(--accent-light)" }} />
                  <span className="text-sm opacity-80">{t as string}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex justify-center pt-4">
        <div className="relative flex items-center justify-center" style={{ width: 112, height: 112 }}>
          <div className="absolute inset-0 rounded-full" style={{ background: "rgba(108,92,231,0.08)" }} />
          <div className="absolute rounded-full animate-pulse-ring" style={{ width: 80, height: 80, background: "rgba(108,92,231,0.12)" }} />
          <Icon.Tv size={40} style={{ color: "var(--accent-light)" }} className="relative" />
        </div>
      </div>

      <h2 className="text-xl font-bold text-center">Regardez une publicite</h2>

      <div className="space-y-3 max-w-sm mx-auto w-full">
        {[
          { n: 1, t: "Cliquez sur le bouton ci-dessous", color: "accent" },
          { n: 2, t: "Regardez les 2 publicites jusqu'a la fin", color: "accent" },
          { n: 3, t: <>Profitez de <span className="font-bold">1 heure</span> d'acces gratuit</>, color: "success" },
        ].map((s) => (
          <div key={s.n} className="flex items-start gap-3">
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
              style={{
                background: s.color === "success" ? "rgba(0,184,148,0.15)" : "rgba(108,92,231,0.15)",
                color: s.color === "success" ? "var(--success)" : "var(--accent-light)",
              }}
            >{s.n}</div>
            <div className="text-sm opacity-70 pt-0.5">{s.t}</div>
          </div>
        ))}
      </div>

      <div className="flex justify-center">
        <AnimatePresence mode="wait">
          {adState === "idle" && (
            <motion.button key="idle" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              onClick={runAds}
              className="flex items-center gap-2 px-8 py-4 rounded-2xl text-white font-bold animate-glow-pulse active:scale-95"
              style={{ background: "linear-gradient(135deg, var(--accent), #5a4bd1)" }}>
              <Icon.Play size={18} /> Regarder la publicite
            </motion.button>
          )}
          {adState === "loading" && (
            <motion.button key="l" disabled initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="flex items-center gap-2 px-8 py-4 rounded-2xl font-bold text-white"
              style={{ background: "rgba(108,92,231,0.3)" }}>
              <Icon.Spinner size={18} /> Chargement...
            </motion.button>
          )}
          {adState === "ad_playing" && (
            <motion.button key="ap" disabled initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="flex items-center gap-2 px-8 py-4 rounded-2xl font-bold"
              style={{ background: "rgba(253,203,110,0.12)", color: "var(--warning)" }}>
              <Icon.Spinner size={18} /> Publicite en cours...
            </motion.button>
          )}
          {adState === "success" && (
            <motion.div key="s" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="px-8 py-4 rounded-2xl font-bold"
              style={{ background: "rgba(0,184,148,0.12)", color: "var(--success)" }}>
              Session activee avec succes !
            </motion.div>
          )}
          {adState === "error" && (
            <motion.button key="e" onClick={() => setAdState("idle")} initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="px-8 py-4 rounded-2xl font-bold"
              style={{ background: "rgba(225,112,85,0.12)", color: "var(--error)" }}>
              Erreur — Cliquez pour reessayer
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      <div className="text-xs opacity-40 text-center">La session expire apres 1 heure</div>

      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-3">Comment fonctionnent les sessions</div>
        <div className="space-y-2 text-xs opacity-60 leading-relaxed">
          <p>Une session gratuite vous donne un acces complet a tous les fichiers du bot pendant 1 heure.</p>
          <p>Pour activer une session, vous devez regarder deux courtes publicites : une publicite interstitielle suivie d'une publicite video recompensee.</p>
          <p>Les deux publicites doivent etre regardees integralement pour que la session soit validee.</p>
          <p>Vous pouvez renouveler votre session a tout moment en regardant de nouvelles publicites, meme si votre session precedente n'a pas encore expire.</p>
        </div>
      </div>

      <div className="glass rounded-2xl p-4 text-center">
        <div className="text-sm mb-3 opacity-80">Vous voulez un acces sans publicite ?</div>
        <button onClick={() => onNavigate("premium")}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold active:scale-95"
          style={{ background: "linear-gradient(135deg, #f9ca24, #f0932b)", color: "#1a1a2e" }}>
          <Icon.Crown size={18} /> Voir les plans Premium
        </button>
      </div>

      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-3">Questions frequentes</div>
        <Faq items={[
          { q: "Combien de fois puis-je regarder des publicites par jour ?", a: "Il n'y a aucune limite. Vous pouvez renouveler votre session autant de fois que vous le souhaitez." },
          { q: "Ma session est-elle partageable ?", a: "Non, chaque session est liee a votre compte Telegram et ne peut pas etre transferee." },
          { q: "Que se passe-t-il quand ma session expire ?", a: "Vous devrez regarder de nouvelles publicites ou souscrire a un plan premium pour retrouver l'acces aux fichiers." },
          { q: "Les publicites sont-elles securisees ?", a: "Oui, toutes les publicites proviennent de reseaux certifies (AdsGram et Monetag) et ne contiennent aucun contenu malveillant." },
        ]} />
      </div>
    </div>
  );
}

export { Faq };
