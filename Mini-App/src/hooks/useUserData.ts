import { useEffect, useState, useCallback } from "react";
import type { PlanKey } from "@/utils/constants";

export interface UserData {
  plan: PlanKey;
  premiumExpiry: string | null;
  sessionExpiry: string | null;
  totalSearches: number;
  weekSearches: number;
  dailySearches: number[];
  recentSearches: { query: string; timestamp: string }[];
}

// ── Helpers Telegram ───────────────────────────────────────────────────────────

function getTelegramInitData(): string {
  return typeof window !== "undefined"
    ? window.Telegram?.WebApp?.initData ?? ""
    : "";
}

// URL de base de l'API bot — définie dans .env
// Ex: VITE_BOT_API_URL=https://ton-bot.koyeb.app
const BOT_API_BASE =
  import.meta.env.VITE_BOT_API_URL ??
  "https://experienced-marnie-imbd-db361783.koyeb.app";

// ── Fetch données utilisateur depuis le bot ────────────────────────────────────

async function fetchUserData(): Promise<UserData> {
  const initData = getTelegramInitData();
  if (!initData) {
    throw new Error(
      "initData Telegram manquant — ouvrez la Mini-App depuis Telegram"
    );
  }
  const res = await fetch(`${BOT_API_BASE}/api/user/me`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": initData,
    },
  });
  if (!res.ok) {
    const err = await res.text().catch(() => "Erreur inconnue");
    throw new Error(`API error ${res.status}: ${err}`);
  }
  return (await res.json()) as UserData;
}

// ── Activer session côté bot après pub visionnée ──────────────────────────────

async function activateSessionOnBot(): Promise<void> {
  const initData = getTelegramInitData();
  if (!initData) return;
  const res = await fetch(`${BOT_API_BASE}/api/session/activate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": initData,
    },
  });
  if (!res.ok) {
    const err = await res.text().catch(() => "");
    throw new Error(`Session activate error ${res.status}: ${err}`);
  }
}

// ── Notifier le bot (paiements, actions) sans fermer la Mini-App ──────────────

export async function notifyBot(payload: unknown): Promise<void> {
  const initData = getTelegramInitData();
  if (!initData) return;
  try {
    await fetch(`${BOT_API_BASE}/api/notify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-Init-Data": initData,
      },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    console.error("[notifyBot] failed:", e);
  }
}

// ── Hook principal ─────────────────────────────────────────────────────────────

export function useUserData() {
  const [data, setData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const d = await fetchUserData();
      setData(d);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      console.error("[useUserData] fetch failed:", msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  /**
   * Appelle le bot pour enregistrer la session + mise à jour optimiste locale.
   * NE ferme PAS la Mini-App.
   */
  const activateSession = useCallback(async () => {
    // 1. Mise à jour optimiste IMMÉDIATE — l'UI bascule sur "session active" instantanément
    const expiry = new Date(Date.now() + 3_600_000).toISOString();
    setData((d) => (d ? { ...d, sessionExpiry: expiry } : d));

    // 2. Appel API bot en arrière-plan pour persister en base
    try {
      await activateSessionOnBot();
      // ✅ Succès — NE PAS appeler load() ici : ça écraserait l'optimistic update
      // si le bot répond avec sessionExpiry null (délai réseau, etc.)
    } catch (e) {
      console.error("[activateSession] failed to notify bot:", e);
      // En cas d'erreur réseau, on recharge après 5s pour synchroniser
      setTimeout(() => load(), 5000);
    }
  }, [load]);

  /** Recharge depuis le bot */
  const refresh = useCallback(() => {
    load();
  }, [load]);

  return { data, loading, error, activateSession, refresh, setData };
}

// ── Formatters ─────────────────────────────────────────────────────────────────

export function formatRelative(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const d = Math.floor(diff / 86_400_000);
  const h = Math.floor(diff / 3_600_000);
  const m = Math.floor(diff / 60_000);
  if (d >= 1) return `il y a ${d}j`;
  if (h >= 1) return `il y a ${h}h`;
  return `il y a ${m}min`;
}

export function formatRemaining(iso: string | null): string {
  if (!iso) return "Aucun";
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return "Expiré";
  const d = Math.floor(diff / 86_400_000);
  const h = Math.floor((diff % 86_400_000) / 3_600_000);
  const m = Math.floor((diff % 3_600_000) / 60_000);
  const s = Math.floor((diff % 60_000) / 1_000);
  if (d > 0) return `${d}j ${h}h ${m}min`;
  if (h > 0) return `${h}h ${m}min`;
  return `${m}min ${s}s`;
}
