// Sample answers for UI development. Content is illustrative only —
// it is NOT taken from the real SINUMERIK manuals. Replace with backend responses.

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

export const SEED_CONVERSATION = [
  { id: 'u1', role: 'user', text: 'How do I start the machine after power-up?' },
  {
    id: 'a1',
    role: 'assistant',
    route: 'manual',
    blocks: [
      { type: 'text', text: 'After switching on, the control boots and the axes need a reference point approach before automatic operation.' },
      {
        type: 'steps',
        title: 'Startup after power-up',
        items: [
          'Turn the main switch on and wait until the HMI start screen is shown.',
          'Release the emergency stop button and press RESET to acknowledge alarm 003000.',
          'Select REF POINT mode on the machine control panel.',
          'Approach the reference point: X axis first, then Z axis.',
          'Check that both axes show the reference symbol, then select JOG or AUTO.',
        ],
      },
      { type: 'figure', ref: 'mcp', caption: 'Machine control panel: RESET, mode keys and axis keys' },
    ],
    sources: [
      { doc: 'Operating manual', section: '3.2 Switching on and referencing', page: 41 },
      { doc: 'Operating manual', section: '3.3 Machine control panel', page: 44 },
    ],
  },
  { id: 'u2', role: 'user', text: 'Alarm 25050 on X axis' },
  {
    id: 'a2',
    role: 'assistant',
    route: 'troubleshooting',
    blocks: [
      { type: 'text', text: 'Alarm 25050 (contour monitoring) means the axis did not follow the commanded position closely enough. It has several possible causes.' },
      {
        type: 'choices',
        prompt: 'Which situation matches best?',
        options: [
          { id: 'c1', label: 'During rapid traverse or fast moves', detail: 'Axis moves normally at low speed' },
          { id: 'c2', label: 'At low speed, axis sounds strained', detail: 'Uneven movement, noise or vibration' },
          { id: 'c3', label: 'On the first move after power-up', detail: 'Axis barely moves before the alarm' },
          { id: 'c4', label: 'None of these', detail: 'Describe what happened' },
        ],
      },
    ],
    sources: [{ doc: 'Service manual', section: '7.4 Axis monitoring alarms', page: 212 }],
  },
];

const CHOICE_ANSWERS = {
  c1: {
    route: 'troubleshooting',
    blocks: [
      { type: 'text', text: 'If the alarm only appears at high speed, the axis is most likely reaching its acceleration or speed limit.' },
      {
        type: 'steps',
        title: 'Check',
        items: [
          'Press RESET to acknowledge the alarm.',
          'Set feed override to 50 % and repeat the same move in JOG.',
          'If the move now runs without alarm, report it to maintenance: drive tuning or axis load needs checking.',
        ],
      },
      { type: 'warning', text: 'Do not change machine data. Parameter changes are done by service personnel only.' },
    ],
    sources: [{ doc: 'Service manual', section: '7.4.2 Contour monitoring', page: 214 }],
  },
  c2: {
    route: 'troubleshooting',
    blocks: [
      { type: 'text', text: 'Strained movement at low speed points to mechanical resistance on the axis.' },
      {
        type: 'steps',
        title: 'Check',
        items: [
          'Press emergency stop before inspecting the axis area.',
          'Look for chips or obstructions under the way covers.',
          'Check the lubrication level indicator and the last lubrication alarm.',
          'Release emergency stop, press RESET and move the axis slowly in JOG.',
          'If the noise continues, stop and contact maintenance.',
        ],
      },
      { type: 'figure', ref: 'axis', caption: 'X axis way cover and lubrication point' },
    ],
    sources: [
      { doc: 'Service manual', section: '7.4.2 Contour monitoring', page: 214 },
      { doc: 'Operating manual', section: '9.1 Daily maintenance', page: 160 },
    ],
  },
  c3: {
    route: 'troubleshooting',
    blocks: [
      { type: 'text', text: 'An alarm on the very first move usually means the drive or the position measuring system is not ready.' },
      {
        type: 'steps',
        title: 'Check',
        items: [
          'Check the drive status LEDs in the electrical cabinet (maintenance only).',
          'Read the alarm list for drive or encoder alarms shown together with 25050.',
          'Switch the control off and on again once. If the alarm returns, contact maintenance.',
        ],
      },
    ],
    sources: [{ doc: 'Service manual', section: '7.5 Drive and encoder alarms', page: 220 }],
  },
  c4: {
    route: 'troubleshooting',
    blocks: [{ type: 'text', text: 'Describe when the alarm appears: which mode, what the axis was doing, and any other alarms in the list.' }],
    sources: [],
  },
};

const MES_ANSWER = {
  route: 'mes',
  blocks: [
    { type: 'text', text: 'Cell 3 has the lowest OEE this week. Most of the loss is setup time on short orders.' },
    {
      type: 'table',
      tool: 'oee_by_work_center(week=44)',
      columns: ['Work center', 'Availability', 'Performance', 'Quality', 'OEE'],
      rows: [
        ['Cell 1 · Lathe', '88 %', '91 %', '99 %', '79 %'],
        ['Cell 2 · Mill', '84 %', '89 %', '98 %', '73 %'],
        ['Cell 3 · Lathe', '71 %', '86 %', '97 %', '59 %'],
      ],
    },
  ],
  sources: [{ doc: 'MES operations log', section: 'Week 44', page: null }],
};

const MANUAL_ANSWER = {
  route: 'manual',
  blocks: [
    { type: 'text', text: 'This is a sample answer from the operating manual. Connect the backend to get real answers.' },
  ],
  sources: [{ doc: 'Operating manual', section: '—', page: null }],
};

function pickAnswer({ mode, message, choiceId }) {
  if (choiceId) return CHOICE_ANSWERS[choiceId] ?? CHOICE_ANSWERS.c4;
  const m = message.toLowerCase();
  if (mode === 'mes' || /oee|scrap|downtime|order|setup time|work center/.test(m)) return MES_ANSWER;
  if (mode === 'troubleshooting' || /alarm|fault|error|\b\d{4,6}\b/.test(m)) return SEED_CONVERSATION[3];
  return MANUAL_ANSWER;
}

export async function mockRespond(req, onStage) {
  for (let i = 0; i < 3; i++) {
    onStage?.(i);
    await wait(450);
  }
  return structuredClone(pickAnswer(req));
}
