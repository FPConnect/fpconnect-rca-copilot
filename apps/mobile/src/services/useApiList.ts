import { useCallback, useEffect, useState } from "react";
import { ApiError } from "./api";
import { fetchList } from "./lists";
import { useSession } from "./SessionProvider";

export function useApiList<T>(path: string, validate: (value: unknown) => value is T) {
  const { client, expire } = useSession();
  const [data, setData] = useState<T[] | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const reload = useCallback(async () => {
    setLoading(true);
    setError("");
    setData(null);
    try {
      const result = await fetchList(path, client, validate);
      setData(result);
    } catch (e) {
      setData(null);
      if (e instanceof ApiError && e.status === 401) await expire();
      else setError(e instanceof ApiError ? e.message : "Could not load data.");
    } finally { setLoading(false); }
  }, [path, client, validate]);
  useEffect(() => { void reload(); }, [reload]);
  return { data, error, loading, reload };
}
