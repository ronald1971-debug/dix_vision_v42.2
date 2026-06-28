import { AltSignalDashboard } from "@/domains/learning/widgets/AltSignalDashboard";
import { ASKBOrchestrator } from "@/domains/learning/widgets/ASKBOrchestrator";
import { CausalRiskAttribution } from "@/domains/learning/widgets/CausalRiskAttribution";
import { CounterfactualPanel } from "@/domains/learning/widgets/CounterfactualPanel";
import { EarningsRAG } from "@/domains/learning/widgets/EarningsRAG";
import { IntentExecutionPanel } from "@/domains/learning/widgets/IntentExecutionPanel";
import { MultilingualNewsFusion } from "@/domains/learning/widgets/MultilingualNewsFusion";
import { NLQConsole } from "@/domains/learning/widgets/NLQConsole";
import { SmartMoneyTracker } from "@/domains/learning/widgets/SmartMoneyTracker";
import { WidgetSlot } from "@/components/WidgetSlot";

export function AIPage() {
  return (
    <div className="grid h-full grid-cols-1 gap-3 overflow-auto p-3 lg:grid-cols-2 xl:grid-cols-3">
      <WidgetSlot widgetKey="ai:ASKBOrchestrator" className="min-h-[320px] xl:col-span-2">
        <ASKBOrchestrator />
      </WidgetSlot>
      <WidgetSlot widgetKey="ai:CounterfactualPanel" className="min-h-[320px]">
        <CounterfactualPanel />
      </WidgetSlot>
      <WidgetSlot widgetKey="ai:NLQConsole" className="min-h-[320px]">
        <NLQConsole />
      </WidgetSlot>
      <WidgetSlot widgetKey="ai:EarningsRAG" className="min-h-[320px]">
        <EarningsRAG />
      </WidgetSlot>
      <WidgetSlot widgetKey="ai:MultilingualNewsFusion" className="min-h-[320px]">
        <MultilingualNewsFusion />
      </WidgetSlot>
      <WidgetSlot widgetKey="ai:AltSignalDashboard" className="min-h-[320px]">
        <AltSignalDashboard />
      </WidgetSlot>
      <WidgetSlot widgetKey="ai:CausalRiskAttribution" className="min-h-[320px]">
        <CausalRiskAttribution />
      </WidgetSlot>
      <WidgetSlot widgetKey="ai:IntentExecutionPanel" className="min-h-[320px]">
        <IntentExecutionPanel />
      </WidgetSlot>
      <WidgetSlot widgetKey="ai:SmartMoneyTracker" className="min-h-[320px] xl:col-span-3">
        <SmartMoneyTracker />
      </WidgetSlot>
    </div>
  );
}
