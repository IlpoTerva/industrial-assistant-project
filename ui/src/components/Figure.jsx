// Figures from the manuals. The backend sends `src` (an image URL from the PDF extraction).
// Until then, `ref` selects a schematic placeholder drawn here.

function PanelSketch() {
  const keys = [
    ['JOG', 0, 0], ['REF', 1, 0], ['AUTO', 2, 0],
    ['X', 0, 1], ['Z', 1, 1], ['RESET', 2, 1, true],
    ['−', 0, 2], ['RAPID', 1, 2], ['+', 2, 2],
  ];
  return (
    <svg viewBox="0 0 340 170" role="img" aria-label="Schematic of the machine control panel">
      <rect className="sk-panel" x="6" y="6" width="328" height="158" rx="8" />
      <circle className="sk-estop" cx="56" cy="62" r="30" />
      <circle className="sk-estop-in" cx="56" cy="62" r="18" />
      <text className="sk-label" x="56" y="116" textAnchor="middle">E-STOP</text>
      {keys.map(([t, c, r, hl]) => (
        <g key={t} transform={`translate(${118 + c * 56} ${22 + r * 44})`}>
          <rect className={hl ? 'sk-key sk-key--hl' : 'sk-key'} width="48" height="34" rx="4" />
          <text className="sk-keytext" x="24" y="22" textAnchor="middle">{t}</text>
        </g>
      ))}
      <circle className="sk-dial" cx="300" cy="62" r="22" />
      <path className="sk-line" d="M300 62 L314 48" />
      <text className="sk-label" x="300" y="116" textAnchor="middle">FEED %</text>
    </svg>
  );
}

function AxisSketch() {
  const folds = Array.from({ length: 9 }, (_, i) => 120 + i * 14);
  return (
    <svg viewBox="0 0 340 170" role="img" aria-label="Schematic of the X axis with way cover and lubrication point">
      <rect className="sk-panel" x="20" y="112" width="300" height="30" rx="3" />
      <rect className="sk-key" x="40" y="70" width="78" height="42" rx="3" />
      <text className="sk-keytext" x="79" y="96" textAnchor="middle">CARRIAGE</text>
      <path className="sk-line" d={`M118 82 ${folds.map((x, i) => `L${x + 7} ${i % 2 ? 82 : 104} L${x + 14} ${i % 2 ? 104 : 82}`).join(' ')}`} />
      <text className="sk-label" x="185" y="62" textAnchor="middle">WAY COVER</text>
      <circle className="sk-mark" cx="62" cy="126" r="9" />
      <path className="sk-line" d="M62 135 L62 152 L110 152" />
      <text className="sk-label" x="114" y="156">LUBRICATION POINT</text>
    </svg>
  );
}

const SKETCHES = { mcp: PanelSketch, axis: AxisSketch };

export default function Figure({ block, onOpen, large = false }) {
  const Sketch = SKETCHES[block.ref];
  const content = block.src ? <img src={block.src} alt={block.caption} /> : Sketch ? <Sketch /> : null;

  return (
    <figure className={`figure ${large ? 'figure--large' : ''}`}>
      {onOpen ? (
        <button type="button" className="figure__frame" onClick={() => onOpen(block)} aria-label={`Enlarge: ${block.caption}`}>
          {content}
        </button>
      ) : (
        <div className="figure__frame">{content}</div>
      )}
      <figcaption>
        <span className="label">Figure</span> {block.caption}
      </figcaption>
    </figure>
  );
}
