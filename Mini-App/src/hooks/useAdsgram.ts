import { useCallback, useEffect, useRef } from "react";

export interface ShowPromiseResult {
  done: boolean;
  description: string;
  state: "load" | "render" | "playing" | "destroy";
  error: boolean;
}

interface AdController {
  show: () => Promise<ShowPromiseResult>;
  destroy: () => void;
}

interface UseAdsgramParams {
  blockId: string;
  onReward: () => void;
  onError?: (result: ShowPromiseResult) => void;
}

export function useAdsgram({ blockId, onReward, onError }: UseAdsgramParams): () => Promise<void> {
  const AdControllerRef = useRef<AdController | undefined>(undefined);

  useEffect(() => {
    // Initialise le controller dès que le script AdsGram est prêt
    AdControllerRef.current = window.Adsgram?.init({ blockId });
  }, [blockId]);

  return useCallback(async () => {
    if (!AdControllerRef.current) {
      onError?.({
        error: true,
        done: false,
        state: "load",
        description: "AdsGram SDK non chargé — vérifiez le script dans index.html",
      });
      return;
    }
    try {
      await AdControllerRef.current.show();
      // L'utilisateur a regardé la pub jusqu'à la fin
      onReward();
    } catch (result) {
      // Erreur ou pub fermée avant la fin (format Reward uniquement)
      onError?.(result as ShowPromiseResult);
    }
  }, [onError, onReward]);
}
