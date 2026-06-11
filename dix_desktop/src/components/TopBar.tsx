import { useLocale, t } from "../i18n";
import { STAGE_LABELS, type RelationshipState } from "../api";
import {
  CloseIcon,
  DownloadIcon,
  EarIcon,
  EyeIcon,
  GearIcon,
  RefreshIcon,
  WarningIcon,
  ShieldIcon,
} from "./icons";
import { useState } from "react";

export interface TopBarProps {
  mode: string;
  hasKey: boolean;
  listenEnabled: boolean;
  listenReady: boolean;
  listening: boolean;
  heard: boolean;
  onToggleListen: () => void;
  onToggleSettings: () => void;
  onToggleWizard: () => void;
  onReset: () => void;
  onQuit: () => void;
  autoWatch: boolean;
  autoWatchAvailable: boolean;
  onToggleAutoWatch: () => void;
  relationship: RelationshipState | null;
  showRelationshipBadge: boolean;
  complianceLevel: number;
  onComplianceChange: (level: number) => void;
}

/**
 * Floating top-right control strip: mode badge, relationship badge,
 * listen toggle, auto-watch toggle, reset / downloads / settings / quit.
 *
 * `props.listenEnabled` is unused by the UI directly today — the actual
 * styling reads `props.listening` (true while the mic stream is live) —
 * but it's kept on the prop type so callers can still flow it through
 * for future "want vs is" indicators without API churn.
 */
export function TopBar(props: TopBarProps) {
  useLocale(); // re-render on language change
  void props.listenEnabled;
  return (
    <div
      className="interactive"
      style={{
        position: "absolute",
        top: 8,
        right: 8,
        display: "flex",
        gap: 6,
        alignItems: "center",
        fontSize: 11,
        color: "#fff",
      }}
    >
      <span
        style={{
          padding: "3px 8px",
          borderRadius: 8,
          background: "rgba(20,20,28,0.7)",
          opacity: 0.9,
          textTransform: "uppercase",
          letterSpacing: 0.5,
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
        }}
        title={props.hasKey ? t("topbar.key_saved") : t("topbar.no_key")}
      >
        <span>{props.mode}</span>
        {!props.hasKey && props.mode !== "local" && (
          <WarningIcon size={11} style={{ opacity: 0.85 }} />
        )}
      </span>
      {props.showRelationshipBadge && props.relationship && (
        <RelationshipBadge state={props.relationship} />
      )}
      <ComplianceControl 
        level={props.complianceLevel} 
        onChange={props.onComplianceChange} 
      />
      <button
        onClick={props.onToggleListen}
        disabled={!props.listenReady}
        style={iconBtnStyle(props.listening)}
        title={
          !props.listenReady
            ? t("topbar.listen.tip_setup")
            : props.listening
              ? t("topbar.listen.tip_listening")
              : t("topbar.listen.tip_idle")
        }
        aria-label={t("topbar.listen.tip_idle")}
      >
        <EarIcon size={14} />
        {props.heard && (
          <span
            style={{
              position: "absolute",
              top: 3,
              right: 3,
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "#7ec6ff",
              boxShadow: "0 0 6px rgba(126,198,255,0.85)",
            }}
          />
        )}
      </button>
      <button
        onClick={props.onToggleAutoWatch}
        disabled={!props.autoWatchAvailable}
        style={iconBtnStyle(props.autoWatch)}
        title={
          !props.autoWatchAvailable
            ? t("topbar.watch.tip_setup")
            : props.autoWatch
              ? t("topbar.watch.tip_on")
              : t("topbar.watch.tip_off")
        }
        aria-label={t("topbar.watch.tip_off")}
      >
        <EyeIcon size={14} />
      </button>
      <button
        onClick={props.onReset}
        style={iconBtn}
        title={t("topbar.reset")}
        aria-label={t("topbar.reset")}
      >
        <RefreshIcon size={13} />
      </button>
      <button
        onClick={props.onToggleWizard}
        style={iconBtn}
        title={t("topbar.downloads")}
        aria-label={t("topbar.downloads")}
      >
        <DownloadIcon size={13} />
      </button>
      <button
        onClick={props.onToggleSettings}
        style={iconBtn}
        title={t("topbar.settings")}
        aria-label={t("topbar.settings")}
      >
        <GearIcon size={13} />
      </button>
      <button
        onClick={props.onQuit}
        style={iconBtn}
        title={t("topbar.quit")}
        aria-label={t("topbar.quit")}
      >
        <CloseIcon size={13} />
      </button>
    </div>
  );
}

