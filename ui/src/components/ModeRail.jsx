import { IconAlarm, IconAuto, IconBook, IconChart } from './Icons.jsx';

// Modes map to the LangGraph routes. "Auto" lets the router node decide.
export const MODES = [
  { id: 'auto', label: 'Ask anything', hint: 'Assistant picks the source', Icon: IconAuto },
  { id: 'manual', label: 'Machine manual', hint: 'Startup, operation, settings', Icon: IconBook },
  { id: 'troubleshooting', label: 'Alarm & fault', hint: 'Alarm codes and fixes', Icon: IconAlarm },
  { id: 'mes', label: 'Production data', hint: 'OEE, downtime, scrap', Icon: IconChart },
];

const QUICK_ACTIONS = {
  auto: ['How do I start the machine after power-up?', 'Alarm 25050 on X axis', 'OEE by work center this week'],
  manual: ['How do I start the machine after power-up?', 'How do I approach the reference point?', 'How do I change the tool offset?'],
  troubleshooting: ['Alarm 25050 on X axis', 'Spindle does not start', 'Emergency stop alarm stays active'],
  mes: ['OEE by work center this week', 'Top downtime reasons this week', 'Scrap rate for order 4471'],
};

export default function ModeRail({ mode, onMode, onQuick, disabled }) {
  return (
    <nav className="rail" aria-label="Assistant mode">
      <span className="label">Mode</span>
      <div className="rail__modes">
        {MODES.map(({ id, label, hint, Icon }) => (
          <button
            key={id}
            type="button"
            className={`modebtn ${mode === id ? 'is-on' : ''}`}
            aria-pressed={mode === id}
            onClick={() => onMode(id)}
          >
            <Icon />
            <span className="modebtn__text">
              <span className="modebtn__label">{label}</span>
              <span className="modebtn__hint">{hint}</span>
            </span>
          </button>
        ))}
      </div>

      <div className="rail__quick">
        <span className="label">Common questions</span>
        {QUICK_ACTIONS[mode].map((q) => (
          <button key={q} type="button" className="quickbtn" disabled={disabled} onClick={() => onQuick(q)}>
            {q}
          </button>
        ))}
      </div>
    </nav>
  );
}
