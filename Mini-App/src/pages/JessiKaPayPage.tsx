import { useEffect, useRef, useState } from "react";
import { motion, useInView } from "framer-motion";
import { Icon } from "@/components/Icons";
import { openTelegramLink } from "@/utils/telegram";
import { JESSIKAPAY_TG } from "@/utils/constants";

function CountUp({ end, suffix = "" }: { end: number; suffix?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    const start = performance.now();
    const dur = 2000;
    let raf = 0;
    const step = (t: number) => {
      const p = Math.min(1, (t - start) / dur);
      const e = 1 - Math.pow(1 - p, 3);
      setVal(Math.floor(end * e));
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [inView, end]);
  return <span ref={ref}>{val.toLocaleString("fr-FR")}{suffix}</span>;
}

function FeatureCard({ i, gradient, Icon: I, title, desc }: { i: number; gradient: string; Icon: typeof Icon.Zap; title: string; desc: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-50px" });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40, rotateX: 10 }}
      animate={inView ? { opacity: 1, y: 0, rotateX: 0 } : {}}
      transition={{ delay: i * 0.1, duration: 0.5 }}
      className="glass rounded-2xl p-5 relative overflow-hidden"
      style={{ backgroundImage: gradient }}
    >
      <I size={60} className="absolute top-2 right-2 opacity-[0.08]" />
      <I size={32} className="mb-3" style={{ color: "var(--accent-light)" }} />
      <div className="text-base font-bold mb-1.5">{title}</div>
      <div className="text-[13px] opacity-60 leading-relaxed">{desc}</div>
    </motion.div>
  );
}

export function JessiKaPayPage() {
  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="relative pt-6 pb-2 text-center overflow-hidden">
        <div className="absolute pointer-events-none" style={{ top: 0, left: 0, width: 160, height: 160, background: "radial-gradient(circle, rgba(108,92,231,0.3), transparent 70%)", filter: "blur(50px)" }} />
        <div className="absolute pointer-events-none" style={{ bottom: 0, right: 0, width: 128, height: 128, background: "radial-gradient(circle, rgba(0,184,148,0.25), transparent 70%)", filter: "blur(50px)" }} />
        <motion.div
          initial={{ scale: 0, rotate: -180 }} animate={{ scale: 1, rotate: 0 }}
          transition={{ delay: 0.2, type: "spring", damping: 14 }}
          className="relative w-24 h-24 mx-auto rounded-3xl flex items-center justify-center"
          style={{ background: "linear-gradient(135deg, var(--accent), var(--success))", boxShadow: "0 10px 40px rgba(108,92,231,0.4)" }}
        >
          <Icon.Money size={40} className="text-white" />
        </motion.div>
        <h1 className="text-4xl font-extrabold mt-4 text-gradient">JessiKaPay</h1>
        <p className="text-sm opacity-60 mt-2 max-w-[280px] mx-auto">La plateforme de transfert d'argent la plus rapide d'Afrique</p>
      </div>

      {/* Features */}
      <div className="space-y-3">
        <FeatureCard i={0} gradient="linear-gradient(135deg, rgba(168,85,247,0.15), rgba(59,130,246,0.08))" Icon={Icon.Zap}
          title="Transferts instantanes" desc="Envoyez et recevez de l'argent en quelques secondes, partout en Afrique. Pas d'attente, pas de complications. Votre argent arrive immediatement." />
        <FeatureCard i={1} gradient="linear-gradient(135deg, rgba(34,197,94,0.15), rgba(20,184,166,0.08))" Icon={Icon.Globe}
          title="11 pays couverts" desc="Agree par des agregateurs de la BCEAO et de l'UEMOA. Disponible au Togo, Burkina Faso, Niger, Senegal, Mali, RDC, Benin, Cote d'Ivoire, Cameroun, Guinee, Senegal et d'autres pays couverts par MoneyFusion en payin." />
        <FeatureCard i={2} gradient="linear-gradient(135deg, rgba(249,115,22,0.15), rgba(239,68,68,0.08))" Icon={Icon.Lock}
          title="Securise" desc="Toutes vos transactions sont protegees par un chiffrement de bout en bout. Vos donnees personnelles et financieres restent strictement confidentielles." />
        <FeatureCard i={3} gradient="linear-gradient(135deg, rgba(236,72,153,0.15), rgba(168,85,247,0.08))" Icon={Icon.Card}
          title="Multi-methodes" desc="Mobile Money (Orange, Wave, Flooz, M-Pesa), carte bancaire, crypto-monnaie — choisissez la methode qui vous convient le mieux." />
      </div>

      {/* Counters */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { v: 5000, s: "+", l: "Utilisateurs" },
          { v: 11, s: "", l: "Pays" },
          { v: 24, s: "/7", l: "Disponibilite" },
        ].map((c, i) => (
          <motion.div key={c.l}
            initial={{ scale: 0.8, opacity: 0 }} whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true }} transition={{ delay: i * 0.15 }}
            className="glass rounded-2xl p-4 text-center">
            <div className="text-2xl font-bold"><CountUp end={c.v} suffix={c.s} /></div>
            <div className="text-xs opacity-50 mt-1">{c.l}</div>
          </motion.div>
        ))}
      </div>

      {/* Testimonials */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-bold text-center opacity-70 mb-3">Ce que disent nos utilisateurs</div>
        <div className="space-y-2">
          {[
            { code: "TG", color: "#0ea15a", name: "Amidou K.", quote: "Rapide et fiable ! J'envoie de l'argent en 10 secondes." },
            { code: "SN", color: "#0d8a4a", name: "Fatou S.", quote: "Le meilleur service de transfert que j'ai utilise." },
            { code: "CI", color: "#f97316", name: "Kouassi B.", quote: "Simple, securise et pas cher. Je recommande !" },
          ].map((t, i) => (
            <motion.div key={i}
              initial={{ x: -20, opacity: 0 }} whileInView={{ x: 0, opacity: 1 }}
              viewport={{ once: true }} transition={{ delay: i * 0.1 }}
              className="flex items-center gap-3 p-3 rounded-xl" style={{ background: "rgba(255,255,255,0.02)" }}>
              <div className="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0" style={{ background: t.color }}>{t.code}</div>
              <div className="min-w-0">
                <div className="text-xs font-bold">{t.name}</div>
                <div className="text-xs opacity-50 italic">"{t.quote}"</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Countries */}
      <div className="glass rounded-2xl p-4 text-center">
        <div className="text-sm font-bold opacity-70 mb-1">Pays disponibles</div>
        <div className="text-[11px] opacity-50 mb-3">Agree BCEAO / UEMOA — propulse par MoneyFusion</div>
        <div className="flex flex-wrap gap-2 justify-center">
          {["TG Togo","BF Burkina Faso","NE Niger","SN Senegal","ML Mali","CD RDC","BJ Benin","CI Cote d'Ivoire","CM Cameroun","GN Guinee","BF +"].map((c, i) => (
            <motion.span key={c}
              initial={{ scale: 0.8, opacity: 0 }} whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }} transition={{ delay: i * 0.05 }}
              className="px-3 py-1.5 rounded-full text-xs" style={{ background: "rgba(255,255,255,0.04)" }}>{c}</motion.span>
          ))}
        </div>
      </div>

      {/* How */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-bold opacity-70 mb-3">Comment utiliser JessiKaPay</div>
        <div className="space-y-3 relative">
          {[
            "Ouvrez @JessiKaPayBot sur Telegram",
            "Creez votre compte en quelques secondes",
            "Selectionnez le pays et le montant a envoyer",
            "Confirmez et l'argent est envoye instantanement",
          ].map((s, i, arr) => (
            <div key={i} className="flex items-start gap-3 relative">
              <div className="relative flex flex-col items-center">
                <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 z-10"
                  style={{ background: "rgba(108,92,231,0.15)", color: "var(--accent-light)" }}>{i+1}</div>
                {i < arr.length - 1 && <div className="w-px h-6 mt-1 border-l border-dashed" style={{ borderColor: "rgba(255,255,255,0.1)" }} />}
              </div>
              <div className="text-sm opacity-80 pt-1">{s}</div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="relative rounded-2xl p-6 text-center overflow-hidden"
        style={{ background: "linear-gradient(135deg, rgba(108,92,231,0.15), rgba(0,184,148,0.12))" }}>
        <div className="absolute inset-0 pointer-events-none"
          style={{ background: "radial-gradient(ellipse at center, rgba(108,92,231,0.2), transparent 70%)" }} />
        <div className="relative">
          <h3 className="text-lg font-bold">Pret a commencer ?</h3>
          <p className="text-sm opacity-60 mt-1 mb-4">Rejoignez des milliers d'utilisateurs qui font confiance a JessiKaPay</p>
          <button onClick={() => openTelegramLink(JESSIKAPAY_TG)}
            className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl text-base font-bold text-white animate-glow-multi active:scale-95"
            style={{ background: "linear-gradient(135deg, var(--accent), var(--success))" }}>
            Ouvrir JessiKaPay <Icon.Arrow size={18} />
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center opacity-30 text-[11px] space-y-0.5">
        <div>JessiKaPay — Transferts d'argent simplifies</div>
        <div>Propulse par JessiKa Group</div>
      </div>
    </div>
  );
}
