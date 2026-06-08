import { useEffect, useState } from "react";

import { CheckCircle2, XCircle, AlertTriangle, Shield, Gauge } from "lucide-react";

import { useCognitiveStream } from "@/state/cognitive_realtime";

interface InvariantRecord {
  id: string;
  status: "COMPLIANT" | "WARNING" | "VIOLATION" | "UNKNOWN";
  last_check: string;
  violation_count?: number;
  last_violation?: string;
  enforcement_level: "AUTO" | "YAML" | "CODE" | "REVIEW" | "DRIFT-KILLER";
}

const SEED_INVARIANTS: InvariantRecord[] = [
  { id: "INV-DIX-01", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "REVIEW" },
  { id: "INV-DIX-02", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "CODE" },
  { id: "INV-DIX-03", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "CODE" },
  { id: "INV-DIX-04", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "CODE" },
  { id: "INV-DIX-05", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "DRIFT-KILLER" },
  { id: "INV-DIX-06", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "CODE" },
  { id: "INV-DIX-07", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "CODE" },
  { id: "INV-DIX-08", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "CODE" },
  { id: "INV-DIX-09", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "CODE" },
  { id: "INV-DIX-10", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "CODE" },
  { id: "INV-DIX-11", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "REVIEW" },
  { id: "INV-DIX-12", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "CODE" },
  { id: "INV-DIX-13", status: "COMPLIANT", last_check: "20:14:02", enforcement_level: "DRIFT-KILLER" },
];

const ENFORCEMENT_ORDER: Record<string, number> = {
  "AUTO": 1,
  "YAML": 2,
  "CODE": 3,
  "DRIFT-KILLER": 4,
  "REVIEW": 5,
};

const STATUS_COLOR: Record<string, string> = {
  COMPLIANT: "text-emerald-400",
  WARNING: "text-amber-400",
  VIOLATION: "text-rose-400",
  UNKNOWN: "text-slate-500",
};

const STATUS_ICON: Record<string, typeof CheckCircle2> = {
  COMPLIANT: CheckCircle2,
  WARNING: AlertTriangle,
  VIOLATION: XCircle,
  UNKNOWN: Shield,
};

export function InvariantComplianceDashboard() {
  const [invariants, setInvariants] = useState<InvariantRecord[]>(SEED_INVARIANTS);
  const [filter, setFilter] = useState<"ALL" | "VIOLATIONS">("ALL");

  // Stream compliance updates from the governance layer
  const { events, live } = useCognitiveStream<Record<string, unknown>>("dyon", 1000);

  useEffect(() => {
    if (events.length === 0) return;
    const latest = events[events.length - 1];
    const payload = (latest.payload ?? {}) as Record<string, unknown>;
    const invariantUpdate = payload.invariant as InvariantRecord | undefined;
    if (invariantUpdate) {
      setInvariants((prev) =>
        prev.map((inv) =>
          inv.id === invariantUpdate.id ? { ...inv, ...invariantUpdate } : inv,
        ),
      );
    }
  }, [events]);

  const visible = filter === "ALL" ? invariants : invariants.filter((inv) => inv.status !== "COMPLIANT");

  const compliantCount = invariants.filter((inv) => inv.status === "COMPLIANT").length;
  const warningCount = invariants.filter((inv) => inv.status === "WARNING").length;
  const violationCount = invariants.filter((inv) => inv.status === "VIOLATION").length;

  const sortedVisible = [...visible].sort(
    (a, b) => (ENFORCEMENT_ORDER[a.enforcement_level] ?? 99) - (ENFORCEMENT_ORDER[b.enforcement_level] ?? 99),
  );

  return (
    <section className="flex h-full flex-col rounded border border-border bg-surface">
      <header className="flex items-baseline justify-between border-b border-border px-3 py-2">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Invariant Compliance
          </h3>
          <p className="mt-0.5 text-[11px] text-slate-500">
            EPIC-001 Architectural Constitution status
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Shield className={`h-4 w-4 ${live ? "text-emerald-400" : "text-slate-600"}`} />
          <span className="font-mono text-[10px] text-slate-400">
            {compliantCount}/{invariants.length} compliant
          </span>
          {warningCount > 0 && (
            <span className="font-mono text-[10px] text-amber-400">
              {warningCount} warnings
            </span>
          )}
          {violationCount > 0 && (
            <span className="font-mono text-[10px] text-rose-400">
              {violationCount} violations
            </span>
          )}
        </div>
      </header>

      {/* Summary bar */}
      <div className="border-b border-border/60 bg-bg/30 px-3 py-2">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="h-3 w-3 text-emerald-400" />
            <span className="font-mono text-[10px] text-slate-300">COMPLIANT ({compliantCount})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <AlertTriangle className="h-3 w-3 text-amber-400" />
            <span className="font-mono text-[10px] text-slate-300">WARNING ({warningCount})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <XCircle className="h-3 w-3 text-rose-400" />
            <span className="font-mono text-[10px] text-slate-300">VIOLATION ({violationCount})</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Gauge className="h-3 w-4 text-violet-400" />
            <span className="font-mono text-[10px] text-slate-400">
              Registry: contracts/ownership_registry.yaml
            </span>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-1 border-b border-border/60 bg-bg/50 px-2 py-1.5">
        {(["ALL", "VIOLATIONS"] as const).map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => setFilter(k)}
            className={`rounded border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider ${
              filter === k
                ? "border-accent/40 bg-accent/10 text-accent"
                : "border-border bg-bg/40 text-slate-500 hover:text-slate-300"
            }`}
          >
            {k === "ALL" ? "All" : "Violations Only"}
          </button>
        ))}
      </div>

      {/* Invariant list */}
      <div className="flex-1 overflow-auto divide-y divide-border/40">
        {sortedVisible.map((inv) => {
          const Icon = STATUS_ICON[inv.status];
          return (
            <div key={inv.id} className="flex items-center gap-2 px-3 py-2">
              <Icon className={`h-4 w-4 flex-shrink-0 ${STATUS_COLOR[inv.status]}`} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-[11px] text-slate-200">{inv.id}</span>
                  <span className="font-mono text-[10px] text-slate-500">{inv.last_check}</span>
                </div>
                <div className="mt-0.5 flex items-center gap-1.5">
                  <span
                    className={`font-mono text-[10px] uppercase ${STATUS_COLOR[inv.status]}`}
                  >
                    {inv.status}
                  </span>
                  <span className="font-mono text-[10px] text-slate-600">
                    {inv.enforcement_level}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}