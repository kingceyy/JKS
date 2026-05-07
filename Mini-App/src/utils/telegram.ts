/* eslint-disable @typescript-eslint/no-explicit-any */
declare global {
  interface Window {
    Telegram?: { WebApp?: any };
    // Monetag — le nom de la fonction dépend de la zone, ex: show_10971920
    show_10971920?: () => Promise<void>;
    Adsgram?: {
      init: (opts: { blockId: string; debug?: boolean }) => {
        show: () => Promise<any>;
        destroy: () => void;
      };
    };
  }
}

const tg = () =>
  typeof window !== "undefined" ? window.Telegram?.WebApp : undefined;

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
  // Fallback pour dev hors Telegram
  return {
    id: 123456789,
    firstName: "Utilisateur",
    lastName: "Test",
    username: "test_user",
    photoUrl: null,
    languageCode: "fr",
  };
}

export function hapticFeedback(
  type: "impact" | "notification" | "selection",
  style?: string
) {
  const hf = tg()?.HapticFeedback;
  if (!hf) return;
  try {
    if (type === "impact") hf.impactOccurred(style ?? "medium");
    else if (type === "notification") hf.notificationOccurred(style ?? "success");
    else hf.selectionChanged();
  } catch {}
}

// ⚠️ sendData() — WebApp.sendData() ferme automatiquement la Mini-App.
// Elle est conservée pour la compatibilité des imports mais ne fait RIEN.
// Utilisez notifyBot() depuis useUserData.ts pour notifier le bot.
export function sendData(_data: unknown) {
  // Intentionnellement vide — voir notifyBot() dans useUserData.ts
}

export function openTelegramLink(url: string) {
  const w = tg();
  if (w?.openTelegramLink) {
    try {
      w.openTelegramLink(url);
      return;
    } catch {}
  }
  if (typeof window !== "undefined") window.open(url, "_blank");
}
