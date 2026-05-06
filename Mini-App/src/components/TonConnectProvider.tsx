/**
 * TonConnectProvider
 * ------------------
 * Wraps the entire app with the TonConnect context.
 * The manifestUrl must point to a valid tonconnect-manifest.json hosted
 * at the root of the Mini App domain.
 *
 * Example manifest (public/tonconnect-manifest.json) :
 * {
 *   "url": "https://your-miniapp.com",
 *   "name": "JessiKaSearch",
 *   "iconUrl": "https://your-miniapp.com/icon-192.png"
 * }
 */
import { TonConnectUIProvider } from "@tonconnect/ui-react";

const MANIFEST_URL =
  import.meta.env.VITE_TONCONNECT_MANIFEST_URL ??
  `${typeof window !== "undefined" ? window.location.origin : ""}/tonconnect-manifest.json`;

export function TonConnectProvider({ children }: { children: React.ReactNode }) {
  return (
    <TonConnectUIProvider manifestUrl={MANIFEST_URL}>
      {children}
    </TonConnectUIProvider>
  );
}
