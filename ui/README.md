# Operator Assistant UI (first draft)

React + plain CSS front end for the shop-floor assistant. Runs as a web app and is
designed to be shown full-screen (kiosk browser) or inside a native window wrapper
(Tauri / Electron / pywebview).

## Run

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # static files in dist/ — FastAPI can serve these directly
```

## Structure

```
src/
  App.jsx                 state: messages, mode, pipeline stage, focused answer
  api/client.js           POST /api/chat — response contract documented at the top
  api/mockData.js         sample answers (USE_MOCK = true in client.js)
  components/
    StatusBar.jsx         station, server status, text size, day/night, clock
    ModeRail.jsx          Auto / Manual / Alarm & fault / Production data + common questions
    Message.jsx           answer blocks: text, steps, warning, figure, choices, table
    Composer.jsx          text input + alarm-code keypad
    SourcePanel.jsx       sources (doc, section, page) and enlarged figures
    Figure.jsx            manual images (src from backend) or schematic placeholders
  styles/tokens.css       colour, type and size tokens, light + dark
  styles/app.css          layout and components
```

## Connecting the backend

1. Set `USE_MOCK = false` in `src/api/client.js`.
2. Expose `POST /api/chat` from FastAPI. The Vite dev server proxies `/api` to `localhost:8000`.
3. Return `{ route, blocks, sources }`. Each LangGraph node decides which blocks it emits:
   - manual node → `text`, `steps`, `figure` (image URL from the PDF extraction)
   - troubleshooting node → `text` + `choices` when an alarm has several causes; the tapped
     option comes back as `choice_id` in the next request
   - MES node → `text` + `table` with the name of the deterministic tool that computed it
4. Optional: replace the fake pipeline stages with Server-Sent Events from the graph nodes.

## Design notes

- Grey, low-saturation palette following high-performance HMI practice (ISA-101): colour is
  reserved for alarm, warning and OK states, plus one blue accent for anything pressable.
- Touch targets at least 3.5 rem (56 px), numbered choice cards and a numeric keypad so
  operators can use the panel with gloves.
- Every answer shows its sources and page numbers; MES numbers are labelled as calculated
  by a tool, not by the language model.
- "Solved / Not solved" feedback is captured per answer (wire to `/api/feedback` for
  evaluation data).