function RelationshipBadge({ state }: { state: RelationshipState }) {
  useLocale();
  const meta = STAGE_LABELS[state.stage];
  const stages = Object.keys(STAGE_LABELS) as (keyof typeof STAGE_LABELS)[];
  const idx = stages.indexOf(state.stage);
  const thresholds = [0, 50, 150, 300, 500, 750, 1000];
  const lo = thresholds[idx] ?? 0;
  const hi = thresholds[idx + 1] ?? state.score + 1;
  const pct = Math.max(0, Math.min(1, (state.score - lo) / (hi - lo))) * 100;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const stageName = t(`stage.${state.stage}` as any);
  return (
    <span
      title={`${stageName} · ${t("rel.score", { score: state.score })} · ${t("rel.interactions", { count: state.total_interactions, streak: state.daily_streak })}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        padding: "3px 8px",
        borderRadius: 8,
        background: "rgba(20,20,28,0.7)",
        fontSize: 11,
      }}
    >
      <span>{meta.emoji}</span>
      <span style={{ opacity: 0.95 }}>{stageName}</span>
      <span
        style={{
          width: 28,
          height: 4,
          borderRadius: 2,
          background: "rgba(255,255,255,0.18)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <span
          style={{
            position: "absolute",
            inset: 0,
            width: `${pct}%`,
            background: "rgba(255,255,255,0.55)",
          }}
        />
      </span>
    </span>
  );
}

const iconBtn: React.CSSProperties = {
  width: 26,
  height: 26,
  borderRadius: 8,
  border: "1px solid rgba(255,255,255,0.10)",
  background: "rgba(20,20,28,0.7)",
  color: "#fff",
  cursor: "pointer",
  fontSize: 13,
  lineHeight: 1,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  position: "relative",
  padding: 0,
};

/** Same neutral icon button, with a subtle white border when "active". */
function iconBtnStyle(active: boolean): React.CSSProperties {
  return {
    ...iconBtn,
    border: active
      ? "1px solid rgba(255,255,255,0.45)"
      : iconBtn.border,
    background: active ? "rgba(255,255,255,0.10)" : iconBtn.background,
  };
}

function ComplianceControl({ level, onChange }: { level: number; onChange: (level: number) => void }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [tempLevel, setTempLevel] = useState(level);

  useLocale();

  const getComplianceColor = (lvl: number) => {
    if (lvl >= 80) return "rgba(34, 197, 94, 0.8)"; // green
    if (lvl >= 50) return "rgba(234, 179, 8, 0.8)"; // yellow
    if (lvl >= 25) return "rgba(249, 115, 22, 0.8)"; // orange
    return "rgba(239, 68, 68, 0.8)"; // red
  };

  const getComplianceLabel = (lvl: number) => {
    if (lvl >= 80) return "FULL";
    if (lvl >= 50) return "HIGH";
    if (lvl >= 25) return "MED";
    return "LOW";
  };

  const handleClick = () => {
    setIsExpanded(!isExpanded);
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newLevel = parseInt(e.target.value);
    setTempLevel(newLevel);
  };

  const handleSliderRelease = () => {
    onChange(tempLevel);
    setIsExpanded(false);
  };

  return (
    <div style={{ position: "relative" }}>
      <button
        onClick={handleClick}
        style={{
          ...iconBtn,
          borderColor: getComplianceColor(level),
          background: `${getComplianceColor(level).replace("0.8", "0.2")}`,
        }}
        title={`Compliance Level: ${level}% (${getComplianceLabel(level)})`}
        aria-label={`Compliance Level: ${level}%`}
      >
        <ShieldIcon size={13} />
        <span style={{ fontSize: 10, fontWeight: "bold", marginLeft: 4 }}>
          {level}%
        </span>
      </button>

      {isExpanded && (
        <div
          style={{
            position: "absolute",
            top: "100%",
            right: 0,
            marginTop: 8,
            padding: 12,
            borderRadius: 8,
            background: "rgba(20,20,28,0.95)",
            border: `1px solid ${getComplianceColor(level)}`,
            color: "#fff",
            fontSize: 11,
            zIndex: 1000,
            minWidth: 200,
            boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
          }}
        >
          <div style={{ marginBottom: 8, fontWeight: "bold" }}>
            Compliance Level: {tempLevel}%
          </div>
          <div style={{ marginBottom: 12, fontSize: 10, opacity: 0.8 }}>
            {getComplianceLabel(tempLevel)} Compliance
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={tempLevel}
            onChange={handleSliderChange}
            onMouseUp={handleSliderRelease}
            onTouchEnd={handleSliderRelease}
            style={{
              width: "100%",
              cursor: "pointer",
              accentColor: getComplianceColor(tempLevel),
            }}
          />
          <div style={{ marginTop: 8, fontSize: 9, opacity: 0.7, lineHeight: 1.4 }}>
            <div>0-25%: Minimal checks</div>
            <div>26-50%: Standard validation</div>
            <div>51-75%: Enhanced compliance</div>
            <div>76-100%: Full enforcement</div>
          </div>
          <div style={{ marginTop: 8, fontSize: 9, opacity: 0.6 }}>
            Components: Regulatory, Audit, Trading, Data
          </div>
        </div>
      )}
    </div>
  );
}

export default TopBar;
