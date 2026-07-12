# DESIGN.md — Sakoon AI — UI/UX & Visual Design Specification

This document is the single source of truth for how the product looks, feels, and behaves. It complements `IDEA.md` (which covers architecture/logic). Read both before coding. Everything here is written to be implementable directly — exact hex codes, spacing, copy, and states — so it can be handed to an AI coding agent (Antigravity) or a human without ambiguity.

---

## 1. Design Philosophy

- **Calm, not clinical.** This is a wellness companion, not a hospital intake form. Soft colors, generous whitespace, rounded corners, no harsh reds except for genuine crisis states.
- **Trustworthy, not childish.** No cartoonish illustrations. Clean typography, restrained color palette, professional spacing — this should look like it could be a real funded product, not a hackathon toy.
- **Legible in two scripts.** Urdu (Nastaliq-style) and Latin text must both render cleanly, at readable sizes, without layout breakage.
- **Never silent.** Every action (sending a message, recording voice, generating a report, sending an email) has a visible state: idle → loading → success/error. No dead air where the user wonders if something happened.
- **Crisis state visually distinct from everything else.** When the safety layer triggers, the UI must not look "the same as normal chat with different text" — it must visually signal *this is different, pay attention*.

---

## 2. Color System

### 2.1 Primary Palette

| Token | Hex | Usage |
|---|---|---|
| `--color-primary` | `#5B8AA6` | Muted teal-blue — primary buttons, active states, assistant message accent |
| `--color-primary-dark` | `#3F6C86` | Primary hover/pressed state |
| `--color-primary-light` | `#EAF2F6` | Assistant chat bubble background, subtle highlights |
| `--color-secondary` | `#8FBFA6` | Sage green — secondary actions, success accents, "calm" motif |
| `--color-secondary-dark` | `#6E9C84` | Secondary hover state |
| `--color-accent` | `#D9A25C` | Warm amber — used sparingly for gentle attention (e.g. mood pill, small highlights) |

### 2.2 Neutrals

| Token | Hex | Usage |
|---|---|---|
| `--color-bg` | `#FAF9F7` | App background — warm off-white, not stark white |
| `--color-surface` | `#FFFFFF` | Cards, sidebar, chat container |
| `--color-border` | `#E4E1DB` | Dividers, input borders |
| `--color-text-primary` | `#2B2B2B` | Main text |
| `--color-text-secondary` | `#6B6B6B` | Timestamps, helper text, placeholders |
| `--color-text-inverse` | `#FFFFFF` | Text on dark/primary backgrounds |

### 2.3 Semantic Colors

| Token | Hex | Usage |
|---|---|---|
| `--color-success` | `#4C9A6A` | Success toasts (report emailed, saved) |
| `--color-success-bg` | `#E9F5EC` | Success banner background |
| `--color-warning` | `#C98A2E` | Non-critical warnings (e.g. "email not provided") |
| `--color-warning-bg` | `#FBF1E1` | Warning banner background |
| `--color-error` | `#C1553D` | Field errors, failed actions (muted terracotta, not harsh red) |
| `--color-error-bg` | `#FBEAE6` | Error banner background |
| `--color-crisis` | `#B23A48` | Reserved *only* for the crisis alert card — deeper, more serious red |
| `--color-crisis-bg` | `#FBE9EA` | Crisis banner background |
| `--color-crisis-border` | `#B23A48` | 2px border around crisis card so it's unmistakable |

**Rule:** `--color-crisis` is never reused for ordinary form errors. If both a regular error and crisis state could visually look similar, the user's brain will pattern-match crisis alerts as "just another error" over time — that must never happen.

### 2.4 User vs Assistant Chat Bubble Colors

- **User bubble:** background `--color-secondary-dark` at 12% opacity tint → practically `#F1F7F3`, text `--color-text-primary`, aligned right, rounded corners (18px, with the bottom-right corner sharper at 4px — standard chat "tail" affordance).
- **Assistant bubble:** background `--color-primary-light` (`#EAF2F6`), text `--color-text-primary`, aligned left, rounded corners (18px, bottom-left at 4px), small assistant avatar (see §9) to the left.
- **System/redirect bubble** (off-topic redirect): background `--color-warning-bg`, italic text, centered, no avatar — visually distinct from a normal assistant reply so the user consciously registers "this was a boundary, not conversation."

---

## 3. Typography

