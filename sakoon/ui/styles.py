"""Sakoon UI — fresh aurora calm design (fancy, fast, simple)."""

CUSTOM_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Sora:wght@500;600;700&family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
<style>
.stApp, :root {
  --font: "Outfit", system-ui, sans-serif;
  --display: "Sora", "Outfit", sans-serif;
  --urdu: "Noto Nastaliq Urdu", serif;

  --primary: #0D9488;
  --primary-deep: #0F766E;
  --primary-soft: #CCFBF1;
  --accent: #38BDF8;
  --bg: #F0FDFA;
  --bg-mesh:
    radial-gradient(900px 480px at 8% -5%, #A5F3FC 0%, transparent 55%),
    radial-gradient(700px 420px at 100% 0%, #99F6E4 0%, transparent 50%),
    radial-gradient(600px 400px at 50% 100%, #E0F2FE 0%, transparent 45%),
    #F0FDFA;
  --surface: rgba(255,255,255,0.78);
  --surface-solid: #FFFFFF;
  --border: #CFFAFE;
  --text: #134E4A;
  --muted: #5B7C78;
  --inverse: #F0FDFA;
  --user-bubble: linear-gradient(145deg, #CCFBF1, #A5F3FC);
  --bot-bubble: #FFFFFF;
  --code: #ECFEFF;
  --ok: #059669;
  --ok-bg: #D1FAE5;
  --warn: #D97706;
  --warn-bg: #FEF3C7;
  --err: #DC2626;
  --err-bg: #FEE2E2;
  --crisis: #E11D48;
  --crisis-bg: #FFE4E6;
  --shadow: 0 10px 40px rgba(13, 148, 136, 0.08);
  --shadow-sm: 0 2px 10px rgba(15, 118, 110, 0.06);
  --r: 18px;
  --pill: 999px;
  --chat-max: 720px;
  --composer-w: min(var(--chat-max), 100%);
  --composer-pad-x: 0.85rem;
  --bubble-max: min(78%, 560px);
  --avatar-size: 34px;
  --input-min-h: 48px;
  --voice-row-h: 52px;

  /* legacy aliases used across the app */
  --color-primary: var(--primary);
  --color-primary-dark: var(--primary-deep);
  --color-primary-light: var(--primary-soft);
  --color-secondary: #2DD4BF;
  --color-secondary-dark: #14B8A6;
  --color-accent: var(--accent);
  --color-bg: var(--bg);
  --color-surface: var(--surface-solid);
  --color-border: var(--border);
  --color-text-primary: var(--text);
  --color-text-secondary: var(--muted);
  --color-text-inverse: var(--inverse);
  --color-success: var(--ok);
  --color-success-bg: var(--ok-bg);
  --color-warning: var(--warn);
  --color-warning-bg: var(--warn-bg);
  --color-error: var(--err);
  --color-error-bg: var(--err-bg);
  --color-crisis: var(--crisis);
  --color-crisis-bg: var(--crisis-bg);
  --color-crisis-border: var(--crisis);
  --color-user-bubble: #CCFBF1;
  --color-assistant-bubble: var(--bot-bubble);
  --color-code-bg: var(--code);
  --radius-sm: 12px;
  --radius-md: 16px;
  --radius-lg: var(--r);
  --radius-pill: var(--pill);
  --sakoon-font: var(--font);
  --sakoon-display: var(--display);
  --sakoon-urdu: var(--urdu);
}

.stApp.sakoon-theme-dark {
  --primary: #2DD4BF;
  --primary-deep: #14B8A6;
  --primary-soft: #134E4A;
  --accent: #7DD3FC;
  --bg: #042F2E;
  --bg-mesh:
    radial-gradient(800px 400px at 0% 0%, #115E59 0%, transparent 55%),
    radial-gradient(700px 380px at 100% 10%, #0C4A6E 0%, transparent 50%),
    #042F2E;
  --surface: rgba(15, 64, 61, 0.75);
  --surface-solid: #0F3D3A;
  --border: #115E59;
  --text: #ECFDF5;
  --muted: #99F6E4;
  --inverse: #042F2E;
  --user-bubble: linear-gradient(145deg, #115E59, #0E7490);
  --bot-bubble: #0F3D3A;
  --code: #134E4A;
  --ok: #34D399;
  --ok-bg: #064E3B;
  --warn: #FBBF24;
  --warn-bg: #78350F;
  --err: #FB7185;
  --err-bg: #4C0519;
  --crisis: #FB7185;
  --crisis-bg: #4C0519;
  --shadow: 0 12px 40px rgba(0,0,0,0.35);
  --shadow-sm: 0 2px 12px rgba(0,0,0,0.25);
  --color-primary: var(--primary);
  --color-primary-dark: var(--primary-deep);
  --color-primary-light: var(--primary-soft);
  --color-bg: var(--bg);
  --color-surface: var(--surface-solid);
  --color-border: var(--border);
  --color-text-primary: var(--text);
  --color-text-secondary: var(--muted);
  --color-text-inverse: var(--inverse);
  --color-user-bubble: #115E59;
  --color-assistant-bubble: var(--bot-bubble);
  --color-code-bg: var(--code);
  --color-success: var(--ok);
  --color-success-bg: var(--ok-bg);
  --color-warning: var(--warn);
  --color-warning-bg: var(--warn-bg);
  --color-error: var(--err);
  --color-error-bg: var(--err-bg);
  --color-crisis: var(--crisis);
  --color-crisis-bg: var(--crisis-bg);
  --color-crisis-border: var(--crisis);
}

html, body, [class*="css"], .stApp {
  font-family: var(--font) !important;
  background: var(--bg-mesh) !important;
  color: var(--text);
  -webkit-font-smoothing: antialiased;
}
[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: transparent !important; }

[data-testid="stSidebar"] {
  background: var(--surface) !important;
  backdrop-filter: blur(18px) saturate(1.25);
  border-right: 1px solid var(--border);
  min-width: 260px !important;
  max-width: 300px !important;
  width: 280px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 1rem 0.85rem; }

section.main .block-container {
  max-width: var(--chat-max);
  padding-top: 1rem;
  padding-bottom: 6.25rem;
  padding-left: var(--composer-pad-x);
  padding-right: var(--composer-pad-x);
  transition: max-width .2s ease;
}
/* Chat-first Claude column vs wider wellness/insights rooms */
.stApp.sakoon-view-chat section.main .block-container { max-width: var(--chat-max); }
.stApp.sakoon-view-wellness section.main .block-container,
.stApp.sakoon-view-insights section.main .block-container {
  max-width: min(960px, 94vw);
}

/* Keep bottom chat dock the same width as the message column */
.stApp.sakoon-view-chat [data-testid="stBottomBlockContainer"] {
  padding-left: var(--composer-pad-x) !important;
  padding-right: var(--composer-pad-x) !important;
}
.stApp.sakoon-view-chat [data-testid="stBottomBlockContainer"] > div {
  max-width: var(--chat-max) !important;
  width: 100% !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

[data-testid="stChatInput"] {
  max-width: var(--composer-w);
  width: 100%;
  margin: 0 auto;
}
[data-testid="stChatInput"] textarea {
  border: 1.5px solid var(--border) !important;
  border-radius: 22px !important;
  font-family: var(--font) !important;
  background: var(--surface-solid) !important;
  color: var(--text) !important;
  box-shadow: var(--shadow) !important;
  min-height: var(--input-min-h) !important;
  max-height: 160px !important;
  padding: 12px 16px !important;
}
[data-testid="stChatInput"] textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 4px rgba(13,148,136,0.18) !important;
}
[data-testid="stChatInput"] textarea:disabled { opacity: 0.55 !important; }

/* Composer rail: Latest / voice / stop share chat column width */
.sakoon-composer-rail {
  max-width: var(--composer-w);
  width: 100%;
  margin: 0.15rem auto 0.35rem;
}
.sakoon-composer-rail .stButton > button {
  min-height: 34px !important;
  padding: 0.25rem 0.7rem !important;
  font-size: 12.5px !important;
}
.sakoon-voice-rail [data-testid="stVerticalBlockBorderWrapper"] {
  max-width: 100% !important;
  width: 100% !important;
  border-radius: 16px !important;
  border-color: var(--border) !important;
  background: var(--surface-solid) !important;
  box-shadow: var(--shadow-sm) !important;
  padding: 0.45rem 0.65rem 0.55rem !important;
}
.sakoon-voice-rail [data-testid="stVerticalBlockBorderWrapper"] > div {
  gap: 0.35rem !important;
}
.sakoon-voice-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem 0.65rem;
  margin: 0 0 0.15rem;
  line-height: 1.35;
}
.sakoon-voice-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: .01em;
}
.sakoon-voice-hint {
  font-size: 12px;
  color: var(--muted);
}
.sakoon-voice-rail [data-testid="stAudioInput"] {
  width: 100% !important;
  max-width: 100% !important;
}
.sakoon-voice-rail [data-testid="stAudioInput"] > div,
.sakoon-voice-rail [data-testid="stAudioInput"] section {
  min-height: var(--voice-row-h) !important;
  max-height: 64px !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}
.sakoon-voice-rail [data-testid="stAudioInput"] label,
.sakoon-voice-rail [data-testid="stAudioInput"] p {
  margin: 0 !important;
}
.sakoon-voice-rail textarea {
  min-height: 72px !important;
  max-height: 120px !important;
}

.stTextInput input, .stTextArea textarea, .stNumberInput input {
  border-radius: 14px !important;
  border-color: var(--border) !important;
  background: var(--surface-solid) !important;
  font-family: var(--font) !important;
}

.stButton > button {
  border-radius: 14px !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  transition: transform .15s ease, box-shadow .15s ease, background .15s ease !important;
  box-shadow: var(--shadow-sm);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #14B8A6 0%, #0D9488 55%, #0891B2 100%) !important;
  color: white !important;
  border: none !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}
.stButton > button[kind="secondary"] {
  background: var(--surface-solid) !important;
  color: var(--primary-deep) !important;
  border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
  background: var(--primary-soft) !important;
  transform: translateY(-1px);
}
div[data-testid="stHorizontalBlock"] .stButton > button {
  padding: 0.28rem 0.75rem !important;
  font-size: 12px !important;
  min-height: 30px !important;
  border-radius: 10px !important;
}

.sakoon-bubble-wrap {
  display: flex; align-items: flex-start; gap: 10px;
  margin-bottom: 8px;
  animation: sakoonIn .32s cubic-bezier(.22,1,.36,1);
}
@keyframes sakoonIn {
  from { opacity: 0; transform: translateY(10px) scale(.985); }
  to { opacity: 1; transform: none; }
}
.sakoon-bubble-wrap.user { justify-content: flex-end; }
.sakoon-bubble-wrap.assistant { justify-content: flex-start; }

.sakoon-avatar {
  width: var(--avatar-size); height: var(--avatar-size); border-radius: 12px;
  background: linear-gradient(145deg, #2DD4BF, #0D9488);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; flex-shrink: 0; margin-top: 2px;
  box-shadow: var(--shadow-sm);
}
.sakoon-avatar.user-avatar {
  background: linear-gradient(145deg, #38BDF8, #0EA5E9);
}

.sakoon-bubble-col { max-width: var(--bubble-max); }
.sakoon-bubble-col.user { display: flex; flex-direction: column; align-items: flex-end; }
.sakoon-bubble-col .sakoon-bubble { max-width: 100%; }

.sakoon-bubble {
  padding: 12px 16px; border-radius: 20px;
  font-size: 15px; line-height: 1.58;
  word-wrap: break-word; box-shadow: var(--shadow-sm);
}
@media (max-width: 640px) {
  .sakoon-bubble-col { max-width: 92% !important; }
  :root { --bubble-max: 92%; }
}

.sakoon-bubble.assistant {
  background: var(--bot-bubble);
  border: 1px solid var(--border);
  color: var(--text);
  border-bottom-left-radius: 8px;
}
.sakoon-bubble.user {
  background: var(--user-bubble);
  color: var(--text);
  border: 1px solid transparent;
  border-bottom-right-radius: 8px;
}
.sakoon-bubble.redirect {
  background: var(--warn-bg); border: 1px solid var(--warn);
  font-style: italic; text-align: center; max-width: 85%; margin: 0 auto;
  border-radius: 16px;
}
.sakoon-bubble.urdu {
  font-family: var(--urdu); font-size: 17px; line-height: 1.85;
  direction: rtl; text-align: right;
}
.sakoon-bubble p { margin: 0 0 .5em; }
.sakoon-bubble p:last-child { margin: 0; }
.sakoon-bubble ul, .sakoon-bubble ol { margin: .35em 0 .35em 1.1em; }
.sakoon-bubble code {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  background: var(--code); padding: 1px 6px; border-radius: 6px; font-size: .9em;
}
.sakoon-bubble pre {
  background: var(--code); border: 1px solid var(--border);
  border-radius: 12px; padding: 10px 12px; overflow-x: auto; margin: .45em 0;
}
.sakoon-bubble pre code { background: transparent; padding: 0; }

.sakoon-table-wrap { overflow-x: auto; margin: .45em 0; }
.sakoon-md-table { width: 100%; border-collapse: collapse; font-size: .92em; }
.sakoon-md-table th, .sakoon-md-table td {
  border: 1px solid var(--border); padding: 6px 10px; text-align: left;
}
.sakoon-md-table th { background: var(--code); font-weight: 600; }

.sakoon-meta-row {
  display: flex; align-items: center; gap: 10px;
  margin-top: 2px; min-height: 28px;
}
.sakoon-ts { font-size: 11px; color: var(--muted); font-weight: 500; }

.sakoon-voice-badge {
  display: inline-block; font-size: 10px; font-weight: 700;
  letter-spacing: .05em; text-transform: uppercase;
  color: var(--primary-deep); background: var(--primary-soft);
  border-radius: var(--pill); padding: 2px 8px; margin-right: 6px;
}

.sakoon-typing { display: flex; gap: 5px; padding: 2px 0; }
.sakoon-typing span {
  width: 7px; height: 7px; border-radius: 50%; background: var(--primary);
  animation: blink 1.15s infinite;
}
.sakoon-typing span:nth-child(2) { animation-delay: .18s; }
.sakoon-typing span:nth-child(3) { animation-delay: .36s; }
@keyframes blink {
  0%,100% { opacity: .35; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-3px); }
}

.sakoon-thinking-bar {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; margin-bottom: 12px;
  border-radius: 16px; background: var(--primary-soft);
  border: 1px solid var(--border); color: var(--primary-deep);
  font-size: 13px; font-weight: 500; box-shadow: var(--shadow-sm);
}

.sakoon-banner {
  padding: 14px 18px; border-radius: 16px; margin-bottom: 12px;
  font-size: 14px; line-height: 1.5; box-shadow: var(--shadow-sm);
}
.sakoon-banner.error { background: var(--err-bg); border: 1px solid var(--err); }
.sakoon-banner.warning { background: var(--warn-bg); border: 1px solid var(--warn); }
.sakoon-banner.success { background: var(--ok-bg); border: 1px solid var(--ok); }
.sakoon-banner.crisis {
  background: var(--crisis-bg); border: 2px solid var(--crisis);
  position: sticky; top: 0; z-index: 100;
}

.sakoon-lang-badge, .sakoon-mood-pill {
  display: inline-block; padding: 6px 12px; border-radius: var(--pill);
  background: var(--primary-soft); color: var(--primary-deep);
  font-size: 12px; font-weight: 600;
}

.sakoon-brand-mark {
  width: 40px; height: 40px; border-radius: 14px;
  background: linear-gradient(145deg, #2DD4BF, #0284C7);
  color: #fff; display: inline-flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 16px; box-shadow: var(--shadow);
}
.sakoon-brand-title {
  font-family: var(--display); font-size: 1.35rem; font-weight: 700;
  letter-spacing: -.03em; color: var(--text);
}
.sakoon-brand-tag { font-size: 12.5px; color: var(--muted); margin: 2px 0 16px; }

.sakoon-chat-intro {
  text-align: center; margin: 0.35rem auto 1.25rem; max-width: 28rem;
}
.sakoon-chat-eyebrow {
  font-size: 11px; font-weight: 700; letter-spacing: .12em;
  text-transform: uppercase; color: var(--muted); margin: 0 0 .35rem;
}
.sakoon-chat-hint {
  margin: 0; font-size: 14.5px; line-height: 1.55; color: var(--muted);
}

.sakoon-copy-btn {
  font-family: var(--font) !important; font-size: 12px !important; font-weight: 600 !important;
  color: var(--primary-deep) !important; background: var(--primary-soft) !important;
  border: 1px solid var(--border) !important; border-radius: 10px !important;
  padding: 4px 10px !important; cursor: pointer !important;
}
.sakoon-copy-btn:hover { filter: brightness(0.97); }

.sakoon-panel, .sakoon-coping-card, .sakoon-history-card, .sakoon-resource-card {
  background: var(--surface-solid); border: 1px solid var(--border);
  border-radius: 20px; padding: 1.15rem 1.25rem; box-shadow: var(--shadow-sm);
  margin-bottom: 1rem;
}
.sakoon-page-hero { margin-bottom: 1.1rem; }
.sakoon-page-hero h2 {
  font-family: var(--display); font-size: 1.7rem; font-weight: 700;
  letter-spacing: -.03em; margin: 0 0 .3rem; color: var(--text);
}
.sakoon-page-hero p { margin: 0; color: var(--muted); }
.sakoon-nav-label {
  font-size: 11px; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted); margin: .4rem 0 .3rem;
}
.sakoon-history-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: 14px; border: 1px solid var(--border);
  background: var(--bg); margin-bottom: 8px; font-size: 13px;
}
.sakoon-history-score { font-weight: 700; color: var(--primary-deep); min-width: 42px; }
.sakoon-history-prompt { font-size: 12px; color: var(--muted); margin: 6px 0; }
.sakoon-history-body { font-size: 14px; line-height: 1.55; white-space: pre-wrap; }
.sakoon-resource-card p { margin: 6px 0 0; font-size: 14px; }
.sakoon-coping-card h3 { font-family: var(--display); margin: 0 0 6px; }
.sakoon-coping-step {
  margin: 12px 0; padding: 14px 16px; border-radius: 14px;
  background: var(--primary-soft); line-height: 1.6;
}
.sakoon-coping-progress { font-size: 12px; color: var(--muted); margin-bottom: 8px; }
.sakoon-disclaimer { font-size: 11px; color: var(--muted); text-align: center; padding-top: 12px; }

.sakoon-scroll-fab {
  position: fixed; right: 22px; bottom: 96px; z-index: 60;
}

.stTabs [data-baseweb="tab"] {
  border-radius: var(--pill) !important; padding: 8px 14px !important; font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
  background: var(--primary-soft) !important; color: var(--primary-deep) !important;
}

/* Sidebar nav feels like one segmented control */
[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:has(button[kind]) {
  gap: 0.35rem !important;
}
[data-testid="stSidebar"] .stButton > button {
  min-height: 38px !important;
}

/* Dark-mode Streamlit chrome */
.stApp.sakoon-theme-dark [data-testid="stExpander"] {
  background: var(--surface-solid) !important;
  border-color: var(--border) !important;
}
.stApp.sakoon-theme-dark [data-testid="stMetricValue"],
.stApp.sakoon-theme-dark [data-testid="stMetricLabel"],
.stApp.sakoon-theme-dark label,
.stApp.sakoon-theme-dark .stMarkdown,
.stApp.sakoon-theme-dark .stCaption {
  color: var(--text) !important;
}
.stApp.sakoon-theme-dark .stSelectbox > div > div,
.stApp.sakoon-theme-dark [data-baseweb="select"] > div {
  background: var(--surface-solid) !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
}
.stApp.sakoon-theme-dark [data-testid="stChatInput"] textarea {
  background: var(--surface-solid) !important;
  color: var(--text) !important;
}

/* Mobile: denser sidebar, larger tap targets, safe chat padding */
@media (max-width: 768px) {
  section.main .block-container {
    padding-top: 0.75rem !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
    padding-bottom: 5.75rem !important;
  }
  [data-testid="stSidebar"] {
    min-width: 100% !important;
    max-width: 100% !important;
    width: 100% !important;
  }
  [data-testid="stSidebar"] > div:first-child { padding: 0.85rem 0.7rem !important; }
  .sakoon-brand-title { font-size: 1.2rem !important; }
  .sakoon-page-hero h2 { font-size: 1.4rem !important; }
  .sakoon-bubble { font-size: 15px !important; padding: 12px 14px !important; }
  .sakoon-avatar { width: 32px; height: 32px; border-radius: 12px; font-size: 12px; }
  [data-testid="stSidebar"] .stButton > button {
    min-height: 42px !important;
    font-size: 13px !important;
  }
  .sakoon-scroll-fab { right: 14px; bottom: 88px; }
  [data-testid="stChatInput"] { padding-bottom: env(safe-area-inset-bottom, 0); }
  .sakoon-composer-rail { margin-bottom: 0.25rem; }
  .sakoon-voice-rail [data-testid="stAudioInput"] > div,
  .sakoon-voice-rail [data-testid="stAudioInput"] section {
    max-height: 72px !important;
  }
}

@media (max-width: 480px) {
  .sakoon-bubble-col { max-width: 94% !important; }
  .sakoon-meta-row { gap: 6px; }
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
"""
