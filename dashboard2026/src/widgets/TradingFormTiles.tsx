import { useQuery } from "@tanstack/react-query";
import { fetchTradingForms } from "@/api/signals";

export function TradingFormTiles() {
  const { data } = useQuery({
    queryKey: ["trading-forms"],
    queryFn: ({ signal }) => fetchTradingForms(signal),
    refetchInterval: 10000,
  });

  if (!data) return <p className="text-xs text-slate-500">Loading trading forms…</p>;

  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {data.forms.map((form) => (
        <div key={form.form} className="flex flex-col gap-2 rounded border border-border bg-surface p-4">
          <div className="flex items-baseline justify-between">
            <h3 className="text-sm font-semibold text-slate-200">{form.form}</h3>
            <span className="text-[10px] uppercase tracking-widest text-slate-500">INDIRA</span>
          </div>
          
          <div className="flex flex-col gap-1">
            <div className="flex items-baseline justify-between text-xs">
              <span className="text-slate-400">Signals</span>
              <span className="font-mono text-slate-200">{form.signals}</span>
            </div>
            <div className="flex items-baseline justify-between text-xs">
              <span className="text-slate-400">Fill Rate</span>
              <span className={`font-mono ${form.fill_rate_pct >= 80 ? "text-ok" : form.fill_rate_pct >= 50 ? "text-warn" : "text-danger"}`}>
                {form.fill_rate_pct}%
              </span>
            </div>
            <div className="flex items-baseline justify-between text-xs">
              <span className="text-slate-400">Exposure</span>
              <span className={`font-mono ${form.exposure_usd > 100000 ? "text-warn" : form.exposure_usd > 500000 ? "text-danger" : "text-ok"}`}>
                ${form.exposure_usd.toLocaleString()}
              </span>
            </div>
            <div className="flex items-baseline justify-between text-xs">
              <span className="text-slate-400">PnL</span>
              <span className={`font-mono ${form.pnl_usd >= 0 ? "text-ok" : "text-danger"}`}>
                ${form.pnl_usd.toLocaleString()}
              </span>
            </div>
            <div className="flex items-baseline justify-between text-xs">
              <span className="text-slate-400">Adapters Ready</span>
              <span className={`font-mono ${form.adapters_ready >= 3 ? "text-ok" : form.adapters_ready >= 1 ? "text-warn" : "text-danger"}`}>
                {form.adapters_ready}
              </span>
            </div>
          </div>
        </div>
      ))}
      
      {data.forms.length === 0 && (
        <p className="col-span-full text-xs text-slate-500">No trading forms configured.</p>
      )}
    </div>
  );
}
