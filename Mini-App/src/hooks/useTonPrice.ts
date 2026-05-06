import { useEffect, useState, useCallback } from "react";

interface TonPrice {
  usd: number;
  lastUpdated: Date;
}

// ── Taux TON/USD via CoinGecko (API publique, sans clé) ───────────────────────
// Fallback : CoinCap si CoinGecko échoue.
// IMPORTANT : toujours fetch avant d'afficher un montant TON.

const COINGECKO_URL =
  "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd";
const COINCAP_URL =
  "https://api.coincap.io/v2/assets/the-open-network";

async function fetchTonPriceFromCoinGecko(): Promise<number> {
  const res = await fetch(COINGECKO_URL);
  if (!res.ok) throw new Error(`CoinGecko ${res.status}`);
  const data = await res.json();
  const price = data?.["the-open-network"]?.usd;
  if (typeof price !== "number" || price <= 0) throw new Error("Price invalid");
  return price;
}

async function fetchTonPriceFromCoinCap(): Promise<number> {
  const res = await fetch(COINCAP_URL);
  if (!res.ok) throw new Error(`CoinCap ${res.status}`);
  const data = await res.json();
  const price = parseFloat(data?.data?.priceUsd ?? "0");
  if (!price || price <= 0) throw new Error("Price invalid");
  return price;
}

async function fetchTonPrice(): Promise<number> {
  try {
    return await fetchTonPriceFromCoinGecko();
  } catch {
    // Fallback CoinCap
    return await fetchTonPriceFromCoinCap();
  }
}

/**
 * Retourne le prix actuel du TON en USD.
 * Rafraîchi toutes les 60 secondes.
 * usdToTon(amount) : convertit un montant USD en TON.
 */
export function useTonPrice() {
  const [price, setPrice] = useState<TonPrice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const usd = await fetchTonPrice();
      setPrice({ usd, lastUpdated: new Date() });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      console.error("[useTonPrice] failed:", msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    // Rafraîchissement automatique toutes les 60s
    const interval = setInterval(load, 60_000);
    return () => clearInterval(interval);
  }, [load]);

  /**
   * Convertit un montant USD en TON avec le taux actuel.
   * Retourne null si le taux n'est pas encore chargé.
   */
  const usdToTon = useCallback(
    (usdAmount: number): number | null => {
      if (!price || price.usd <= 0) return null;
      return usdAmount / price.usd;
    },
    [price]
  );

  /**
   * Montant TON en nanotons (unité utilisée par TON Connect).
   * 1 TON = 1_000_000_000 nanotons.
   */
  const usdToNanoton = useCallback(
    (usdAmount: number): bigint | null => {
      const ton = usdToTon(usdAmount);
      if (ton === null) return null;
      return BigInt(Math.round(ton * 1_000_000_000));
    },
    [usdToTon]
  );

  return { price, loading, error, usdToTon, usdToNanoton, refresh: load };
}
