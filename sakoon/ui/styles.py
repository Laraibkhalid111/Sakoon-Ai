"""Sakoon UI — CSS with light/dark tokens (calm palette, DESIGN.md-aligned)."""

CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
<style>
.stApp, :root {
  --color-primary: #5B8AA6;
  --color-primary-dark: #3F6C86;
  --color-primary-light: #EAF2F6;
  --color-secondary: #8FBFA6;
  --color-secondary-dark: #6E9C84;
  --color-accent: #D9A25C;
  --color-bg: #FAF9F7;
  --color-surface: #FFFFFF;
  --color-border: #E4E1DB;
  --color-text-primary: #2B2B2B;
  --color-text-secondary: #6B6B6B;
  --color-text-inverse: #FFFFFF;
  --color-success: #4C9A6A;
  --color-success-bg: #E9F5EC;
  --color-warning: #C98A2E;
  --color-warning-bg: #FBF1E1;
  --color-error: #C1553D;
  --color-error-bg: #FBEAE6;
  --color-crisis: #B23A48;
  --color-crisis-bg: #FBE9EA;
  --color-crisis-border: #B23A48;
  --color-user-bubble: #F1F7F3;
  --color-code-bg: #F3F1EC;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 18px;
}

.stApp.sakoon-theme-dark {
  --color-primary: #7BA8BF;
  --color-primary-dark: #5B8AA6;
  --color-primary-light: #2A3640;
  --color-secondary: #8FBFA6;
  --color-secondary-dark: #6E9C84;
  --color-accent: #D9A25C;
  --color-bg: #161B20;
  --color-surface: #1E262E;
  --color-border: #323B45;
  --color-text-primary: #E8EAED;
  --color-text-secondary: #9AA3AD;
  --color-text-inverse: #161B20;
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
  --color-code-bg: #252D36;
}

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, Segoe UI, sans-serif;
  background-color: var(--color-bg) !important;
  color: var(--color-text-primary);
}

[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
  background-color: var(--color-bg) !important;
}

[data-testid="stSidebar"] {
  background-color: var(--color-surface) !important;
  border-right: 1px solid var(--color-border);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

[data-testid="stChatInput"] textarea {
  border: 1px solid var(--color-border) !important;
  border-radius: 12px !important;
  font-family: 'Inter', sans-serif;
  background: var(--color-surface) !important;
  color: var(--color-text-primary) !important;
}
[data-testid="stChatInput"] textarea:focus {
  border: 2px solid var(--color-primary) !important;
  box-shadow: 0 0 0 3px rgba(91,138,166,0.15) !important;
}
[data-testid="stChatInput"] textarea:disabled {
  opacity: 0.6 !important;
}

.stButton > button {
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  transition: background-color 0.15s ease, transform 0.15s ease !important;
  padding: 10px 20px !important;
}
.stButton > button[kind="primary"] {
  background-color: var(--color-primary) !important;
  color: var(--color-text-inverse) !important;
  border: none !important;
}
.stButton > button[kind="primary"]:hover {
  background-color: var(--color-primary-dark) !important;
  transform: translateY(-1px);
}
.stButton > button[kind="primary"]:disabled { opacity: 0.5; cursor: not-allowed !important; }
.stButton > button[kind="secondary"] {
  background: transparent !important;
  color: var(--color-primary) !important;
  border: 1px solid var(--color-primary) !important;
}
.stButton > button[kind="secondary"]:hover { background: var(--color-primary-light) !important; }

.sakoon-bubble-wrap {
  display: flex;
  align-items: flex-end;
  margin-bottom: 14px;
  animation: sakoonFadeUp 0.25s ease;
}
@keyframes sakoonFadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.sakoon-bubble-wrap.user { justify-content: flex-end; }
.sakoon-bubble-wrap.assistant { justify-content: flex-start; }

.sakoon-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  margin-right: 8px;
}

.sakoon-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  font-size: 15px;
  line-height: 1.65;
  position: relative;
  word-wrap: break-word;
}
@media (max-width: 640px) {
  .sakoon-bubble { max-width: 90% !important; }
}
.sakoon-bubble.assistant {
  background: var(--color-primary-light);
  color: var(--color-text-primary);
  border-bottom-left-radius: 4px;
}
.sakoon-bubble.user {
  background: var(--color-user-bubble);
  color: var(--color-text-primary);
  border-bottom-right-radius: 4px;
}
.sakoon-bubble.redirect {
  background: var(--color-warning-bg);
  border: 1px solid var(--color-warning);
  color: var(--color-text-primary);
  font-style: italic;
  border-radius: 10px;
  text-align: center;
  max-width: 80%;
  margin: 0 auto;
}
.sakoon-bubble.urdu {
  font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', serif;
  font-size: 17px;
  line-height: 1.8;
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
  border-radius: 8px;
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

.sakoon-bubble-col { max-width: 75%; }
.sakoon-bubble-col .sakoon-bubble { max-width: 100%; }
.sakoon-brand-mark {
  width: 32px; height: 32px; border-radius: 10px;
  background: var(--color-primary); color: #fff;
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 14px;
}

.sakoon-meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}
.sakoon-ts {
  font-size: 11px;
  color: var(--color-text-secondary);
}
.sakoon-copy-btn {
  font-size: 11px;
  color: var(--color-primary);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 2px 8px;
  cursor: pointer;
  font-family: Inter, sans-serif;
  transition: background 0.15s ease;
}
.sakoon-copy-btn:hover { background: var(--color-primary-light); }

.sakoon-typing { display: flex; gap: 5px; padding: 4px 0; }
.sakoon-typing span {
  width: 8px; height: 8px; border-radius: 50%;
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
  padding: 10px 14px;
  margin-bottom: 8px;
  border-radius: 10px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  font-size: 13px;
  animation: sakoonPulse 1.6s ease-in-out infinite;
}
@keyframes sakoonPulse {
  0%,100% { opacity: 0.75; }
  50% { opacity: 1; }
}

.sakoon-banner {
  padding: 14px 18px;
  border-radius: 10px;
  margin-bottom: 12px;
  font-size: 14px;
  line-height: 1.5;
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
  border-radius: 999px;
}
.sakoon-mood-pill {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
}
.sakoon-disclaimer {
  font-size: 11px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  text-align: center;
  padding: 12px 8px 0;
}
.sakoon-brand-title {
  font-family: Inter, sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.sakoon-brand-tag {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 0;
  margin-bottom: 16px;
}

.sakoon-coping-card {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 14px;
  padding: 16px 18px;
  margin: 8px 0 16px;
  animation: sakoonFadeUp 0.3s ease;
}
.sakoon-coping-card h3 {
  margin: 0 0 6px 0;
  font-size: 16px;
  color: var(--color-text-primary);
}
.sakoon-coping-step {
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text-primary);
  margin: 12px 0;
  padding: 12px 14px;
  background: var(--color-primary-light);
  border-radius: 10px;
}
.sakoon-coping-progress {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
"""
