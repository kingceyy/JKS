import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip } from "chart.js";
import { Icon } from "@/components/Icons";
import { useUserData, formatRelative, formatRemaining } from "@/hooks/useUserData";
import { getTelegramUser } from "@/utils/telegram";
import { PLAN_COLORS, PLAN_LABELS } from "@/utils/constants";
import type { TabKey } from "@/components/BottomNav";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip);

function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`skeleton ${className}`} />;
}

export function HomePage({ onNavigate }: { onNavigate: (k: TabKey) => void }) {
  const { data, loading } = useUserData();
  const user = getTelegramUser();
  const [, force] = useState(0);
  useEffect(() => { const t = setInterval(() => force((x) => x + 1), 1000); return () => clearInterval(t); }, []);

  if (loading || !data) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-20" />
        <div className="grid grid-cols-2 gap-3">
          {[0,1,2,3].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-52" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  const planColor = PLAN_COLORS[data.plan];
  const sessionActive = data.sessionExpiry && new Date(data.sessionExpiry).getTime() > Date.now();
  const initials = user.firstName.charAt(0).toUpperCase();

  const stats = [
    { label: "Recherches totales", value: data.totalSearches.toString(), Icon: Icon.Search },
    { label: "Cette semaine", value: data.weekSearches.toString(), Icon: Icon.Bars },
    { label: "Plan actuel", value: PLAN_LABELS[data.plan], Icon: Icon.Star },
    { label: "Temps restant", value: formatRemaining(data.sessionExpiry), Icon: Icon.Hourglass, success: !!sessionActive },
  ];

  const chartData = {
    labels: ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"],
    datasets: [{
      data: data.dailySearches,
      borderColor: "#00b894",
      backgroundColor: "rgba(0,184,148,0.08)",
      fill: true, tension: 0.4, borderWidth: 2,
      pointRadius: 4, pointBackgroundColor: "#00b894",
      pointBorderColor: "#0f0f1a", pointBorderWidth: 2,
    }],
  };
  const chartOpts = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { backgroundColor: "rgba(0,0,0,0.8)" } },
    scales: {
      y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.03)" }, ticks: { color: "rgba(255,255,255,0.35)", font: { size: 11 }, precision: 0 } },
      x: { grid: { color: "rgba(255,255,255,0.03)" }, ticks: { color: "rgba(255,255,255,0.35)", font: { size: 11 } } },
    },
  } as const;

  return (
    <div className="space-y-4">
      {/* Profile */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-4">
        <div className="relative">
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center font-bold text-xl"
            style={{
              border: `2.5px solid ${planColor}`,
              background: `radial-gradient(circle, ${planColor}33, transparent)`,
              color: planColor,
            }}
          >
            {user.photoUrl ? <img src={user.photoUrl} alt="" className="w-full h-full rounded-full object-cover" /> : initials}
          </div>
          <div
            className="absolute -bottom-0.5 -right-0.5 w-5 h-5 rounded-full flex items-center justify-center border-2"
            style={{ background: sessionActive ? "var(--success)" : "#5a5a6a", borderColor: "var(--bg-primary)" }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-white" />
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-bold text-lg truncate">{user.firstName} {user.lastName ?? ""}</div>
          <div className="text-sm opacity-50 truncate">@{user.username ?? "user"}</div>
          <span
            className="inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-semibold"
            style={{ background: `${planColor}33`, color: planColor }}
          >{PLAN_LABELS[data.plan]}</span>
        </div>
      </motion.div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08, type: "spring", stiffness: 200, damping: 20 }}
            className="glass rounded-2xl p-3.5 relative overflow-hidden"
          >
            <s.Icon size={40} className="absolute top-2 right-2 opacity-5" />
            <div className="text-xs opacity-50">{s.label}</div>
            <div className="text-xl font-bold mt-1" style={{ color: s.success ? "var(--success)" : undefined }}>{s.value}</div>
          </motion.div>
        ))}
      </div>

      {/* Chart */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-3">Activite de recherche</div>
        <div style={{ height: 180 }}><Line data={chartData} options={chartOpts} /></div>
      </div>

      {/* Recent */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-2">Recherches recentes</div>
        <div className="space-y-1">
          {data.recentSearches.map((r, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="flex items-center gap-3 py-2.5 px-2 rounded-xl hover:bg-white/[0.04]"
            >
              <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ background: "rgba(108,92,231,0.12)", color: "var(--accent-light)" }}>
                <Icon.Search size={16} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm truncate">{r.query}</div>
                <div className="text-xs opacity-40 mt-0.5">{formatRelative(r.timestamp)}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Detailed */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-3">Votre historique en chiffres</div>
        <div className="divide-y divide-white/[0.04]">
          {[
            { l: "Recherches aujourd'hui", v: "5" },
            { l: "Moyenne par jour", v: "8.2" },
            { l: "Recherche la plus frequente", v: <span className="italic">one piece</span> },
          ].map((row, i) => (
            <div key={i} className="flex justify-between py-2.5 text-sm">
              <span className="opacity-60">{row.l}</span>
              <span className="font-semibold">{row.v}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Access banner */}
      {!sessionActive && (
        <div
          className="rounded-2xl p-4 text-center"
          style={{ background: "linear-gradient(135deg, rgba(108,92,231,0.12), rgba(0,184,148,0.08))", border: "1px solid var(--border-subtle)" }}
        >
          <div className="text-sm opacity-80 mb-3">Vous n'avez pas de session active. Regardez une publicite pour obtenir 1 heure d'acces gratuit.</div>
          <button
            onClick={() => onNavigate("access")}
            className="px-6 py-2.5 rounded-xl font-semibold text-white animate-glow-pulse active:scale-95"
            style={{ background: "var(--accent)" }}
          >Obtenir un acces</button>
        </div>
      )}

      {/* Tips */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-3">Astuces pour mieux chercher</div>
        <div className="space-y-3">
          {[
            "Utilisez des mots-cles precis pour des resultats plus rapides",
            "Essayez les noms en version originale (VO) et en version francaise (VF)",
            "Ajoutez l'annee pour filtrer les resultats (ex: spider-man 2023)",
            "Souscrivez a un plan premium pour un acces illimite sans interruption",
          ].map((tip, i) => (
            <div key={i} className="flex gap-3 items-start">
              <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0" style={{ background: "rgba(108,92,231,0.15)", color: "var(--accent-light)" }}>{i+1}</div>
              <div className="text-sm opacity-80">{tip}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
