const cases = [
  {
    id: 'wearable', name: 'Wearable', sub: 'Right word, right physiological moment',
    device: 'RUN / LIVE', clock: '00:18:00', metric: '170', label: 'HEART RATE • BPM',
    moment: 'Breakthrough wall detected', text: 'Those who hope in the Lord will renew their strength.',
    ref: 'Isaiah 40:31', native: 'Waits for recovery, then delivers a private haptic cue',
    attribution: 'Credential-free demo excerpt • live mode retrieves text and attribution from YouVersion',
    trace: [
      ['LOCAL PREFLIGHT', 'consent true • crisis false • cooldown clear'],
      ['GLOO V2 CONTRACT', 'need: endurance • theme: strength • tone: concise • safe: true'],
      ['YOUVERSION ROUTE', 'BSB 3034 • ISA.40.31 • passage + attribution'],
      ['DELIVERY POLICY', 'recovery window • private • 15 min cooldown']
    ]
  },
  {
    id: 'gaming', name: 'Gaming', sub: 'Meaning woven into play',
    device: 'CO-OP / MATCH', clock: '8TH ATTEMPT', metric: '08', label: 'CONSECUTIVE FAILURES',
    moment: 'Frustration pattern detected', text: 'Blessed is the one who perseveres under trial.',
    ref: 'James 1:12', native: 'Appears at respawn or round end, never mid-combat',
    attribution: 'Credential-free demo excerpt • live mode retrieves text and attribution from YouVersion',
    trace: [
      ['LOCAL PREFLIGHT', 'consent true • crisis false • cooldown clear'],
      ['GLOO V2 CONTRACT', 'need: encouragement • theme: perseverance • tone: teammate'],
      ['YOUVERSION ROUTE', 'BSB 3034 • JAS.1.12 • passage + attribution'],
      ['DELIVERY POLICY', 'respawn surface • private/team-safe • 15 min cooldown']
    ]
  },
  {
    id: 'ide', name: 'Developer IDE', sub: 'Presence in the margins',
    device: 'EDITOR / BUILD', clock: '03:14:27', metric: '27', label: 'FAILED BUILDS',
    moment: 'Long struggle, low progress', text: 'If any of you lacks wisdom, you should ask God, who gives generously.',
    ref: 'James 1:5', native: 'A dismissible margin card after the build completes',
    attribution: 'Credential-free demo excerpt • live mode retrieves text and attribution from YouVersion',
    trace: [
      ['LOCAL PREFLIGHT', 'consent true • crisis false • cooldown clear'],
      ['GLOO V2 CONTRACT', 'need: clarity • theme: wisdom • tone: calm'],
      ['YOUVERSION ROUTE', 'BSB 3034 • JAS.1.5 • passage + attribution'],
      ['DELIVERY POLICY', 'after build • private • 30 min cooldown']
    ]
  },
  {
    id: 'social', name: 'Social', sub: 'Scripture with human judgment',
    device: 'COMMUNITY / LIVE', clock: 'PRIVATE', metric: '!', label: 'DISTRESS SIGNAL',
    moment: 'Public response prohibited', text: 'The Lord is close to the brokenhearted.',
    ref: 'Psalm 34:18', native: 'Private moderator suggestion; never auto-posted publicly',
    attribution: 'Credential-free demo excerpt • live mode retrieves text and attribution from YouVersion',
    trace: [
      ['LOCAL PREFLIGHT', 'consent true • crisis false • public context'],
      ['GLOO V2 CONTRACT', 'need: support • theme: comfort • public: false'],
      ['YOUVERSION ROUTE', 'BSB 3034 • PSA.34.18 • passage + attribution'],
      ['DELIVERY POLICY', 'private moderator prompt • human review • 30 min cooldown']
    ]
  },
  {
    id: 'creator', name: 'Creator', sub: 'Grounding during pressure',
    device: 'STREAM / CREATOR', clock: 'LIVE 01:42', metric: '94', label: 'CHAT PRESSURE INDEX',
    moment: 'Toxicity spike detected', text: 'A gentle answer turns away wrath.',
    ref: 'Proverbs 15:1', native: 'Creator-only overlay beside chat controls',
    attribution: 'Credential-free demo excerpt • live mode retrieves text and attribution from YouVersion',
    trace: [
      ['LOCAL PREFLIGHT', 'consent true • crisis false • cooldown clear'],
      ['GLOO V2 CONTRACT', 'need: grounding • theme: restraint • tone: steady'],
      ['YOUVERSION ROUTE', 'BSB 3034 • PRO.15.1 • passage + attribution'],
      ['DELIVERY POLICY', 'creator pause • private overlay • 10 min cooldown']
    ]
  }
];

const frontiers = document.querySelector('#frontiers');
const scene = document.querySelector('#scene');
const trace = document.querySelector('#trace');
let active = 0;
let timer;

cases.forEach((item, index) => {
  const button = document.createElement('button');
  button.className = 'frontier';
  button.innerHTML = `<b>${item.name}</b><small>${item.sub}</small>`;
  button.onclick = () => render(index);
  frontiers.appendChild(button);
});

function render(index) {
  active = index;
  const item = cases[index];
  document.querySelectorAll('.frontier').forEach((node, position) => {
    node.classList.toggle('active', position === index);
  });
  document.querySelector('#deviceName').textContent = item.device;
  document.querySelector('#clock').textContent = item.clock;
  scene.innerHTML = `
    <div class="metric">${item.metric}</div>
    <div class="metric-label">${item.label}</div>
    <div class="moment">${item.moment}</div>
    <div class="verse-card"><blockquote>“${item.text}”</blockquote><b>${item.ref}</b></div>
    <div class="native">${item.native}</div>
    <div class="attribution">${item.attribution}</div>`;
  trace.innerHTML = item.trace.map(([stage, detail]) => `
    <div class="trace-item"><b>${stage}</b><span>${detail}</span></div>`).join('');
}

document.querySelector('#autoBtn').onclick = () => {
  clearInterval(timer);
  render(0);
  timer = setInterval(() => render((active + 1) % cases.length), 3200);
};

render(0);
