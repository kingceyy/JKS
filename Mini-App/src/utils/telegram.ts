/* eslint-disable @typescript-eslint/no-explicit-any */
declare global {
  interface Window {
    Telegram?: { WebApp?: any };
    show_interstitial?: (zone: string) => Promise<void>;
    Adsgram?: { init: (opts: { blockId: string }) => { show: () => Promise<void> } };
  }
}

const tg = () => (typeof window !== "undefined" ? window.Telegram?.WebApp : undefined);

export function initTelegram() {
  const w = tg();
  if (!w) return;
  try {
    w.ready?.();
    w.expand?.();
    w.setHeaderColor?.("#0f0f1a");
    w.setBackgroundColor?.("#0f0f1a");
    w.disableVerticalSwipes?.();
  } catch {}
}

export interface TgUser {
  id: number;
  firstName: string;
  lastName?: string;
  username?: string;
  photoUrl?: string | null;
  languageCode?: string;
}

export function getTelegramUser(): TgUser {
  const u = tg()?.initDataUnsafe?.user;
  if (u) {
    return {
      id: u.id,
      firstName: u.first_name,
      lastName: u.last_name,
      username: u.username,
      photoUrl: u.photo_url ?? null,
      languageCode: u.language_code,
    };
  }
  return {
    id: 123456789,
    firstName: "Utilisateur",
    lastName: "Test",
    username: "test_user",
    photoUrl: null,
    languageCode: "fr",
  };
}

export function hapticFeedback(type: "impact" | "notification" | "selection", style?: string) {
  const hf = tg()?.HapticFeedback;
  if (!hf) return;
  try {
    if (type === "impact") hf.impactOccurred(style ?? "medium");
    else if (type === "notification") hf.notificationOccurred(style ?? "success");
    else hf.selectionChanged();
  } catch {}
}

export function sendData(data: unknown) {
  try { tg()?.sendData?.(JSON.stringify(data)); } catch {}
}

export function openTelegramLink(url: string) {
  const w = tg();
  if (w?.openTelegramLink) { try { w.openTelegramLink(url); return; } catch {} }
  if (typeof window !== "undefined") window.open(url, "_blank");
}
