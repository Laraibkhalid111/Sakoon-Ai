"""Sakoon UI — premium calm design system (light/dark tokens)."""

# Fonts: Plus Jakarta Sans (UI) + Fraunces (brand) — not Inter/system defaults.
CUSTOM_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
<style>
/* ── Design tokens ───────────────────────────────────────────────────────── */
.stApp, :root {
  --sakoon-font: "Plus Jakarta Sans", "Segoe UI", sans-serif;
  --sakoon-display: "Fraunces", Georgia, serif;
  --sakoon-urdu: "Noto Nastaliq Urdu", "Jameel Noori Nastaleeq", serif;

  --color-primary: #3D7A6F;
  --color-primary-dark: #2F5F57;
  --color-primary-light: #E7F2EF;
  --color-secondary: #7FA994;
  --color-secondary-dark: #5E8573;
  --color-accent: #C4A574;
  --color-bg: #F3F6F5;
  --color-bg-glow: radial-gradient(1200px 600px at 10% -10%, #E4F0EC 0%, transparent 55%),
                   radial-gradient(900px 500px at 100% 0%, #EDE8E1 0%, transparent 50%),
                   var(--color-bg);
  --color-surface: rgba(255, 255, 255, 0.82);
  --color-surface-solid: #FFFFFF;
  --color-border: #D7E0DC;
  --color-text-primary: #1C2422;
  --color-text-secondary: #5C6B66;
  --color-text-inverse: #F7FBFA;
  --color-success: #3F8F6B;
  --color-success-bg: #E6F5EE;
  --color-warning: #B8832F;
  --color-warning-bg: #F8F0E2;
  --color-error: #B85A4A;
  --color-error-bg: #F8EBE8;
  --color-crisis: #A83D4A;
  --color-crisis-bg: #F8E8EA;
  --color-crisis-border: #A83D4A;
  --color-user-bubble: #EAF3EF;
  --color-assistant-bubble: #FFFFFF;
  --color-code-bg: #EEF2F0;
  --shadow-sm: 0 1px 2px rgba(28, 36, 34, 0.04);
  --shadow-md: 0 8px 24px rgba(28, 36, 34, 0.06);
  --shadow-lg: 0 16px 40px rgba(28, 36, 34, 0.08);
  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-pill: 999px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --glass: blur(14px) saturate(1.2);
  --chat-max: 820px;
}

.stApp.sakoon-theme-dark {
  --color-primary: #6BA89A;
  --color-primary-dark: #4E8B7E;
  --color-primary-light: #243330;
  --color-secondary: #7FA994;
  --color-secondary-dark: #5E8573;
  --color-accent: #C4A574;
  --color-bg: #121816;
  --color-bg-glow: radial-gradient(1000px 500px at 0% 0%, #1A2A26 0%, transparent 55%),
                   radial-gradient(800px 400px at 100% 0%, #1E1C18 0%, transparent 50%),
                   var(--color-bg);
  --color-surface: rgba(26, 34, 32, 0.88);
  --color-surface-solid: #1A2220;
  --color-border: #2E3A36;
  --color-text-primary: #E8EEEB;
  --color-text-secondary: #9AABA4;
  --color-text-inverse: #121816;
  --color-success: #6BB589;
  --color-success-bg: #1E3328;
  --color-warning: #D4A04A;
  --color-warning-bg: #3A2E1A;
  --color-error: #D47A6A;
  --color-error-bg: #3A2422;
  --color-crisis: #E07A86;
  --color-crisis-bg: #3A2226;
  --color-crisis-border: #E07A86;
  --color-user-bubble: #243028;
  --color-assistant-bubble: #1E2624;
  --color-code-bg: #222B28;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.25);
  --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.28);
  --shadow-lg: 0 16px 40px rgba(0, 0, 0, 0.35);
}

/* ── App shell ───────────────────────────────────────────────────────────── */
html, body, [class*="css"], .stApp {
  font-family: var(--sakoon-font) !important;
  background: var(--color-bg-glow) !important;
  color: var(--color-text-primary);
  -webkit-font-smoothing: antialiased;
}

[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
  background: transparent !important;
}
[data-testid="stHeader"] {
  backdrop-filter: var(--glass);
}

[data-testid="stSidebar"] {
  background: var(--color-surface) !important;
  backdrop-filter: var(--glass);
  border-right: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}
[data-testid="stSidebar"] > div:first-child {
  padding-top: 1.25rem;
  padding-left: 0.85rem;
  padding-right: 0.85rem;
}

section.main .block-container {
  max-width: var(--chat-max);
  padding-top: 1.5rem;
  padding-bottom: 6rem;
}

/* ── Inputs ──────────────────────────────────────────────────────────────── */
[data-testid="stChatInput"] {
  max-width: var(--chat-max);
  margin: 0 auto;
}
[data-testid="stChatInput"] textarea {
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-lg) !important;
  font-family: var(--sakoon-font) !important;
  background: var(--color-surface-solid) !important;
  color: var(--color-text-primary) !important;
  box-shadow: var(--shadow-sm) !important;
  min-height: 48px !important;
}
[data-testid="stChatInput"] textarea:focus {
  border: 1.5px solid var(--color-primary) !important;
  box-shadow: 0 0 0 4px rgba(61, 122, 111, 0.14) !important;
}
[data-testid="stChatInput"] textarea:disabled {
  opacity: 0.55 !important;
}

.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div,
.stNumberInput input {
  border-radius: var(--radius-sm) !important;
  border-color: var(--color-border) !important;
  font-family: var(--sakoon-font) !important;
  background: var(--color-surface-solid) !important;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.stButton > button {
  border-radius: var(--radius-sm) !important;
  font-family: var(--sakoon-font) !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em;
  transition: background-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease !important;
  padding: 0.55rem 1.1rem !important;
  box-shadow: var(--shadow-sm);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(180deg, #4A8B7F 0%, var(--color-primary) 100%) !important;
  color: var(--color-text-inverse) !important;
  border: none !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--color-primary-dark) !important;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.stButton > button[kind="primary"]:disabled { opacity: 0.5; cursor: not-allowed !important; }
.stButton > button[kind="secondary"] {
  background: var(--color-surface-solid) !important;
  color: var(--color-primary) !important;
  border: 1px solid var(--color-border) !important;
}
.stButton > button[kind="secondary"]:hover {
  background: var(--color-primary-light) !important;
  border-color: var(--color-primary) !important;
  transform: translateY(-1px);
}

/* Compact action buttons (Copy / Regenerate) */
div[data-testid="stHorizontalBlock"] .stButton > button {
  padding: 0.25rem 0.7rem !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  min-height: 28px !important;
  border-radius: 8px !important;
}

/* ── Chat bubbles ────────────────────────────────────────────────────────── */
.sakoon-bubble-wrap {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 6px;
  animation: sakoonFadeUp 0.28s ease;
}
@keyframes sakoonFadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.sakoon-bubble-wrap.user { justify-content: flex-end; }
.sakoon-bubble-wrap.assistant { justify-content: flex-start; }

.sakoon-avatar {
  width: 34px; height: 34px;
  border-radius: 12px;
  background: linear-gradient(145deg, #4A8B7F, var(--color-primary-dark));
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 2px;
  box-shadow: var(--shadow-sm);
}
.sakoon-avatar.user-avatar {
  background: linear-gradient(145deg, #8FB5A8, #5E8573);
  order: 2;
  margin-left: 0;
}

.sakoon-bubble-col { max-width: min(75%, 640px); }
.sakoon-bubble-col.user { display: flex; flex-direction: column; align-items: flex-end; }
.sakoon-bubble-col .sakoon-bubble { max-width: 100%; }

.sakoon-bubble {
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  font-size: 15px;
  line-height: 1.65;
  position: relative;
  word-wrap: break-word;
  box-shadow: var(--shadow-sm);
}
@media (max-width: 640px) {
  .sakoon-bubble-col { max-width: 92% !important; }
}
.sakoon-bubble.assistant {
  background: var(--color-assistant-bubble);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-bottom-left-radius: 6px;
}
.sakoon-bubble.user {
  background: var(--color-user-bubble);
  color: var(--color-text-primary);
  border: 1px solid transparent;
  border-bottom-right-radius: 6px;
}
.sakoon-bubble.redirect {
  background: var(--color-warning-bg);
  border: 1px solid var(--color-warning);
  color: var(--color-text-primary);
  font-style: italic;
  border-radius: var(--radius-md);
  text-align: center;
  max-width: 80%;
  margin: 0 auto;
  box-shadow: none;
}
.sakoon-bubble.urdu {
  font-family: var(--sakoon-urdu);
  font-size: 17px;
  line-height: 1.85;
  direction: rtl;
  text-align: right;
}
.sakoon-bubble p { margin: 0 0 0.55em 0; }
.sakoon-bubble p:last-child { margin-bottom: 0; }
.sakoon-bubble ul, .sakoon-bubble ol { margin: 0.4em 0 0.4em 1.1em; padding: 0; }
.sakoon-bubble code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.9em;
  background: var(--color-code-bg);
  padding: 1px 6px;
  border-radius: 4px;
}
.sakoon-bubble pre {
  background: var(--color-code-bg);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 10px 12px;
  overflow-x: auto;
  margin: 0.5em 0;
}
.sakoon-bubble pre code { background: transparent; padding: 0; }

.sakoon-table-wrap { overflow-x: auto; margin: 0.5em 0; }
.sakoon-md-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92em;
}
.sakoon-md-table th, .sakoon-md-table td {
  border: 1px solid var(--color-border);
  padding: 6px 10px;
  text-align: left;
}
.sakoon-md-table th { background: var(--color-code-bg); font-weight: 600; }

.sakoon-meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 2px;
  min-height: 28px;
}
.sakoon-ts {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.sakoon-typing { display: flex; gap: 5px; padding: 4px 0; }
.sakoon-typing span {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--color-primary);
  animation: sakoonBlink 1.2s infinite;
}
.sakoon-typing span:nth-child(2) { animation-delay: 0.2s; }
.sakoon-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes sakoonBlink {
  0%,100% { opacity: 0.3; transform: translateY(0); }
  50%      { opacity: 1; transform: translateY(-2px); }
}

.sakoon-thinking-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  margin-bottom: 12px;
  border-radius: var(--radius-md);
  background: var(--color-primary-light);
  border: 1px solid var(--color-border);
  color: var(--color-primary-dark);
  font-size: 13px;
  font-weight: 500;
  animation: sakoonPulse 1.6s ease-in-out infinite;
  box-shadow: var(--shadow-sm);
}
@keyframes sakoonPulse {
  0%,100% { opacity: 0.8; }
  50% { opacity: 1; }
}

.sakoon-banner {
  padding: 14px 18px;
  border-radius: var(--radius-md);
  margin-bottom: 12px;
  font-size: 14px;
  line-height: 1.5;
  box-shadow: var(--shadow-sm);
}
.sakoon-banner.error   { background: var(--color-error-bg);   border: 1px solid var(--color-error); }
.sakoon-banner.warning { background: var(--color-warning-bg); border: 1px solid var(--color-warning); }
.sakoon-banner.success { background: var(--color-success-bg); border: 1px solid var(--color-success); }
.sakoon-banner.crisis  {
  background: var(--color-crisis-bg);
  border: 2px solid var(--color-crisis-border);
  font-size: 15px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.sakoon-lang-badge {
  display: inline-block;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-weight: 600;
}
.sakoon-mood-pill {
  display: inline-block;
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  font-size: 13px;
  box-shadow: var(--shadow-sm);
}
.sakoon-disclaimer {
  font-size: 11px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  text-align: center;
  padding: 12px 8px 0;
}

.sakoon-brand-mark {
  width: 36px; height: 36px; border-radius: 12px;
  background: linear-gradient(145deg, #4A8B7F, var(--color-primary-dark));
  color: #fff;
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 15px;
  font-family: var(--sakoon-font);
  box-shadow: var(--shadow-md);
}
.sakoon-brand-title {
  font-family: var(--sakoon-display);
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}
.sakoon-brand-tag {
  font-size: 12.5px;
  color: var(--color-text-secondary);
  margin-top: 2px;
  margin-bottom: 18px;
}

.sakoon-auth-shell {
  max-width: 420px;
  margin: 2.5rem auto 1rem;
  padding: 1.75rem 1.5rem 1.25rem;
  background: var(--color-surface);
  backdrop-filter: var(--glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}
.sakoon-auth-shell h3 {
  font-family: var(--sakoon-display);
  font-weight: 600;
  letter-spacing: -0.02em;
  margin-bottom: 0.35rem;
}

.sakoon-panel {
  background: var(--color-surface-solid);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-4);
}
.sakoon-panel h2, .sakoon-panel h3 {
  font-family: var(--sakoon-display);
  letter-spacing: -0.02em;
}

.sakoon-coping-card {
  border: 1px solid var(--color-border);
  background: var(--color-surface-solid);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  margin: 8px 0 16px;
  box-shadow: var(--shadow-md);
  animation: sakoonFadeUp 0.3s ease;
}
.sakoon-coping-card h3 {
  margin: 0 0 6px 0;
  font-size: 17px;
  font-family: var(--sakoon-display);
  color: var(--color-text-primary);
}
.sakoon-coping-step {
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text-primary);
  margin: 12px 0;
  padding: 14px 16px;
  background: var(--color-primary-light);
  border-radius: var(--radius-md);
}
.sakoon-coping-progress {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}

/* Tabs / forms polish */
.stTabs [data-baseweb="tab-list"] {
  gap: 6px;
  background: transparent;
}
.stTabs [data-baseweb="tab"] {
  border-radius: var(--radius-pill) !important;
  padding: 8px 14px !important;
  font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
  background: var(--color-primary-light) !important;
  color: var(--color-primary-dark) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
"""
