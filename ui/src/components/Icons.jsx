// Small stroke icons. They inherit colour from the surrounding text.
const base = {
  width: 22,
  height: 22,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  'aria-hidden': true,
};

export const IconAuto = () => (
  <svg {...base}><circle cx="12" cy="12" r="8" /><path d="M12 8v4l3 2" /></svg>
);
export const IconBook = () => (
  <svg {...base}><path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5z" /><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H13v16h5.5a1.5 1.5 0 0 0 1.5-1.5z" /></svg>
);
export const IconAlarm = () => (
  <svg {...base}><path d="M12 3 2.5 19.5h19z" /><path d="M12 10v4.5" /><path d="M12 17.2v.3" /></svg>
);
export const IconChart = () => (
  <svg {...base}><path d="M4 20V4" /><path d="M4 20h16" /><path d="M8 16v-5" /><path d="M12 16V8" /><path d="M16 16v-3" /></svg>
);
export const IconSend = () => (
  <svg {...base}><path d="M4 12h14" /><path d="m12 5 7 7-7 7" /></svg>
);
export const IconKeypad = () => (
  <svg {...base}><rect x="4" y="3" width="16" height="18" rx="2" /><path d="M8 8h.01M12 8h.01M16 8h.01M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01" strokeWidth="2.6" /></svg>
);
export const IconDoc = () => (
  <svg {...base}><path d="M6 3h8l4 4v14H6z" /><path d="M14 3v4h4" /><path d="M9 12h6M9 16h6" /></svg>
);
export const IconWarn = () => (
  <svg {...base}><path d="M12 3 2.5 19.5h19z" /><path d="M12 10v4.5" /><path d="M12 17.2v.3" /></svg>
);
export const IconCheck = () => (
  <svg {...base}><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
);
export const IconX = () => (
  <svg {...base}><path d="M6 6l12 12M18 6 6 18" /></svg>
);
export const IconSun = () => (
  <svg {...base}><circle cx="12" cy="12" r="4" /><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4" /></svg>
);
export const IconMoon = () => (
  <svg {...base}><path d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z" /></svg>
);
export const IconPlus = () => (
  <svg {...base}><path d="M12 5v14M5 12h14" /></svg>
);
export const IconTool = () => (
  <svg {...base}><path d="M14.5 5.5a4 4 0 0 0-5 5L4 16l4 4 5.5-5.5a4 4 0 0 0 5-5l-2.5 2.5-3-1-1-3z" /></svg>
);
