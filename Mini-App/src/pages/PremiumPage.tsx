import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  TonConnectButton,
  useTonConnectUI,
  useTonWallet,
} from "@tonconnect/ui-react";
import { Icon } from "@/components/Icons";
import { useUserData, formatRemaining } from "@/hooks/useUserData";
import { useTonPrice } from "@/hooks/useTonPrice";
import {
  PLAN_COLORS,
  PLAN_LABELS,
  PREMIUM_PLANS,
  USDT_WALLET,
  SUPPORT_TG,
  type PremiumPlan,
} from "@/utils/constants";
import { openTelegramLink, hapticFeedback, sendData } from "@/utils/telegram";
import { Faq } from "./AccessPage";

// ── Adresse TON qui reçoit les paiements ──────────────────────────────────────
// Même adresse que USDT_WALLET (format TON friendly address)
// Remplacer par l'adresse réelle dans constants.ts → TON_WALLET
const TON_WALLET_ADDRESS = import.meta.env.VITE_TON_WALLET ?? USDT_WALLET;

// ── BottomSheet ────────────────────────────────────────────────────────────────

function BottomSheet({
  open,
  onClose,
  children,
}: {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[60]"
            style={{ background: "rgba(0,0,0,0.6)" }}
            onClick={onClose}
          />
          <motion.div
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed left-0 right-0 bottom-0 z-[70] p-6 rounded-t-3xl"
            style={{
              background: "var(--bg-secondary)",
              paddingBottom: "calc(24px + env(safe-area-inset-bottom))",
            }}
          >
            <div
              className="w-10 h-1 rounded-full mx-auto mb-4"
              style={{ background: "rgba(255,255,255,0.15)" }}
            />
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// ── TonPaymentSheet ────────────────────────────────────────────────────────────

function TonPaymentSheet({
  plan,
  onClose,
}: {
  plan: PremiumPlan;
  onClose: () => void;
}) {
  const [tonConnectUI] = useTonConnectUI();
  const wallet = useTonWallet();
  const { price, loading: priceLoading, error: priceError, usdToTon, usdToNanoton } = useTonPrice();
  const [status, setStatus] = useState<"idle" | "pending" | "success" | "error">("idle");
  const [txHash, setTxHash] = useState<string | null>(null);

  const tonAmount = usdToTon(plan.usd);
  const nanoAmount = usdToNanoton(plan.usd);

  const handlePay = async () => {
    if (!wallet) {
      // Pas encore connecté — ouvrir le modal de connexion
      await tonConnectUI.openModal();
      return;
    }
    if (!nanoAmount) return;

    setStatus("pending");
    hapticFeedback("impact", "medium");

    try {
      // Payload encodé en base64 : identifie le plan acheté côté bot
      const payloadStr = JSON.stringify({
        action: "premium_purchase",
        plan: plan.key,
        days: plan.days,
      });
      const payloadB64 = btoa(payloadStr);

      const result = await tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 300, // 5 min
        messages: [
          {
            address: TON_WALLET_ADDRESS,
            amount: nanoAmount.toString(),
            // payload optionnel : commentaire lisible dans l'explorateur
            payload: payloadB64,
          },
        ],
      });

      const hash = result.boc; // boc = identifiant de la transaction
      setTxHash(hash);
      setStatus("success");
      hapticFeedback("notification", "success");

      // Notifier le bot via WebApp.sendData pour activation immédiate
      sendData({
        action: "ton_payment",
        plan: plan.key,
        days: plan.days,
        tx_boc: hash,
        amount_nano: nanoAmount.toString(),
        amount_ton: tonAmount?.toFixed(4),
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      console.error("[TonPay] error:", msg);
      // Annulation par l'utilisateur → ne pas afficher erreur
      if (msg.includes("User rejects") || msg.includes("cancel")) {
        setStatus("idle");
      } else {
        setStatus("error");
        hapticFeedback("notification", "error");
      }
    }
  };

  const color = PLAN_COLORS[plan.key];

  if (status === "success") {
    return (
      <div className="space-y-4 text-center">
        <div className="text-4xl">🎉</div>
        <h3 className="text-lg font-bold text-green-400">Paiement envoyé !</h3>
        <p className="text-sm opacity-60">
          Votre plan <span style={{ color }}>{PLAN_LABELS[plan.key]}</span> sera
          activé dans quelques secondes après confirmation de la blockchain.
        </p>
        {txHash && (
          <div
            className="font-mono text-[9px] break-all p-2 rounded-xl"
            style={{ background: "rgba(255,255,255,0.04)" }}
          >
            TX: {txHash.slice(0, 60)}…
          </div>
        )}
        <button
          onClick={onClose}
          className="w-full py-3 rounded-xl font-semibold text-sm text-white"
          style={{ background: "var(--success)" }}
        >
          Fermer
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold">Payer avec TON</h3>
        {/* Bouton natif TON Connect (affiche avatar + adresse si connecté) */}
        <TonConnectButton />
      </div>

      {/* Résumé plan */}
      <div className="glass rounded-xl p-4 divide-y divide-white/[0.04]">
        {[
          ["Plan", <span style={{ color }}>{PLAN_LABELS[plan.key]}</span>],
          ["Durée", plan.duration],
          [
            "Prix USD",
            <span className="font-bold">{plan.usd.toFixed(2)} $</span>,
          ],
          [
            "Montant TON",
            priceLoading ? (
              <span className="opacity-50 text-xs">Chargement du taux…</span>
            ) : priceError ? (
              <span className="text-red-400 text-xs">Erreur taux</span>
            ) : (
              <span className="font-bold text-blue-300">
                {tonAmount?.toFixed(4)} TON
              </span>
            ),
          ],
          [
            "Taux actuel",
            priceLoading ? (
              "…"
            ) : price ? (
              <span className="opacity-60 text-xs">
                1 TON = {price.usd.toFixed(3)} $ · mis à jour{" "}
                {new Date(price.lastUpdated).toLocaleTimeString("fr-FR")}
              </span>
            ) : null,
          ],
        ].map(([l, v], i) => (
          <div key={i} className="flex justify-between py-2 text-sm">
            <span className="opacity-60">{l}</span>
            <span className="font-semibold">{v}</span>
          </div>
        ))}
      </div>

      {/* Avertissement si taux indisponible */}
      {priceError && (
        <div
          className="text-xs p-3 rounded-xl"
          style={{ background: "rgba(225,112,85,0.1)", color: "var(--error)" }}
        >
          Impossible de récupérer le taux TON/USD. Réessayez dans quelques
          secondes.
        </div>
      )}

      {/* Info wallet */}
      {!wallet && (
        <div
          className="text-xs p-3 rounded-xl text-center"
          style={{ background: "rgba(108,92,231,0.08)" }}
        >
          Connectez votre wallet TON pour continuer
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={onClose}
          className="flex-1 py-3 rounded-xl font-semibold text-sm"
          style={{ background: "rgba(255,255,255,0.06)" }}
        >
          Annuler
        </button>
        <button
          onClick={handlePay}
          disabled={status === "pending" || !!priceError || priceLoading}
          className="flex-1 py-3 rounded-xl font-semibold text-sm text-white animate-glow-pulse active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
          style={{ background: "var(--accent)" }}
        >
          {status === "pending" ? (
            <span className="flex items-center justify-center gap-2">
              <Icon.Spinner size={16} /> En cours…
            </span>
          ) : !wallet ? (
            "Connecter le wallet"
          ) : (
            `Payer ${tonAmount?.toFixed(4) ?? "…"} TON`
          )}
        </button>
      </div>
    </div>
  );
}

// ── PremiumPage ────────────────────────────────────────────────────────────────

const PLAN_ICONS = {
  bronze: Icon.Medal,
  argent: Icon.Medal,
  or: Icon.Medal,
  platine: Icon.Diamond,
  diamant: Icon.Diamond,
  adamantide: Icon.Flame,
} as const;

export function PremiumPage() {
  const { data } = useUserData();
  const [tonPlan, setTonPlan] = useState<PremiumPlan | null>(null);
  const [usdtPlan, setUsdtPlan] = useState<PremiumPlan | null>(null);

  // Prefetch le taux TON dès l'ouverture de la page
  const { price: tonPrice, usdToTon } = useTonPrice();

  if (!data) return null;

  const isPremium =
    data.plan !== "free" &&
    data.premiumExpiry &&
    new Date(data.premiumExpiry).getTime() > Date.now();

  return (
    <div className="space-y-5">
      {/* Plan actuel */}
      {isPremium && (
        <div
          className="rounded-2xl p-4"
          style={{
            background: `linear-gradient(135deg, ${PLAN_COLORS[data.plan]}33, ${PLAN_COLORS[data.plan]}0d)`,
            border: `1px solid ${PLAN_COLORS[data.plan]}40`,
          }}
        >
          <div className="flex justify-between">
            <div>
              <div className="text-xs opacity-50">Plan actuel</div>
              <div
                className="font-bold text-lg"
                style={{ color: PLAN_COLORS[data.plan] }}
              >
                {PLAN_LABELS[data.plan]}
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs opacity-50">Temps restant</div>
              <div
                className="font-bold text-lg"
                style={{ color: "var(--success)" }}
              >
                {formatRemaining(data.premiumExpiry)}
              </div>
            </div>
          </div>
          <div className="text-xs opacity-40 mt-2">
            Expire le{" "}
            {new Date(data.premiumExpiry!).toLocaleDateString("fr-FR")}
          </div>
        </div>
      )}

      <div className="text-center">
        <h2 className="text-xl font-bold">Plans Premium</h2>
        <p className="text-sm opacity-50 mt-1">Accès illimité sans publicité</p>
      </div>

      {/* Taux TON live */}
      {tonPrice && (
        <div
          className="flex items-center justify-center gap-2 text-xs py-2 px-4 rounded-full mx-auto w-fit"
          style={{ background: "rgba(0,136,204,0.1)", color: "#3da1d2" }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
          1 TON = {tonPrice.usd.toFixed(3)} $ · taux live CoinGecko
        </div>
      )}

      {/* Avantages */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-3">
          Avantages Premium
        </div>
        <div className="space-y-2.5">
          {[
            [Icon.CheckCircle, "Accès illimité à tous les fichiers"],
            [Icon.Shield, "Aucune publicité à regarder"],
            [Icon.Clock, "Session permanente pendant toute la durée du plan"],
            [Icon.Headset, "Support client prioritaire"],
            [Icon.Zap, "Téléchargements plus rapides"],
            [Icon.Star, "Badge exclusif sur votre profil"],
          ].map(([I, t], i) => {
            const C = I as typeof Icon.Star;
            return (
              <div key={i} className="flex items-center gap-3 text-sm">
                <C size={20} style={{ color: "var(--success)" }} />
                <span className="opacity-80">{t as string}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Cartes plans */}
      <div className="space-y-3">
        {PREMIUM_PLANS.map((p) => {
          const color = PLAN_COLORS[p.key];
          const PIcon = PLAN_ICONS[p.key];
          const tonAmt = usdToTon(p.usd);
          return (
            <div
              key={p.key}
              className="glass rounded-2xl p-4 relative"
              style={{ borderColor: `${color}1a` }}
            >
              {p.badge === "popular" && (
                <span
                  className="absolute top-3 right-3 px-2 py-0.5 rounded-full text-[11px] font-semibold animate-pulse"
                  style={{ background: `${color}26`, color }}
                >
                  Populaire
                </span>
              )}
              {p.badge === "best" && (
                <span
                  className="absolute top-3 right-3 px-2 py-0.5 rounded-full text-[11px] font-semibold"
                  style={{ background: `${color}26`, color }}
                >
                  Meilleur rapport
                </span>
              )}
              <div className="flex items-center gap-3 mb-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{ background: `${color}1a`, color }}
                >
                  <PIcon size={22} />
                </div>
                <div>
                  <div className="font-bold" style={{ color }}>
                    {PLAN_LABELS[p.key]}
                  </div>
                  <div className="text-xs opacity-50">{p.duration}</div>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mb-3">
                <span
                  className="px-2.5 py-1 rounded-full text-xs"
                  style={{ background: "rgba(255,255,255,0.04)" }}
                >
                  {p.fcfa} FCFA
                </span>
                <span
                  className="px-2.5 py-1 rounded-full text-xs"
                  style={{ background: "rgba(255,255,255,0.04)" }}
                >
                  {p.cdf} CDF
                </span>
                <span
                  className="px-2.5 py-1 rounded-full text-xs font-semibold"
                  style={{ background: "rgba(255,255,255,0.06)" }}
                >
                  {p.usd.toFixed(2)} $
                </span>
                {/* Prix TON live */}
                {tonAmt !== null && (
                  <span
                    className="px-2.5 py-1 rounded-full text-xs font-semibold"
                    style={{ background: "rgba(0,136,204,0.12)", color: "#3da1d2" }}
                  >
                    ≈ {tonAmt.toFixed(3)} TON
                  </span>
                )}
              </div>

              <div className="space-y-1.5 mb-3">
                {[
                  "Accès illimité aux fichiers",
                  "Aucune publicité",
                  "Session permanente",
                  "Support prioritaire",
                ].map((a, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 text-xs opacity-60"
                  >
                    <Icon.Check size={12} style={{ color: "var(--success)" }} />{" "}
                    {a}
                  </div>
                ))}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => {
                    hapticFeedback("impact", "light");
                    setTonPlan(p);
                  }}
                  className="flex-1 py-2.5 rounded-xl text-sm font-semibold flex items-center justify-center gap-1.5 active:scale-95"
                  style={{ background: `${color}26`, color }}
                >
                  <Icon.Diamond size={14} /> Payer avec TON
                </button>
                <button
                  onClick={() => {
                    hapticFeedback("impact", "light");
                    setUsdtPlan(p);
                  }}
                  className="flex-1 py-2.5 rounded-xl text-sm font-semibold flex items-center justify-center gap-1.5 active:scale-95"
                  style={{ background: "rgba(255,255,255,0.05)" }}
                >
                  <Icon.Dollar size={14} /> Payer en USDT
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Tableau comparatif */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-3">
          Comparer les plans
        </div>
        <table className="w-full text-xs">
          <thead>
            <tr className="opacity-50">
              <th className="text-left py-2">Plan</th>
              <th className="text-left">Durée</th>
              <th className="text-right">$/jour</th>
              <th className="text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {PREMIUM_PLANS.map((p) => (
              <tr
                key={p.key}
                className="border-t border-white/[0.04]"
                style={{
                  background:
                    p.key === "or" ? "rgba(108,92,231,0.05)" : undefined,
                }}
              >
                <td
                  className="py-2 font-semibold"
                  style={{ color: PLAN_COLORS[p.key] }}
                >
                  {PLAN_LABELS[p.key]}
                </td>
                <td className="opacity-70">{p.duration}</td>
                <td className="text-right opacity-70">
                  {(p.usd / p.days).toFixed(2)} $
                </td>
                <td className="text-right font-semibold">
                  {p.usd.toFixed(2)} $
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Money */}
      <div className="glass rounded-2xl p-4 text-center">
        <Icon.Phone
          size={32}
          className="mx-auto mb-2"
          style={{ color: "var(--accent-light)" }}
        />
        <div className="font-bold text-sm mb-2">Paiement Mobile Money</div>
        <div className="text-xs opacity-60 leading-relaxed mb-3">
          Pour payer via Orange Money, Wave, Flooz, M-Pesa ou tout autre moyen
          de paiement mobile, contactez notre équipe de support. Traitement
          manuel sous 24 heures.
        </div>
        <button
          onClick={() => openTelegramLink(SUPPORT_TG)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold active:scale-95"
          style={{
            background: "rgba(0,184,148,0.12)",
            color: "var(--success)",
          }}
        >
          <Icon.Chat size={16} /> Contacter le support
        </button>
      </div>

      {/* Garanties */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-3">
          Nos garanties
        </div>
        <div className="space-y-3">
          {[
            [
              Icon.ShieldCheck,
              "Paiement 100% sécurisé via la blockchain TON",
            ],
            [
              Icon.Refresh,
              "Activation instantanée après confirmation du paiement",
            ],
            [
              Icon.Headset,
              "Support disponible 7 jours sur 7 pour toute question",
            ],
          ].map(([I, t], i) => {
            const C = I as typeof Icon.Star;
            return (
              <div key={i} className="flex items-center gap-3 text-sm">
                <C size={20} style={{ color: "var(--accent-light)" }} />
                <span className="opacity-80">{t as string}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* FAQ */}
      <div className="glass rounded-2xl p-4">
        <div className="text-sm font-semibold opacity-70 mb-3">
          Questions fréquentes
        </div>
        <Faq
          items={[
            {
              q: "Comment fonctionne le paiement TON ?",
              a: "Après avoir cliqué sur Payer, votre wallet TON Connect s'ouvrira automatiquement. Le montant exact en TON est calculé en temps réel via le taux CoinGecko. Validez la transaction et votre plan sera activé dans quelques secondes.",
            },
            {
              q: "Le montant en TON est-il exact ?",
              a: "Oui. Le taux TON/USD est récupéré en temps réel depuis CoinGecko (avec CoinCap en secours). Le montant affiché est recalculé à chaque ouverture du formulaire de paiement.",
            },
            {
              q: "Le paiement USDT est-il automatique ?",
              a: "Non, le paiement USDT est manuel. Envoyez le montant exact à l'adresse indiquée, puis cliquez sur J'ai payé et contactez le support avec la preuve de transaction.",
            },
            {
              q: "Puis-je changer de plan en cours de route ?",
              a: "Oui, vous pouvez souscrire à un plan supérieur à tout moment. Le temps restant de votre plan actuel sera ajouté au nouveau plan.",
            },
            {
              q: "Que se passe-t-il si mon plan expire ?",
              a: "Votre accès reviendra au mode gratuit. Vous pourrez toujours utiliser les sessions gratuites en regardant des publicités.",
            },
          ]}
        />
      </div>

      {/* TON Sheet */}
      <BottomSheet open={!!tonPlan} onClose={() => setTonPlan(null)}>
        {tonPlan && (
          <TonPaymentSheet plan={tonPlan} onClose={() => setTonPlan(null)} />
        )}
      </BottomSheet>

      {/* USDT Sheet */}
      <BottomSheet open={!!usdtPlan} onClose={() => setUsdtPlan(null)}>
        {usdtPlan && (
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-center">Paiement USDT</h3>
            <div className="text-center">
              <div className="text-xs opacity-50">Envoyez exactement</div>
              <div
                className="text-2xl font-bold"
                style={{ color: "#26a17b" }}
              >
                {usdtPlan.usd.toFixed(2)} USDT
              </div>
              <div className="text-xs opacity-50 mt-1">
                sur le réseau TON à cette adresse :
              </div>
            </div>
            <div
              className="font-mono text-[10px] break-all p-3 rounded-xl"
              style={{ background: "rgba(255,255,255,0.04)" }}
            >
              {USDT_WALLET}
            </div>
            <button
              onClick={() => {
                navigator.clipboard?.writeText(USDT_WALLET);
                hapticFeedback("notification", "success");
              }}
              className="w-full py-2.5 rounded-xl text-sm font-semibold"
              style={{
                background: "rgba(108,92,231,0.12)",
                color: "var(--accent-light)",
              }}
            >
              Copier l'adresse
            </button>
            <div className="flex gap-2">
              <button
                onClick={() => setUsdtPlan(null)}
                className="flex-1 py-3 rounded-xl font-semibold text-sm"
                style={{ background: "rgba(255,255,255,0.06)" }}
              >
                Annuler
              </button>
              <button
                onClick={() => {
                  openTelegramLink(SUPPORT_TG);
                  setUsdtPlan(null);
                }}
                className="flex-1 py-3 rounded-xl font-semibold text-sm text-white"
                style={{ background: "#26a17b" }}
              >
                J'ai payé
              </button>
            </div>
          </div>
        )}
      </BottomSheet>
    </div>
  );
}
