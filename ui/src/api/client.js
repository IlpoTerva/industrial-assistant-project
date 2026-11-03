// API client for the operator assistant.
//
// The UI talks to ONE endpoint: POST /api/chat
// Your FastAPI backend wraps the LangGraph pipeline (router -> manual / troubleshooting / MES node)
// and returns a response in the shape documented below. While the backend isn't ready,
// USE_MOCK = true returns sample answers from mockData.js.
//
// Request:
//   { mode: "auto" | "manual" | "troubleshooting" | "mes",
//     message: string,
//     choice_id?: string,          // set when the operator taps a numbered situation card
//     session_id: string }
//
// Response:
//   { route: "manual" | "troubleshooting" | "mes",   // which LangGraph node answered
//     blocks: Block[],                               // rendered top to bottom
//     sources: { doc, section, page }[] }
//
// Block types:
//   { type: "text",    text }
//   { type: "steps",   title?, items: string[] }
//   { type: "warning", text }
//   { type: "figure",  caption, src?, ref? }         // src = image URL served by the backend
//   { type: "choices", prompt, options: { id, label, detail }[] }
//   { type: "table",   tool, columns: string[], rows: (string|number)[][] }


const API_URL = '/api/chat/stream';



// Progress labels shown while the pipeline works. With a streaming backend (SSE),
// send these as events from the LangGraph nodes instead of faking them here.

export async function sendMessage({message, sessionId, mode, choiceId}, onStage) {

  //onStage?.(0);
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
                          message,  
                          session_id: sessionId,
                          mode,
                          choice_id: choiceId ?? null
                        }),
  });
  if (!res.ok) {
    throw new Error(`The assistant server answered with status ${res.status}.`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let result = null
  while (true){
    const {value, done} = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, {stream: true});

    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines){
      if (!line.trim()) continue;
      const event = JSON.parse(line);
      if (event.type === 'stage') onStage?.(event);
      else if (event.type === 'result') result = event.data;
      else if (event.type === 'error') throw new Error(event.message)
    }
  }
  if (!result) throw new Error('The server closed connection bedore sending an answer')

  return normalize(result);
}

function normalize(data) {
  if (typeof data == 'string'){
    return {route: null, blocks: [{type: 'text', text: data}], sources: []};
  }
  return {
    route: data.route ?? null,
    blocks: Array.isArray(data.blocks) ? data.blocks : [{type: 'text', text: data.answer ?? data.text ?? JSON.stringify(data)}],
    sources: data.sources ?? [], 
  }
}