| Role | Font | Fallback stack | Size | Weight |
|---|---|---|---|---|
| Latin body/UI | **Inter** (Google Fonts) | `-apple-system, Segoe UI, sans-serif` | 15–16px | 400 |
| Latin headings | **Inter** | same | 20–28px | 600–700 |
| Urdu text (chat + PDF) | **Noto Nastaliq Urdu** (Google Fonts) | `Jameel Noori Nastaleeq, serif` | 17–18px (Nastaliq needs slightly larger size to stay legible) | 400 |
| Monospace (rare — debug/logs only, not user-facing) | `JetBrains Mono` | `monospace` | 13px | 400 |

**Rules:**
- Detect script per message: if the text contains Arabic-range Unicode characters (Urdu script), render that specific chat bubble with the Urdu font-family and `direction: rtl; text-align: right;`. Roman Urdu (Urdu written in Latin letters) still uses the Latin font, LTR — don't force RTL on Roman Urdu.
- Line height: 1.6 for body text, 1.8 for Urdu script (taller line height needed for Nastaliq's vertical stroke style).
- Never mix font sizes within a single chat bubble.

---

## 4. Streamlit Theming Setup

### 4.1 `.streamlit/config.toml`

```toml
[theme]
base = "light"
primaryColor = "#5B8AA6"
backgroundColor = "#FAF9F7"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#2B2B2B"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[browser]
gatherUsageStats = false
```

### 4.2 Custom CSS Injection

Streamlit's built-in theming only goes so far (no hover-state control, no custom chat bubble shaping). Inject a single `<style>` block once at the top of `app.py` via `st.markdown(..., unsafe_allow_html=True)`, targeting Streamlit's stable `data-testid` selectors:

- `[data-testid="stChatMessage"]` → bubble shape/background per role (use `:has()` or nth-child alternation, or better: build bubbles manually with `st.markdown` + custom HTML/CSS divs instead of relying purely on `st.chat_message`, for full control over left/right alignment and avatar placement).
- `[data-testid="stSidebar"]` → background `--color-surface`, right border `1px solid var(--color-border)`.
- `button[kind="primary"]` → background `--color-primary`, hover `--color-primary-dark` with `transition: background-color 0.15s ease`.
- `[data-testid="stChatInput"] textarea` → border `1px solid var(--color-border)`, border-radius `12px`, focus state border `2px solid var(--color-primary)` with subtle `box-shadow: 0 0 0 3px rgba(91,138,166,0.15)`.

Load Google Fonts via a `<link>` tag in the same injected `<style>`/`<head>` block:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
```

**Recommendation for Antigravity implementation:** put all custom CSS in one constant string at the top of `app.py` (or a small `styles.py` if it gets long) — do not scatter `st.markdown(unsafe_allow_html=True)` calls throughout the file. One injection point, one source of truth.

---

## 5. Layout & Page Structure

### 5.1 Overall Grid

```
┌─────────────────────────────────────────────┐
│  SIDEBAR (fixed, ~320px)  │   MAIN CHAT AREA │
│                            │                  │
│  Logo + App Name          │  [Crisis banner  │
│  Language badge           │   — only if      │
│  ─────────────            │   triggered]     │
│  🎙️ Voice Input           │                  │
│  (expander)                │  Chat history    │
│  ─────────────            │  (scrollable)    │
│  📄 Generate Report        │                  │
│  📧 Resend to Email        │                  │
│  ─────────────            │                  │
│  Mood indicator pill       │                  │
│  ─────────────            │  Chat input bar  │
│  Disclaimer footer         │  (fixed bottom)  │
└─────────────────────────────────────────────┘
```

### 5.2 Responsive Behavior (Streamlit mobile)

- Streamlit auto-collapses the sidebar into a top hamburger on narrow viewports (<640px) — rely on this native behavior, don't fight it.
- On mobile, move the "Generate Report" and "Voice Input" actions into a horizontal button row *above* the chat if the sidebar is collapsed by default for the demo — but for the presentation, assume desktop/projector width and don't over-invest engineering time in mobile polish. Note it as a "nice-to-have" in README, not a v1 requirement.
- Chat bubbles: max-width `75%` of container on desktop, `88%` on mobile, so text wraps naturally and doesn't stretch edge-to-edge.

### 5.3 Spacing Scale

Use an 8px base unit throughout: `4, 8, 16, 24, 32, 48px`. Chat bubble internal padding: `12px 16px`. Section vertical spacing in sidebar: `24px` between groups.

---

## 6. Component Specifications

### 6.1 Header / Branding

- Top of sidebar: small circular/rounded-square logo mark (simple — e.g. a soft crescent-and-leaf or abstract calm-wave icon, single color `--color-primary`) + app name in Inter 600, 18px.
- Tagline directly beneath, 12px, `--color-text-secondary`: *"A calm space to talk"* / (Urdu equivalent shown if user's language is Urdu: "بات کرنے کی ایک پرسکون جگہ").

### 6.2 Language Badge

- Small pill, top-right of chat area or under the logo: `🌐 English` / `🌐 اردو` / `🌐 Mixed`.
- Background `--color-primary-light`, text `--color-primary-dark`, 12px font, `padding: 4px 10px`, `border-radius: 999px`.
- Updates automatically based on `detected_language` from the last Groq JSON response — no manual toggle needed, but include a manual override dropdown in sidebar as a fallback (`Auto / English / اردو`) in case auto-detection misfires.

### 6.3 Chat Message Bubbles

**Assistant message:**
```
[avatar]  ┌─────────────────────────────┐
          │  Message text here...        │
          │                    10:42 AM  │
          └─────────────────────────────┘
```
- Avatar: 32px circle, soft illustration or simple monogram on `--color-primary` background.
- Timestamp: 11px, `--color-text-secondary`, bottom-right of bubble, low emphasis.

**User message:** mirrored, right-aligned, no avatar (keeps focus on the assistant as the "presence" in the room), bubble color per §2.4.

**Voice-originated message:** small mic icon (🎙️, 12px) prefixed inside the bubble before the transcribed text, so the user can tell it was voice input at a glance, e.g.: `🎙️ mujhe kal se neend nahi aa rahi...`

**Typing/thinking indicator:** while waiting for Groq response, show an assistant bubble with 3 animated dots (`● ● ●`, staggered fade opacity 0.3→1→0.3, 1.2s loop) instead of a generic spinner — keeps it feeling conversational.

### 6.4 Chat Input Bar

- Fixed to bottom of main area, `--color-surface` background, `1px solid var(--color-border)` top border, padding `16px`.
- Text input: rounded `12px`, placeholder text (language-aware):
  - EN: `"Type how you're feeling..."`
  - UR: `"آپ کیسا محسوس کر رہے ہیں، لکھیں..."`
- Send button: circular, `--color-primary` background, white paper-plane icon, disabled (opacity 0.4, cursor not-allowed) when input is empty.
- **States:**
  - Default: border `--color-border`
  - Focus: border `--color-primary`, glow shadow (see §4.2)
  - Error (e.g. message failed to send): border `--color-error`, small inline text below field: EN `"Message couldn't be sent. Please try again."` / UR `"پیغام نہیں بھیجا جا سکا۔ دوبارہ کوشش کریں۔"`
  - Disabled while assistant is responding: input dimmed (opacity 0.6), placeholder changes to `"Sakoon is thinking..."` / `"...ساکون سوچ رہا ہے"`

### 6.5 Voice Input Widget (sidebar expander)

- Expander label: `🎙️ Voice Input` — collapsed by default, expands to reveal `st.audio_input`.
- **States:**
  - Idle: standard mic icon, helper text below: EN `"Tap to record. Speak in Urdu or English."`
  - Recording: Streamlit's native red recording indicator (built into `st.audio_input`) — leave as-is, don't fight the native widget styling here.
  - Processing (sent to Whisper): show `st.spinner("Listening carefully...")` / `("بغور سن رہے ہیں...")` beneath the widget.
  - Transcription failed (silence, no speech detected, API error): inline warning banner (see §6.8 Warning style): EN `"Couldn't catch that — could you try recording again, or type instead?"` / UR `"سمجھ نہیں آیا — دوبارہ ریکارڈ کریں یا لکھ کر بتائیں۔"`
  - Success: transcribed text auto-populates as a new chat message (per §6.3 voice bubble style), expander auto-collapses back to idle.

### 6.6 Buttons

| Variant | Default | Hover | Active/Pressed | Disabled |
|---|---|---|---|---|
| Primary (`Generate Report`) | bg `--color-primary`, text white, `border-radius: 10px`, `padding: 10px 20px` | bg `--color-primary-dark`, `transform: translateY(-1px)`, subtle shadow | `transform: translateY(0)`, shadow removed | opacity `0.5`, `cursor: not-allowed` |
| Secondary (`Resend Email`) | bg transparent, `1px solid var(--color-primary)`, text `--color-primary` | bg `--color-primary-light` | bg `--color-primary-light` darker tint | opacity `0.5` |
| Danger (rare — e.g. "Clear conversation") | bg transparent, text `--color-error`, `1px solid var(--color-error)` | bg `--color-error-bg` | same, darker | opacity `0.5` |

All buttons: `transition: all 0.15s ease`, no jarring instant color snaps.

### 6.7 Mood Indicator Pill

- Small rounded pill in sidebar, updates as `mood_rating` (1–10) is extracted from conversation.
- Color scales along a calm gradient, not alarming reds even at low mood — this is a *reflective* indicator, not a diagnostic severity meter:
  - 1–3: `--color-accent` (amber) — "Having a hard time"
  - 4–6: `--color-primary` (teal) — "Getting through it"
  - 7–10: `--color-secondary` (sage) — "Feeling steady"
- Format: `🫧 Mood today: Getting through it` (label text, not raw number — raw numeric scores feel clinical/judgmental).

### 6.8 Notification / Banner Styles

| Type | Background | Border | Icon | Example copy (EN / UR) |
|---|---|---|---|---|
| Success | `--color-success-bg` | `1px solid var(--color-success)` | ✅ | "Your report has been emailed to you." / "آپ کی رپورٹ ای میل کر دی گئی ہے۔" |
| Warning | `--color-warning-bg` | `1px solid var(--color-warning)` | ⚠️ | "We couldn't send the email, but you can download the report below." / "ای میل بھیجنا ممکن نہ ہوا، لیکن آپ نیچے سے رپورٹ ڈاؤن لوڈ کر سکتے ہیں۔" |
| Error | `--color-error-bg` | `1px solid var(--color-error)` | ❌ | "Something went wrong. Please try again in a moment." / "کچھ مسئلہ ہو گیا۔ براہ کرم دوبارہ کوشش کریں۔" |
| **Crisis** | `--color-crisis-bg` | `2px solid var(--color-crisis)` | 💙 (not a harsh warning icon — deliberately a gentle heart, tone matters here) | See §7 exact copy |

All banners: `border-radius: 10px`, `padding: 14px 18px`, positioned as a sticky element at the top of the chat area (not a dismissible toast for crisis — it should stay visible).

---

## 7. Crisis State — Exact Specification

When `safety.py` flags a message:

1. Chat area shows a **pinned card at the top**, always visible while scrolling, styled per §6.8 crisis row.
2. Copy (exact, do not let the LLM generate this — it's hard-coded):

   **English:**
   > "It sounds like you're going through something really heavy right now. You don't have to face this alone. If you're in immediate danger or thinking about harming yourself, please reach out right now:
   > 📞 Umang Mental Health Helpline (Pakistan): 0311-7786264
   > 📞 Or your local emergency number
   > I'm still here to talk with you, but please also consider reaching a person who can be there with you."

   **Urdu:**
   > "لگتا ہے آپ اس وقت کسی بہت مشکل دور سے گزر رہے ہیں۔ آپ کو یہ اکیلے نہیں سہنا۔ اگر آپ فوری خطرے میں ہیں یا خود کو نقصان پہنچانے کا سوچ رہے ہیں، تو ابھی رابطہ کریں:
   > 📞 امنگ مینٹل ہیلتھ ہیلپ لائن (پاکستان): 0311-7786264
   > 📞 یا اپنے قریبی ایمرجنسی نمبر پر
   > میں یہاں آپ سے بات کرنے کے لیے موجود ہوں، لیکن براہ کرم کسی ایسے شخص سے بھی رابطہ کریں جو آپ کے قریب ہو۔"

   *(Verify the helpline number is current before the live presentation — numbers change.)*

3. The rest of the chat continues normally beneath the pinned card — the bot doesn't shut down, it stays present, just with the resource card anchored above.
4. This card **cannot be dismissed** by the user for the remainder of the session (no "x" close button) — it can only be replaced if risk de-escalates in later Groq turns, but the helpline numbers should remain accessible via a small persistent "Need help now?" link in the sidebar for the rest of the session regardless.

---

## 8. Field Validation & Error Message Copy (Full Table)

Since intake is conversational (not a rigid form), "field errors" mostly surface as inline assistant clarifications — but validate silently in code before accepting data:

| Field | Validation rule | If invalid, assistant says (EN) | (UR) |
|---|---|---|---|
| Email | basic regex `^[^@\s]+@[^@\s]+\.[^@\s]+$` | "That doesn't look like a complete email — mind double-checking it?" | "یہ مکمل ای میل نہیں لگ رہی — ایک بار دوبارہ چیک کر لیں؟" |
| Phone | digits only, 10–13 chars incl. optional `+` | "Could you share your number with the country code, like +923001234567?" | "براہ کرم اپنا نمبر کوڈ کے ساتھ لکھیں، مثلاً +923001234567" |
| Name | non-empty, no pure numeric string | "I didn't quite catch your name — what should I call you?" | "مجھے آپ کا نام سمجھ نہیں آیا — میں آپ کو کیا کہہ کر بلاؤں؟" |
| Mood rating (internal, not user-facing form) | 1–10 int | n/a — clamp silently, never show a raw validation error for this to the user |

**System-level errors (not conversational, shown as banners per §6.8):**

| Scenario | Banner type | Copy (EN) | Copy (UR) |
|---|---|---|---|
| Groq API timeout/failure | Error | "I'm having a little trouble responding right now. Give me a moment and try again." | "مجھے ابھی جواب دینے میں تھوڑی مشکل ہو رہی ہے۔ ذرا رکیں اور دوبارہ کوشش کریں۔" |
| Whisper transcription failure | Warning | See §6.5 | See §6.5 |
| PDF generation failure | Error | "I couldn't put your report together just now. Please try the 'Generate Report' button again." | "میں ابھی آپ کی رپورٹ نہیں بنا سکا۔ براہ کرم دوبارہ 'رپورٹ بنائیں' پر کلک کریں۔" |
| SMTP send failure | Warning (not error — download still works) | See §6.8 | See §6.8 |
| SQLite write failure | Error (log silently, don't alarm user) | "Something didn't save correctly, but let's keep going." | "کچھ محفوظ نہیں ہو سکا، لیکن ہم بات جاری رکھتے ہیں۔" |
| Off-topic redirect | System bubble (§2.4) | "I'd love to chat about that another time — right now, let's keep our focus on how you're feeling. What's been on your mind?" | "اس بارے میں بات پھر کبھی کریں گے — ابھی ہم اس پر توجہ رکھتے ہیں کہ آپ کیسا محسوس کر رہے ہیں۔ آپ کے ذہن میں کیا ہے؟" |

---

## 9. Iconography

Use emoji as the icon system (zero-dependency, renders natively everywhere, appropriately warm tone for this product — no need for an icon font library):

| Meaning | Icon |
|---|---|
| Assistant avatar | 🫶 or a simple monogram circle (pick one, stay consistent) |
| Voice input | 🎙️ |
| Report/PDF | 📄 |
| Email | 📧 |
| Mood | 🫧 |
| Success | ✅ |
| Warning | ⚠️ |
| Error | ❌ |
| Crisis/care | 💙 |
| Language | 🌐 |

Keep usage restrained — one icon per label/heading max, never icon-soup in body text.

---

## 10. Email Template Design

Send as **multipart** (HTML + plain-text fallback) via `smtplib`/`email.mime.multipart`.

### 10.1 Subject Line
`Your Wellness Session Summary — Sakoon AI 🫶` (EN) / language-matched if the user's session was primarily Urdu — but keep subject line bilingual-safe by defaulting to English subject with an Urdu greeting inside the body, to avoid encoding issues in some email clients.

### 10.2 HTML Structure

```
┌───────────────────────────────────────────┐
│  [Header band — --color-primary-light bg]  │
│   Logo mark + "Sakoon AI"                   │
├───────────────────────────────────────────┤
│  Hi [Name],                                 │
│  Here's a summary from your session today.  │
│  (short, warm, 1–2 sentences, not corporate)│
├───────────────────────────────────────────┤
│  [Card] Session Summary                     │
│  [Card] Symptoms & Triggers noted           │
│  [Card] Your Self-Care Plan                 │
│  [Card] When to reach out for more support  │
│         (always includes helpline info)     │
├───────────────────────────────────────────┤
│  📎 Full PDF report attached                │
├───────────────────────────────────────────┤
│  [Footer — --color-bg]                      │
│  Disclaimer: not a medical diagnosis.        │
│  "Sent with care by Sakoon AI"               │
└───────────────────────────────────────────┘
```

### 10.3 Email HTML/CSS constraints (important — email clients ≠ browsers)
- Use **inline CSS only** (`style="..."` per element) — Gmail strips `<style>` blocks in the `<head>` in many contexts.
- Table-based layout for the card sections (`<table>` with `role="presentation"`) rather than flexbox/grid — flexbox support is inconsistent across email clients (especially Outlook).
- Max width `600px`, centered, `background: #FAF9F7` on the outer body cell.
- Font: system font stack in email body (`Arial, Helvetica, sans-serif`) for the Latin parts — don't rely on Google Fonts loading in email clients, it's unreliable. Urdu portions of the email body (if any short greeting is bilingual) should still degrade gracefully to a default Unicode-capable font.
- Buttons in email (if any, e.g. "Open Sakoon AI again") — VML fallback not necessary for a demo; a simple padded `<a>` styled as a button is fine.

### 10.4 Plain-text fallback
Always include a plain-text `MIMEText` part alongside the HTML part (required for `multipart/alternative`) — a simple line-by-line version of the same content, no styling, so clients that block HTML still show something readable.

---

## 11. PDF Report — Visual Design Detail (expands IDEA.md §9)

- Page size A4, margins `20mm` all sides.
- **Header band:** `--color-primary` full-width rectangle, height `28mm`, white text: app name (18pt bold) + generated date (10pt, right-aligned within the band).
- **Section headers:** `--color-primary-dark`, 13pt bold, with a thin `--color-secondary` underline rule (0.75pt) beneath each.
- **Body text:** 11pt, `--color-text-primary`-equivalent gray (`#2B2B2B`), line spacing 1.4.
- **Urdu text blocks within the PDF:** must embed the Noto Nastaliq Urdu TTF explicitly via `fpdf2`'s `add_font()` — the default core fonts in fpdf2 do NOT support Arabic-script Unicode, this will silently render boxes/garbage if skipped. This is the highest-risk visual bug — test this specific path early, not at the end.
- **Disclaimer box:** light `--color-warning-bg` background box, rounded corners, 9pt italic text, placed directly under the header and again in the footer.
- **Footer:** 8pt gray, centered: `Generated by Sakoon AI · [timestamp] · Page X of Y`.
- Section order matches IDEA.md §9 exactly (Header → Patient Info → Session Summary → Symptoms/Triggers → Self-Care Plan → When to Seek Help → Footer).

---

## 12. Motion / Micro-interactions (keep minimal — Streamlit isn't built for heavy animation)

- Button hover: `0.15s ease` color transition (§6.6).
- Typing indicator: `1.2s` looped opacity fade (§6.3).
- New chat message: simple fade-in + 4px upward slide over `0.2s` on append (via CSS animation on the injected message div) — skip if it adds implementation risk under time pressure; this is a "polish if time allows," not core.
- No page-transition animations, no confetti/celebration effects — tone-inappropriate for this product.

---

## 13. Accessibility Notes

- Minimum contrast ratio 4.5:1 for all body text against its background (verify `--color-text-primary` on `--color-primary-light` and `--color-bg` — both pass at the specified hex values).
- All icons paired with text labels, never icon-only buttons (important for the "Generate Report" / "Resend Email" actions).
- Font sizes never below 11px anywhere, including timestamps.
- Crisis card copy is not conveyed by color alone — it uses explicit warm language + icon + border, so it doesn't rely on colorblind users perceiving "red."

---

## 14. Recommended Repo Documentation Set

For a clean, presentation-ready repo, include these `.md` files at root (this keeps scope tight — no over-documentation):

| File | Purpose |
|---|---|
| `README.md` | Project overview, setup instructions, how to run locally, screenshot, tech stack summary, link to live deployed app |
| `IDEA.md` | *(already created)* — problem, solution, architecture, modules, user flow |
| `DESIGN.md` | *(this file)* — UI/UX, color system, component states, copy, email/PDF formatting |
| `.env.example` *(not .md, but pair it)* | Lists required secret keys (`GROQ_API_KEY`, `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`) without real values, so anyone cloning knows what to set up |
| `CHANGELOG.md` *(optional, low effort)* | Simple dated bullet list per merge to `main` — nice for showing iterative work during the presentation Q&A |

Skip `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, architecture decision records, etc. — not needed for a single-team demo project and would just be clutter given the "minimal files" principle from `IDEA.md`.

---

## 15. Quick Reference — CSS Variables Block (drop-in starting point)

```css
:root {
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

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 18px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 32px;
  --space-6: 48px;
}
```

---

*This spec is intentionally exhaustive so implementation in Antigravity can move fast without back-and-forth on "what should this look like." If something isn't covered here, default to the Design Philosophy in §1: calm, trustworthy, legible, never silent.*
