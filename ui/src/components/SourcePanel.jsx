import Figure from './Figure.jsx';
import { IconDoc, IconX } from './Icons.jsx';

// Right-hand panel: where the focused answer came from, plus any enlarged figure.
// Showing sources lets the operator check the manual page instead of trusting the answer blindly.
export default function SourcePanel({ msg, figure, onCloseFigure, open, onClose }) {
  const figures = msg?.blocks.filter((b) => b.type === 'figure') ?? [];

  return (
    <aside className={`panel ${open ? 'is-open' : ''}`} aria-label="Sources for the selected answer">
      <div className="panel__head">
        <span className="label">Sources for selected answer</span>
        <button type="button" className="iconbtn panel__close" onClick={onClose} aria-label="Close sources">
          <IconX />
        </button>
      </div>

      {figure && (
        <div className="panel__figure">
          <Figure block={figure} large />
          <button type="button" className="btn btn--small" onClick={onCloseFigure}>Close figure</button>
        </div>
      )}

      {msg ? (
        <>
          <ul className="sources">
            {msg.sources.map((s, i) => (
              <li key={i} className="source">
                <IconDoc />
                <div>
                  <span className="source__doc">{s.doc}</span>
                  <span className="source__section">{s.section}</span>
                </div>
                {s.page != null && <span className="source__page">p. {s.page}</span>}
              </li>
            ))}
            {msg.sources.length === 0 && <li className="panel__empty">This answer has no document sources.</li>}
          </ul>

          {!figure && figures.length > 0 && (
            <div className="panel__thumbs">
              <span className="label">Figures in this answer</span>
              {figures.map((f, i) => (
                <Figure key={i} block={f} />
              ))}
            </div>
          )}

          <p className="panel__note">
            Answers are generated from these documents. If a step looks wrong, check the page in the manual or ask maintenance.
          </p>
        </>
      ) : (
        <p className="panel__empty">Select an answer to see which manual pages it used.</p>
      )}
    </aside>
  );
}
