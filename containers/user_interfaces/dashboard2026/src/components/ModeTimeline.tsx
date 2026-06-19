import { useQuery } from "@tanstack/react-query";
import { fetchModeTimeline, type ModeTransition } from "@/api/signals";

export function ModeTimeline() {
  const query = useQuery({
    queryKey: ["mode-timeline"],
    queryFn: () => fetchModeTimeline(),
    refetchInterval: 10000,
  });

  const data = query.data;
  const timeline = data?.timeline ?? [];
  const recentTransitions = timeline.slice(0, 5);

  if (recentTransitions.length === 0) {
    return (
      <div className="flex items-center gap-1.5 rounded border border-border bg-surface px-2.5 py-1 font-mono text-[11px] uppercase tracking-wider text-slate-400">
        <span className="font-semibold">Timeline:</span>
        <span>No transitions</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5 rounded border border-border bg-surface px-2.5 py-1 font-mono text-[11px] uppercase tracking-wider">
      <span className="font-semibold text-slate-400">Timeline:</span>
      {recentTransitions.map((transition: ModeTransition, idx: number) => (
        <span key={transition.ts_utc} className="flex items-center">
          {idx > 0 && <span className="mx-1 text-slate-500">→</span>}
          <span className="text-accent">{transition.to_mode}</span>
        </span>
      ))}
    </div>
  );
}
