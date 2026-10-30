import Figure from './Figure.jsx';
import { IconCheck, IconDoc, IconTool, IconWarn, IconX } from './Icons.jsx';

const ROUTE_LABEL = {
  manual: 'Machine manual',
  troubleshooting: 'Alarm & fault',
  mes: 'Production data',
};

function Steps({ block }) {
  return (
    <div className="steps">
      {block.title && <span className="label">{block.title}</span>}
      <ol>
        {block.items.map((item, i) => (
          <li key={i}>
            <span className="steps__n">{i + 1}</span>
            <span>{item}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

function Choices({ block, selected, onChoose, disabled }) {
  return (
    <div className="choices">
      <span className="choices__prompt">{block.prompt}</span>
      <div className="choices__grid">
        {block.options.map((opt, i) => {
          const isSel = selected === opt.id;
          return (
            <button
              key={opt.id}
              type="button"
              className={`choice ${isSel ? 'is-on' : ''}`}
              disabled={disabled || (selected && !isSel)}
              aria-pressed={isSel}
              onClick={() => onChoose(opt)}
            >
              <span className="choice__n">{i + 1}</span>
              <span className="choice__text">
                <span className="choice__label">{opt.label}</span>
                <span className="choice__detail">{opt.detail}</span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function DataTable({ block }) {
  return (
    <div className="datatable">
      <div className="datatable__scroll">
        <table>
          <thead>
            <tr>{block.columns.map((c) => <th key={c} scope="col">{c}</th>)}</tr>
          </thead>
          <tbody>
            {block.rows.map((row, r) => (
              <tr key={r}>
                {row.map((cell, c) => {
                  const pct = typeof cell === 'string' && cell.endsWith('%') ? parseFloat(cell) : null;
                  const low = c === row.length - 1 && pct !== null && pct < 65;
                  return c === 0 ? (
                    <th key={c} scope="row">{cell}</th>
                  ) : (
                    <td key={c} className={low ? 'is-low' : ''}>{cell}</td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="datatable__tool">
        <IconTool /> Calculated by <code>{block.tool}</code>, not by the language model
      </p>
    </div>
  );
}

function Block({ block, msg, onChoose, onOpenFigure, busy }) {
  switch (block.type) {
    case 'text':
      return <p className="answer__text">{block.text}</p>;
    case 'steps':
      return <Steps block={block} />;
    case 'warning':
      return (
        <p className="notice notice--warn">
          <IconWarn /> <span>{block.text}</span>
        </p>
      );
    case 'figure':
      return <Figure block={block} onOpen={onOpenFigure} />;
    case 'choices':
      return <Choices block={block} selected={msg.chosen} disabled={busy} onChoose={(opt) => onChoose(msg.id, opt)} />;
    case 'table':
      return <DataTable block={block} />;
    default:
      return null;
  }
}

export default function Message({ msg, isFocused, onFocusSources, onChoose, onOpenFigure, onFeedback, busy }) {
  if (msg.role === 'user') {
    return (
      <div className="msg msg--user">
        <span className="label">Operator</span>
        <p>{msg.text}</p>
      </div>
    );
  }

  const awaitingChoice = msg.blocks.some((b) => b.type === 'choices') && !msg.chosen;

  return (
    <article className={`msg msg--assistant ${isFocused ? 'is-focused' : ''}`}>
      <header className="answer__head">
        <span className={`route route--${msg.route}`}>{ROUTE_LABEL[msg.route] ?? 'Assistant'}</span>
        {msg.sources?.length > 0 && (
          <button type="button" className="linkbtn" onClick={() => onFocusSources(msg.id)}>
            <IconDoc /> {msg.sources.length} {msg.sources.length === 1 ? 'source' : 'sources'}
          </button>
        )}
      </header>

      <div className="answer__body">
        {msg.blocks.map((b, i) => (
          <Block key={i} block={b} msg={msg} onChoose={onChoose} onOpenFigure={onOpenFigure} busy={busy} />
        ))}
      </div>

      {!awaitingChoice && (
        <footer className="answer__foot">
          {msg.feedback ? (
            <span className={`feedback-done ${msg.feedback === 'solved' ? 'is-ok' : ''}`}>
              {msg.feedback === 'solved' ? 'Marked as solved' : 'Marked as not solved · maintenance can review this session'}
            </span>
          ) : (
            <>
              <span className="label">Did this help?</span>
              <button type="button" className="btn btn--small" onClick={() => onFeedback(msg.id, 'solved')}>
                <IconCheck /> Solved
              </button>
              <button type="button" className="btn btn--small" onClick={() => onFeedback(msg.id, 'unsolved')}>
                <IconX /> Not solved
              </button>
            </>
          )}
        </footer>
      )}
    </article>
  );
}
