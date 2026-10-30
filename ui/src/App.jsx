import { useEffect, useMemo, useRef, useState } from 'react';
import StatusBar from './components/StatusBar.jsx';
import ModeRail, { MODES } from './components/ModeRail.jsx';
import Message from './components/Message.jsx';
import Composer from './components/Composer.jsx';
import SourcePanel from './components/SourcePanel.jsx';
import { sendMessage } from './api/client.js';

const STATION = 'Cell 3 · CNC lathe · SINUMERIK 808D';
const newId = () => Math.random().toString(36).slice(2, 9);

function readPref(key, fallback) {
  try {
    return localStorage.getItem(key) ?? fallback;
  } catch {
    return fallback;
  }
}
function writePref(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* storage unavailable: preference lasts for this session only */
  }
}

function PipelineStatus({ stages }) {
  const items = stages.length ? stages : ['Starting']
  return (
    <div className="pipeline" role="status" aria-live="polite">
      {items.map((label, i) => (
        <span key={i} className={`pipeline__step ${i < items.length - 1 ? 'is-done' : 'is-active'}`}>
        <span className="pipeline__dot" />
          {label}
        </span>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="empty">
      <h1>What do you need help with?</h1>
      <p>Ask about operating the machine, enter an alarm code, or check production figures. Answers show the manual pages they come from.</p>

    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [mode, setMode] = useState('auto');
  const [stages, setStages] = useState(null);
  
  const [error, setError] = useState(null);
  const [focusId, setFocusId] = useState(null);
  const [figure, setFigure] = useState(null);
  const [panelOpen, setPanelOpen] = useState(false);
  const [theme, setTheme] = useState(() => readPref('oa-theme', ''));
  const [textScale, setTextScale] = useState(() => Number(readPref('oa-scale', '1')));
  const [sessionId, setSessionId] = useState(newId);
  const threadRef = useRef(null);

  const busy = stages !== null;
  const focused = useMemo(() => messages.find((m) => m.id === focusId) ?? null, [messages, focusId]);

  // Theme: follow the system until the operator picks day or night.
  const systemDark = typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  const effectiveTheme = theme || (systemDark ? 'dark' : 'light');
  useEffect(() => {
    if (theme) document.documentElement.setAttribute('data-theme', theme);
    else document.documentElement.removeAttribute('data-theme');
  }, [theme]);

  useEffect(() => {
    document.documentElement.style.setProperty('--text-scale', String(textScale));
  }, [textScale]);

  useEffect(() => {
    const el = threadRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
  }, [messages, stages]);

  async function ask({ text, choiceId}) {
    setError(null);
    setMessages((m) => [...m, { id: newId(), role: 'user', text }]);
    setStages([]);
    try {
      const res = await sendMessage(
        {message: text, sessionId, mode, choiceId}, 
        (e) => {setStages((s) => [...(s ?? []), e.label])}
      );
      const id = newId();
      setMessages((m) => [...m, { id, role: 'assistant', ...res }]);
      setFocusId(id);
      setFigure(null);
    } catch (e) {
      setError(e.message || 'The assistant did not answer. Check the server connection and try again.');
    } finally {
      setStages(null);
    }
  }

  const handleChoose = (msgId, opt) => {
    setMessages((m) => m.map((x) => (x.id === msgId ? { ...x, chosen: opt.id } : x)));
    const n = messages.find((x) => x.id === msgId)?.blocks.find((b) => b.type === 'choices')?.options.findIndex((o) => o.id === opt.id);
    ask({ text: `Situation ${n + 1}: ${opt.label}`, choiceId: opt.id });
  };

  const handleFeedback = (msgId, value) => {
    // TODO: POST /api/feedback { session_id, message_id, value } for evaluation logging
    setMessages((m) => m.map((x) => (x.id === msgId ? { ...x, feedback: value } : x)));
  };

  const newSession = () => {
    setMessages([]);
    setFocusId(null);
    setFigure(null);
    setError(null);
    setSessionId(newId());
  };

  const modeLabel = MODES.find((m) => m.id === mode)?.label;

  return (
    <div className="app">
      <StatusBar
        station={STATION}
        serverOnline
        sampleData
        theme={effectiveTheme}
        onToggleTheme={() => {
          const next = effectiveTheme === 'dark' ? 'light' : 'dark';
          setTheme(next);
          writePref('oa-theme', next);
        }}
        textScale={textScale}
        onTextScale={(s) => {
          setTextScale(s);
          writePref('oa-scale', String(s));
        }}
        onNewSession={newSession}
      />

      <div className="workspace">
        <ModeRail mode={mode} onMode={setMode} onQuick disabled={busy} />

        <main className="conversation">
          <div className="thread" ref={threadRef}>
            {messages.length === 0 ? (
              <EmptyState  />
            ) : (
              messages.map((msg) => (
                <Message
                  key={msg.id}
                  msg={msg}
                  busy={busy}
                  isFocused={msg.id === focusId}
                  onFocusSources={(id) => {
                    setFocusId(id);
                    setFigure(null);
                    setPanelOpen(true);
                  }}
                  onChoose={handleChoose}
                  onOpenFigure={(f) => {
                    setFigure(f);
                    setPanelOpen(true);
                  }}
                  onFeedback={handleFeedback}
                />
              ))
            )}
            {busy && <PipelineStatus stages={stages} />}
            {error && (
              <p className="notice notice--alarm" role="alert">
                {error}
              </p>
            )}
          </div>

          <div className="conversation__foot">
            <span className="conversation__mode">
              Mode: <strong>{modeLabel}</strong>
            </span>
            <Composer mode={mode} busy={busy} onSend={(t) => ask({ text: t })} />
          </div>
        </main>

        <SourcePanel
          msg={focused?.role === 'assistant' ? focused : null}
          figure={figure}
          onCloseFigure={() => setFigure(null)}
          open={panelOpen}
          onClose={() => setPanelOpen(false)}
        />
      </div>
    </div>
  );
}
