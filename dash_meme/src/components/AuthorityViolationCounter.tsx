import { useQuery } from "@tanstack/react-query";
import { fetchSecurityEvents } from "@/api/signals";

export function AuthorityViolationCounter() {
  const { data } = useQuery({
    queryKey: ["security-events"],
    queryFn: ({ signal }: { signal?: AbortSignal }) => fetchSecurityEvents(signal),
    refetchInterval: 5000,
  });

  const violationCount = data?.total ?? 0;
  const hasViolations = violationCount > 0;

  return (
    <span
      className={`flex items-center gap-1.5 rounded border px-2.5 py-1 font-mono text-[11px] uppercase tracking-wider ${
        hasViolations
          ? "text-danger bg-danger/10 border-danger/40 animate-pulse"
          : "text-ok bg-ok/10 border-ok/40"
      }`}
    >
      <span className="font-semibold">AV:</span>
      <span>{violationCount}</span>
    </span>
  );
}
