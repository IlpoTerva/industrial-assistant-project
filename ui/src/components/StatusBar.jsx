import { useEffect, useState } from 'react';
import { IconMoon, IconPlus, IconSun } from './Icons.jsx';

function useClock() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 15000);
    return () => clearInterval(t);
  }, []);
  return now;
}

export default function StatusBar({ station, serverOnline, sampleData, theme, onToggleTheme, textScale, onTextScale, onNewSession }) {
  const now = useClock();
  const time = now.toLocaleTimeString('fi-FI', { hour: '2-digit', minute: '2-digit' });
  const date = now.toLocaleDateString('fi-FI', { day: 'numeric', month: 'numeric' });

  return (
    <header className="statusbar">
      <div className="statusbar__id">
        <span className="brandmark" aria-hidden="true" />
        <div className="statusbar__titles">
          <span className="statusbar__app">Operator Assistant</span>
          <span className="statusbar__station">{station}</span>
        </div>
      </div>

      <div className="statusbar__state" aria-label="System status">
        <span className={`pill ${serverOnline ? 'pill--ok' : 'pill--alarm'}`}>
          <span className="pill__dot" />
          {serverOnline ? 'Server online · local network' : 'Server offline'}
        </span>
        {sampleData && <span className="pill pill--warn">Sample data</span>}
      </div>

      <div className="statusbar__controls">
        <div className="segmented" role="group" aria-label="Text size">
          <button type="button" className={textScale === 1 ? 'is-on' : ''} onClick={() => onTextScale(1)} aria-pressed={textScale === 1}>
            A
          </button>
          <button type="button" className={`segmented__big ${textScale > 1 ? 'is-on' : ''}`} onClick={() => onTextScale(1.18)} aria-pressed={textScale > 1}>
            A
          </button>
        </div>
        <button type="button" className="iconbtn" onClick={onToggleTheme} aria-label={theme === 'dark' ? 'Switch to day display' : 'Switch to night display'}>
          {theme === 'dark' ? <IconSun /> : <IconMoon />}
        </button>
        <button type="button" className="btn btn--quiet" onClick={onNewSession}>
          <IconPlus /> <span className="hide-narrow">New session</span>
        </button>
        <time className="statusbar__clock" dateTime={now.toISOString()}>
          <span>{time}</span>
          <small>{date}</small>
        </time>
      </div>
    </header>
  );
}
