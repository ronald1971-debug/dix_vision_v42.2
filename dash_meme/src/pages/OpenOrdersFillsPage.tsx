import { useQuery } from "@tanstack/react-query";
import { fetchOpenOrders, fetchRecentFills, cancelOrder, cancelAllOrders } from "@/api/signals";

export function OpenOrdersFillsPage() {
  const { data: ordersData } = useQuery({
    queryKey: ["open-orders"],
    queryFn: ({ signal }) => fetchOpenOrders(signal),
    refetchInterval: 5000,
  });

  const { data: fillsData } = useQuery({
    queryKey: ["recent-fills"],
    queryFn: ({ signal }) => fetchRecentFills(50, signal),
    refetchInterval: 5000,
  });

  const handleCancelOrder = async (orderId: string) => {
    try {
      await cancelOrder(orderId);
      // Trigger refetch
    } catch (error) {
      console.error("Failed to cancel order:", error);
    }
  };

  const handleCancelAllOrders = async () => {
    try {
      await cancelAllOrders();
      // Trigger refetch
    } catch (error) {
      console.error("Failed to cancel all orders:", error);
    }
  };

  return (
    <section className="flex h-full flex-col">
      <header className="mb-4">
        <h1 className="text-lg font-semibold tracking-tight">
          Orders & Fills
          <span className="ml-2 rounded border border-border bg-bg px-2 py-0.5 font-mono text-[11px] uppercase tracking-widest text-slate-400">LIVE</span>
        </h1>
        <p className="mt-1 text-xs text-slate-400">
          Open orders and recent fills with real-time updates.
          Refreshes every 5s.
        </p>
      </header>

      <div className="flex gap-4 mb-4">
        <button
          onClick={handleCancelAllOrders}
          className="rounded border border-border bg-surface px-4 py-2 text-sm font-medium text-slate-200 hover:bg-surface/80 transition-colors"
        >
          Cancel All Orders
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Open Orders */}
        <div className="flex flex-col gap-2 rounded border border-border bg-surface p-4">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
            Open Orders
            <span className="ml-2 text-[10px] text-slate-500">INDIRA</span>
          </h3>
          
          {ordersData ? (
            <div className="flex flex-col gap-2">
              {ordersData.orders.length > 0 ? (
                ordersData.orders.map((order) => (
                  <div key={order.id} className="flex items-center gap-3 rounded border border-border bg-bg/60 px-3 py-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-slate-200">{order.symbol}</span>
                        <span className={`text-[10px] uppercase ${order.side === "BUY" ? "text-ok" : "text-danger"}`}>
                          {order.side}
                        </span>
                        <span className="text-[10px] text-slate-500">{order.type}</span>
                        <span className="text-[10px] text-slate-500">{order.status}</span>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-[10px] text-slate-500">
                        <span>Qty: {order.qty}</span>
                        {order.price && <span>Price: {order.price}</span>}
                        <span>{order.ts_utc}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleCancelOrder(order.id)}
                      className="rounded border border-border bg-surface px-3 py-1 text-xs text-slate-400 hover:text-slate-200 hover:bg-surface/80 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500">No open orders.</p>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500">Loading orders…</p>
          )}
        </div>

        {/* Recent Fills */}
        <div className="flex flex-col gap-2 rounded border border-border bg-surface p-4">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
            Recent Fills
            <span className="ml-2 text-[10px] text-slate-500">INDIRA</span>
          </h3>
          
          {fillsData ? (
            <div className="flex flex-col gap-2 max-h-[400px] overflow-y-auto">
              {fillsData.fills.length > 0 ? (
                fillsData.fills.map((fill) => (
                  <div key={fill.id} className="flex items-center gap-3 rounded border border-border bg-bg/60 px-3 py-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-slate-200">{fill.symbol}</span>
                        <span className={`text-[10px] uppercase ${fill.side === "BUY" ? "text-ok" : "text-danger"}`}>
                          {fill.side}
                        </span>
                        <span className="text-[10px] text-slate-500">{fill.qty} @ {fill.price}</span>
                        <span className="text-[10px] text-slate-500">Fee: ${fill.fee_usd}</span>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-[10px] text-slate-500">
                        <span>{fill.ts_utc}</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500">No recent fills.</p>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500">Loading fills…</p>
          )}
        </div>
      </div>
    </section>
  );
}
