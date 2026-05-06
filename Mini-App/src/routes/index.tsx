import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { AnimatePresence, motion } from "framer-motion";
import { ParticlesBackground } from "@/components/ParticlesBackground";
import { BottomNav, type TabKey } from "@/components/BottomNav";
import { HomePage } from "@/pages/HomePage";
import { AccessPage } from "@/pages/AccessPage";
import { PremiumPage } from "@/pages/PremiumPage";
import { JessiKaPayPage } from "@/pages/JessiKaPayPage";
import { TonConnectProvider } from "@/components/TonConnectProvider";
import { initTelegram } from "@/utils/telegram";

export const Route = createFileRoute("/")({ component: App });

function App() {
  const [tab, setTab] = useState<TabKey>("home");
  useEffect(() => { initTelegram(); }, []);

  return (
    // TonConnectProvider englobe toute l'app pour que PremiumPage
    // puisse utiliser useTonConnectUI / useTonWallet
    <TonConnectProvider>
      <div
        className="relative min-h-screen"
        style={{ background: "var(--bg-primary)", color: "var(--text-primary)" }}
      >
        <ParticlesBackground />
        <main
          className="relative z-10 max-w-md mx-auto px-4 pt-5"
          style={{ paddingBottom: "calc(80px + env(safe-area-inset-bottom))" }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={tab}
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              transition={{ duration: 0.25 }}
            >
              {tab === "home" && <HomePage onNavigate={setTab} />}
              {tab === "access" && <AccessPage onNavigate={setTab} />}
              {tab === "premium" && <PremiumPage />}
              {tab === "jessikaPay" && <JessiKaPayPage />}
            </motion.div>
          </AnimatePresence>
        </main>
        <BottomNav active={tab} onChange={setTab} />
      </div>
    </TonConnectProvider>
  );
}
