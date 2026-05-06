export const ADSGRAM_BLOCK_ID = "YOUR_ADSGRAM_BLOCK_ID";
export const MONETAG_ZONE_ID = "10971920";
export const USDT_WALLET = "TTaDZGdMoZJtqrj1sxGEkd8wqfDVQXXt14";
export const SUPPORT_TG = "https://t.me/JessiKaSearchBot";
export const JESSIKAPAY_TG = "https://t.me/JessiKaPayBot";

export type PlanKey = "free" | "bronze" | "argent" | "or" | "platine" | "diamant" | "adamantide";

export const PLAN_COLORS: Record<PlanKey, string> = {
  free: "#8a8a9a",
  bronze: "#cd7f32",
  argent: "#c0c0c0",
  or: "#f9ca24",
  platine: "#e5e4e2",
  diamant: "#b9f2ff",
  adamantide: "#ff6b6b",
};

export const PLAN_LABELS: Record<PlanKey, string> = {
  free: "Gratuit",
  bronze: "Bronze",
  argent: "Argent",
  or: "Or",
  platine: "Platine",
  diamant: "Diamant",
  adamantide: "Adamantide",
};

export interface PremiumPlan {
  key: Exclude<PlanKey, "free">;
  duration: string;
  days: number;
  fcfa: string;
  cdf: string;
  usd: number;
  badge?: "popular" | "best";
}

export const PREMIUM_PLANS: PremiumPlan[] = [
  { key: "bronze", duration: "7 jours", days: 7, fcfa: "520", cdf: "2 500", usd: 0.94 },
  { key: "argent", duration: "30 jours", days: 30, fcfa: "2 100", cdf: "8 800", usd: 3.8 },
  { key: "or", duration: "60 jours", days: 60, fcfa: "4 200", cdf: "17 600", usd: 7.5, badge: "popular" },
  { key: "platine", duration: "90 jours", days: 90, fcfa: "6 300", cdf: "26 400", usd: 11 },
  { key: "diamant", duration: "180 jours", days: 180, fcfa: "12 600", cdf: "52 800", usd: 22, badge: "best" },
  { key: "adamantide", duration: "365 jours", days: 365, fcfa: "25 200", cdf: "105 500", usd: 45.2 },
];
