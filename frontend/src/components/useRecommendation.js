import { useCallback, useState } from "react";
import { recommendBudget } from "../services/api";

export default function useRecommendation() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [warming, setWarming] = useState(false);
  const [error, setError] = useState(null);

  const run = useCallback(async (params) => {
    setLoading(true);
    setError(null);
    setWarming(false);
    try {
      setData(await recommendBudget(params, { onRetry: () => setWarming(true) }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
      setWarming(false);
    }
  }, []);

  return { data, loading, warming, error, run, setWarming };
}
