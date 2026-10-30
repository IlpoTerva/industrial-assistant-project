import { useRef, useState } from 'react';
import { IconKeypad, IconSend } from './Icons.jsx';

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'C', '0', '⌫'];

// Alarm codes are typed on a large on-screen keypad: faster than a soft keyboard with gloves on.
function AlarmKeypad({ onSubmit, onClose }) {
  const [code, setCode] = useState('');

  const press = (k) => {
    if (k === 'C') return setCode('');
    if (k === '⌫') return setCode((c) => c.slice(0, -1));
    setCode((c) => (c.length < 6 ? c + k : c));
  };

  return (
    <div className="keypad" role="dialog" aria-label="Enter alarm code">
      <div className="keypad__display">
        <span className="label">Alarm code</span>
        <output className="keypad__code" aria-live="polite">{code || '——'}</output>
      </div>
      <div className="keypad__grid">
        {KEYS.map((k) => (
          <button key={k} type="button" className={`keypad__key ${/\d/.test(k) ? '' : 'keypad__key--fn'}`} onClick={() => press(k)}>
            {k}
          </button>
        ))}
      </div>
      <div className="keypad__actions">
        <button type="button" className="btn" onClick={onClose}>Cancel</button>
        <button type="button" className="btn btn--primary" disabled={code.length < 3} onClick={() => onSubmit(`Alarm ${code}`)}>
          Look up alarm
        </button>
      </div>
    </div>
  );
}

export default function Composer({ mode, busy, onSend }) {
  const [text, setText] = useState('');
  const [keypad, setKeypad] = useState(false);
  const inputRef = useRef(null);

  const submit = (e) => {
    e.preventDefault();
    const t = text.trim();
    if (!t || busy) return;
    onSend(t);
    setText('');
  };

  const placeholder = {
    auto: 'Ask about the machine, an alarm or production…',
    manual: 'Ask how to operate the machine…',
    troubleshooting: 'Describe the fault or enter the alarm code…',
    mes: 'Ask about orders, OEE, downtime or scrap…',
  }[mode];

  return (
    <div className="composer">
      {keypad && (
        <AlarmKeypad
          onClose={() => setKeypad(false)}
          onSubmit={(t) => {
            setKeypad(false);
            onSend(t);
          }}
        />
      )}
      <form className="composer__form" onSubmit={submit}>
        <button
          type="button"
          className={`iconbtn iconbtn--big ${keypad ? 'is-on' : ''}`}
          onClick={() => setKeypad((k) => !k)}
          aria-pressed={keypad}
          aria-label="Enter alarm code on keypad"
          title="Alarm code keypad"
        >
          <IconKeypad />
        </button>
        <label htmlFor="composer-input" className="sr-only">Question</label>
        <input
          id="composer-input"
          ref={inputRef}
          className="composer__input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={placeholder}
          autoComplete="off"
        />
        <button type="submit" className="btn btn--primary btn--send" disabled={busy || !text.trim()}>
          <IconSend /> <span className="hide-narrow">Send</span>
        </button>
      </form>
    </div>
  );
}
