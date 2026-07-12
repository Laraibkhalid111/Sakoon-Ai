# PLANNING.md — Sakoon AI — Modular Build Plan

This document breaks `IDEA.md` (architecture/logic) and `DESIGN.md` (UI/UX spec) into an executable, module-by-module, task-by-task build plan. It is the operating checklist for development — work top to bottom, module by module, task by task (`T0, T1, T2...`), don't skip ahead.

**Golden rules for every module (baked into the tasks below, don't shortcut them):**
1. Every module starts with a task to re-read `DESIGN.md` (and the relevant part of `IDEA.md`) for that feature area before writing code — never guess colors, copy, spacing, or states.
2. Every module's second-to-last task is a **hardening pass**: edge cases from `IDEA.md` §16, error handling, UI consistency check against `DESIGN.md`, "is this actually production/deployment ready" — not just "does the happy path work."
3. Every module's last task is a **clean git push** using the branch model from `IDEA.md` §15 (`feature/xyz` → `dev`, tested → `dev` → `main`), with a proper conventional commit message.
4. No module is "done" until Streamlit can run it locally with zero crashes and zero secrets committed.

---

## M0 — Repo Bootstrap & Environment

**Goal:** Get the exact minimal file structure from `IDEA.md` §5 in place, branches created, secrets scaffolded, Groq reachable. Nothing user-facing yet.

- **T0.0** — Read `IDEA.md` §4 (Tech Stack), §5 (File Structure), §6 (Data Model), §15 (Git Workflow) end to end. Confirm no deviation (no LangChain, no Docker, no extra folders).
- **T0.1** — Initialize/confirm the GitHub repo `SAKOON_AI` is connected to the local working folder. Create `main` and `dev` branches if they don't exist. Confirm branch protection intent (no direct commits to `main`).
- **T0.2** — Create the exact file skeleton from `IDEA.md` §5: `app.py`, `chatbot.py`, `safety.py`, `database.py`, `report.py`, `emailer.py`, `prompts.py`, `requirements.txt`, `.gitignore`, `.streamlit/secrets.toml` (local, gitignored), `README.md` — each file created with a one-line docstring/purpose comment only, no logic yet.
- **T0.3** — Write `.gitignore` (secrets.toml, `sakoon.db`, `__pycache__/`, `*.pdf`, `.venv/`, `.DS_Store`).
- **T0.4** — Write `requirements.txt` (streamlit, groq, fpdf2, python-dotenv if needed — pin approximate major versions). Set up a virtual environment and `pip install -r requirements.txt` locally to confirm it resolves cleanly.
- **T0.5** — Populate `.streamlit/secrets.toml` locally with placeholder keys (`GROQ_API_KEY`, `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`) and create `.env.example` documenting them without real values (per `DESIGN.md` §14).
- **T0.6** — Smoke-test: minimal script that calls the Groq API with a hardcoded "hello" prompt and prints the response, to confirm the key/network path works before building anything on top of it. Delete/park this script once confirmed (don't leave stray test files in root).
- **T0.7** — **Hardening pass:** confirm no secrets are staged for commit (`git status`, check `.gitignore` is actually excluding `secrets.toml`), confirm `requirements.txt` installs cleanly in a fresh venv, confirm the repo has no leftover scratch files.
- **T0.8** — Commit & push: branch `feature/repo-bootstrap` off `dev` → PR into `dev`. Commit message: `chore: bootstrap repo skeleton, branches, secrets scaffold, deps`. Merge once verified.

---

## M1 — Core Bilingual Chat Loop (MVP demo-able core)

**Goal:** A working scoped, bilingual, JSON-mode chat loop in Streamlit — this is the single most important module per `IDEA.md` §17 (build-order priority #2) since it's independently demo-able.

- **T1.0** — Re-read `IDEA.md` §7 (Groq brain / JSON schema), §3 (core design principles — single purpose, hard boundaries), and `DESIGN.md` §2 (color system), §3 (typography), §6.3 (chat bubbles), §6.4 (chat input bar) before writing any UI or prompt code.
- **T1.1** — `prompts.py`: write the system prompt covering persona, scope lock, no-diagnosis/no-medication rule, one-thing-at-a-time question flow, and the exact JSON schema from `IDEA.md` §7 (`reply_to_user`, `conversation_stage`, `detected_language`, `extracted{...}`, `suggested_coping_action`, `is_on_topic`). Keep schema definition as a single constant string, reused for validation.
- **T1.2** — `chatbot.py`: Groq client wrapper — function that takes conversation history + current stage, calls Groq with `response_format={"type": "json_object"}`, parses and validates the JSON response (with try/except + schema key fallback defaults so a malformed response never crashes the app).
- **T1.3** — `app.py`: page config, load `.streamlit/config.toml` theme values (`DESIGN.md` §4.1), inject the single custom CSS block (`DESIGN.md` §4.2) including Google Fonts `<link>` for Inter + Noto Nastaliq Urdu. One injection point only, per the design doc's explicit recommendation.
- **T1.4** — Build the sidebar + main chat layout grid exactly per `DESIGN.md` §5.1 (sidebar ~320px, header/branding §6.1, language badge §6.2 placeholder for now, chat area, fixed-bottom input).
- **T1.5** — Implement custom chat bubble rendering (not raw `st.chat_message` styling) per `DESIGN.md` §6.3 — user bubble right-aligned/no avatar, assistant bubble left-aligned with avatar, correct rounded-corner "tail" logic, timestamps, script-aware font/direction switching (Urdu vs Roman Urdu vs English) per `DESIGN.md` §3 rules.
- **T1.6** — Wire `st.chat_input()` to the Groq call: on submit → append user message → show typing/thinking indicator (3 animated dots per `DESIGN.md` §6.3, not a generic spinner) → call `chatbot.py` → render `reply_to_user` → merge `extracted` into `st.session_state.profile`.
- **T1.7** — Implement `is_on_topic: false` handling: render the fixed warm redirect copy from `DESIGN.md` §8 (system/redirect bubble style, §2.4) instead of the model's raw text — bulletproof, not model-dependent.
- **T1.8** — Implement chat input states from `DESIGN.md` §6.4: default/focus/error/disabled-while-responding (dimmed, placeholder swap to "Sakoon is thinking...").
- **T1.9** — Implement the conversational intake flow per `IDEA.md` §11 Steps 0–2 (welcome message, name/email/phone gathered conversationally, not a rigid form) using `conversation_stage` to drive prompt behavior.
- **T1.10** — Implement Groq API failure handling: try/except around the call, on failure show the exact error banner copy from `DESIGN.md` §8 system-level error table ("I'm having a little trouble responding right now...") without crashing the session.
- **T1.11** — **Hardening pass:** test empty/blank submit, very long rambling message, jailbreak/off-topic rephrasing attempts (`IDEA.md` §16), rapid double-submit race condition on `st.session_state`. Confirm bubble styling, fonts, spacing, and copy match `DESIGN.md` exactly (no placeholder colors/fonts left in). Confirm no console errors, app runs clean end-to-end locally.
- **T1.12** — Commit & push: branch `feature/core-chat-loop` off `dev` → PR into `dev`. Commit message: `feat: bilingual JSON-mode chat loop with scope-locked redirect handling`. Merge once verified.

---

## M2 — Deterministic Safety / Crisis Layer

**Goal:** Crisis detection that runs independently of the LLM and cannot be prompted away, with the exact visual and copy treatment from `DESIGN.md` §7.

- **T2.0** — Re-read `IDEA.md` §8 (Safety Layer) and `DESIGN.md` §7 (Crisis State — Exact Specification), §2.3 (crisis color tokens — never reused for ordinary errors), §6.8 (banner styles) in full before writing detection logic or UI.
- **T2.1** — `safety.py`: build the deterministic keyword/pattern matcher for self-harm/harm-to-others/acute-crisis expressions across English, Urdu script, and Roman Urdu. Keep the pattern list as a maintainable data structure (list/set), not scattered string checks.
- **T2.2** — Wire `safety.py` to run on **every** user message, before it reaches Groq, in `app.py`'s message-handling path.
- **T2.3** — On trigger: bypass the normal LLM reply for that turn entirely; render the pinned crisis card at the top of the chat area using the exact hardcoded English/Urdu copy from `DESIGN.md` §7.2 (verify the helpline number is current, flag it as a pre-launch check item) — never LLM-generated text for this card.
- **T2.4** — Style the crisis card per `DESIGN.md` §6.8 crisis row: `--color-crisis-bg`, 2px `--color-crisis` border, 💙 icon (not a harsh warning icon), non-dismissible, sticky at top of chat area, distinct from all other banner types.
- **T2.5** — Persist `risk_level = 'crisis'` on the session (state now, DB wiring completes in M3) so it's never silently dropped, and ensure the rest of the chat continues normally beneath the pinned card (bot stays present, doesn't shut down) per `DESIGN.md` §7.3.
- **T2.6** — Add the persistent "Need help now?" sidebar link that stays available for the rest of the session regardless of later de-escalation, per `DESIGN.md` §7.4.
- **T2.7** — **Hardening pass:** test crisis-pattern messages both at conversation start and mid-conversation (`IDEA.md` §16), test that the crisis card cannot be dismissed, confirm crisis-red is visually distinct from `--color-error` at a glance, confirm bilingual copy renders correctly in both scripts, confirm this layer fires even if Groq is down/timing out (safety check must not depend on the LLM being reachable).
- **T2.8** — Commit & push: branch `feature/crisis-safety-layer` off `dev` → PR into `dev`. Commit message: `feat: deterministic bilingual crisis detection with pinned safety card`. Merge once verified.

---

## M3 — SQLite Persistence Layer

**Goal:** Local memory across the session and a data foundation for the PDF report — 4 flat tables, no over-engineering.

- **T3.0** — Re-read `IDEA.md` §6 (Data Model) and confirm `database.py` will implement exactly these 4 tables with no additions: `users`, `sessions`, `messages`, `symptom_snapshots`.
- **T3.1** — `database.py`: schema creation (`CREATE TABLE IF NOT EXISTS`) run once at app startup, connecting to `sakoon.db`.
- **T3.2** — CRUD helpers: create/find user by session, create session row, append message row per turn (role, content, input_mode, timestamp), upsert `symptom_snapshots` as `extracted` data accumulates turn over turn.
- **T3.3** — Wire `app.py`/`chatbot.py` output into `database.py` calls: every user+assistant turn logged, every `extracted` update reflected in `symptom_snapshots`, session `risk_level` updated when crisis triggers (from M2).
- **T3.4** — Wrap all writes in try/except; on failure, log silently and show the exact non-alarming copy from `DESIGN.md` §8 ("Something didn't save correctly, but let's keep going.") — persistence failures must never crash or interrupt the conversation.
- **T3.5** — (Optional, time-permitting per `IDEA.md` §6) simple "past sessions" read-only list in the sidebar.
- **T3.6** — **Hardening pass:** test SQLite write failure (e.g. simulate locked/missing file), confirm no crash; test that a session with partial/incomplete data (user left mid-conversation) still leaves a queryable, non-corrupt row set; confirm `sakoon.db` is gitignored and never committed.
- **T3.7** — Commit & push: branch `feature/sqlite-persistence` off `dev` → PR into `dev`. Commit message: `feat: SQLite persistence for users, sessions, messages, symptom snapshots`. Merge once verified.

---

## M4 — Voice Input (Whisper via Groq)

**Goal:** `st.audio_input` → Groq Whisper transcription → fed into the same chat pipeline as text, with exact widget states from `DESIGN.md` §6.5.

- **T4.0** — Re-read `IDEA.md` §4 (voice stack rationale) and `DESIGN.md` §6.5 (Voice Input Widget states) and §6.3 (voice-originated message bubble treatment with 🎙️ prefix) before implementing.
- **T4.1** — Add the sidebar `🎙️ Voice Input` expander (collapsed by default) housing `st.audio_input`, per `DESIGN.md` §5.1/§6.5.
- **T4.2** — Implement idle-state helper copy ("Tap to record. Speak in Urdu or English.") and leave Streamlit's native recording indicator untouched (don't fight native widget styling, per design doc instruction).
- **T4.3** — On audio submit: send to Groq Whisper (`whisper-large-v3-turbo`), show `st.spinner` with the exact bilingual copy from `DESIGN.md` §6.5 ("Listening carefully..." / Urdu equivalent) during processing.
- **T4.4** — On successful transcription: auto-populate the transcript as a new chat message using the voice-bubble style (🎙️ prefix inside bubble, per `DESIGN.md` §6.3), feed it into the exact same `chatbot.py` pipeline used for typed text (no parallel/duplicate logic path), then auto-collapse the expander back to idle.
- **T4.5** — On transcription failure (silence, no speech detected, API error): show the inline warning banner with exact copy from `DESIGN.md` §6.5, wrapped in try/except so it never crashes the session.
- **T4.6** — **Hardening pass:** test background noise, silence, very short clips, and Whisper API failure/timeout (`IDEA.md` §16). Confirm voice-originated messages are visually distinguishable from typed ones in chat history. Confirm the fallback path (user just types instead) always remains available.
- **T4.7** — Commit & push: branch `feature/voice-input` off `dev` → PR into `dev`. Commit message: `feat: voice input via st.audio_input + Groq Whisper transcription`. Merge once verified.

---

## M5 — PDF Wellness Report Generation

**Goal:** A clean, correctly-formatted PDF per `IDEA.md` §9 and the pixel-level detail in `DESIGN.md` §11 — including the highest-risk technical item (Urdu font embedding).

- **T5.0** — Re-read `IDEA.md` §9 (report sections) and `DESIGN.md` §11 (PDF visual detail) in full, in particular the Urdu font warning: fpdf2's default core fonts do **not** support Arabic-script Unicode and will silently render garbage/boxes if `add_font()` isn't used explicitly. Treat this as the first thing to prototype and test, not the last.
- **T5.1** — Source and vendor the Noto Nastaliq Urdu TTF file into the repo (small, licensed-for-embedding font file), and write a minimal standalone test script that renders a line of Urdu text into a throwaway PDF to confirm the font path works, before integrating into `report.py` proper.
- **T5.2** — `report.py`: build the structured report dict from `st.session_state.profile` / DB data (name, contact, session date, primary concern, mood trend, symptoms, triggers, self-care plan, professional-help note + helpline numbers always included regardless of risk level).
- **T5.3** — Implement PDF layout per `DESIGN.md` §11: A4, 20mm margins, `--color-primary` header band (28mm height, app name 18pt bold + right-aligned date), section headers 13pt bold `--color-primary-dark` with 0.75pt `--color-secondary` underline, 11pt body text at 1.4 line spacing, disclaimer box (`--color-warning-bg`, rounded, 9pt italic) under header and in footer, 8pt centered footer with page numbers. Section order must exactly match `IDEA.md` §9.
- **T5.4** — Add the one-paragraph Groq-generated narrative summary for the Session Summary section (a single scoped LLM call reusing `chatbot.py`'s client, not a new provider).
- **T5.5** — Confirm no medication names/dosages appear anywhere in generated content (spot-check against the self-care/recovery plan generation prompt).
- **T5.6** — Wire the sidebar "📄 Generate Report" button (`DESIGN.md` §6.6 primary button styling/states) to build the PDF and offer it via `st.download_button`; wrap in try/except with the exact PDF-failure error copy from `DESIGN.md` §8 on failure.
- **T5.7** — Handle partial/incomplete session data (user left mid-conversation) — report must still generate cleanly with whatever fields are available, never crash on missing fields (`IDEA.md` §16).
- **T5.8** — **Hardening pass:** generate reports for (a) a full complete session, (b) a partial session, (c) an all-Urdu session, (d) a mixed-script session — visually inspect each PDF for correct font rendering, layout, and no garbled text. Confirm button states match `DESIGN.md` §6.6 exactly (disabled/hover/pressed).
- **T5.9** — Commit & push: branch `feature/pdf-report` off `dev` → PR into `dev`. Commit message: `feat: fpdf2 wellness report generation with embedded Urdu font support`. Merge once verified.

---

## M6 — Email Delivery

**Goal:** SMTP delivery of the PDF report with graceful fallback, plus the HTML/plain-text email template from `DESIGN.md` §10.

- **T6.0** — Re-read `IDEA.md` §10 (Email Delivery) and `DESIGN.md` §10 (Email Template Design) in full — especially the email-client constraints (inline CSS only, table-based layout, no Google Fonts reliance, 600px max width).
- **T6.1** — `emailer.py`: `smtplib.SMTP_SSL` + Gmail app-password login, function that takes recipient, subject, HTML body, plain-text body, and PDF attachment path.
- **T6.2** — Build the HTML email template per `DESIGN.md` §10.2/§10.3: header band with logo mark, warm 1–2 sentence greeting, card sections (Session Summary / Symptoms & Triggers / Self-Care Plan / When to Reach Out — always including helpline info), footer with medical disclaimer, `role="presentation"` tables instead of flexbox, inline styles only.
- **T6.3** — Build the required plain-text `MIMEText` fallback (line-by-line, unstyled) per `DESIGN.md` §10.4, sent as part of the same `multipart/alternative` message.
- **T6.4** — Set the subject line exactly per `DESIGN.md` §10.1 (English subject, Urdu-aware greeting inside the body — never a bilingual subject line, to avoid client encoding issues).
- **T6.5** — Wire the sidebar "📧 Resend to Email" button and the automatic send-on-report-generation flow from `IDEA.md` §11 Step 7. Wrap the whole send in try/except so a failed send never breaks report generation — on failure, show the exact warning banner from `DESIGN.md` §8 (download still works as fallback) rather than an error banner.
- **T6.6** — **Hardening pass:** test with wrong app password, test with no internet connection (`IDEA.md` §16), confirm the download button remains fully functional regardless of email outcome, confirm the sent email renders correctly in at least Gmail (and ideally one more client) with the PDF attached.
- **T6.7** — Commit & push: branch `feature/email-delivery` off `dev` → PR into `dev`. Commit message: `feat: SMTP email delivery with HTML/plain-text template and PDF attachment`. Merge once verified.

---

## M7 — Full UI/UX Polish Pass (Design System Compliance)

**Goal:** A dedicated pass to bring every screen and state into full compliance with `DESIGN.md`, now that all functional modules exist — this module exists because individual modules build UI incrementally, but the *whole* app needs one coherent design-system sweep.

- **T7.0** — Re-read `DESIGN.md` in full, front to back, as a checklist document (not a skim) — §1 Philosophy through §15 CSS variables.
- **T7.1** — Language badge (`DESIGN.md` §6.2): wire it to `detected_language` from the last Groq response automatically, add the manual override dropdown (`Auto / English / اردو`) in the sidebar as fallback.
- **T7.2** — Mood indicator pill (`DESIGN.md` §6.7): wire to latest `mood_rating`, implement the 3-tier color/label mapping (amber/teal/sage), confirm it never shows a raw numeric score to the user.
- **T7.3** — Sweep every button in the app against `DESIGN.md` §6.6's exact table (Primary/Secondary/Danger — default/hover/active/disabled states, transitions).
- **T7.4** — Sweep every banner (success/warning/error/crisis) against `DESIGN.md` §6.8 for correct colors, borders, icons, and copy — confirm crisis styling is never reused elsewhere.
- **T7.5** — Confirm all inline field-validation copy (email/phone/name) matches `DESIGN.md` §8's exact bilingual table, surfaced as conversational assistant clarifications, not raw form errors.
- **T7.6** — Verify typography rules (`DESIGN.md` §3): correct font per script, correct RTL/LTR handling, correct line-heights, no mixed font sizes within a bubble.
- **T7.7** — Verify spacing scale (`DESIGN.md` §5.3) and responsive behavior (`DESIGN.md` §5.2 — native sidebar collapse on mobile, bubble max-width 75%/88%).
- **T7.8** — Add the optional micro-interactions from `DESIGN.md` §12 (button hover transitions, fade-in on new message) only if they don't add implementation risk — explicitly skippable per the design doc.
- **T7.9** — Accessibility sweep per `DESIGN.md` §13: contrast ratios, icon+text pairing (no icon-only buttons), minimum font sizes, crisis card not relying on color alone.
- **T7.10** — **Hardening pass:** full click-through of every user-facing state in the app (idle, loading, success, error, crisis, disabled) side-by-side with `DESIGN.md`, on both a desktop-width viewport and a narrow one; confirm nothing looks like an unstyled default Streamlit component; confirm no dead-air states remain (per Design Philosophy §1 "Never silent").
- **T7.11** — Commit & push: branch `feature/design-system-polish` off `dev` → PR into `dev`. Commit message: `style: full DESIGN.md compliance pass across all UI states`. Merge once verified.

---

## M8 — Full Edge Case & Regression Pass

**Goal:** Systematically clear every edge case in `IDEA.md` §16 in one dedicated pass, across the fully integrated app (not module-by-module in isolation this time).

- **T8.0** — Re-read `IDEA.md` §16 (Edge Cases) and §14 (Non-Functional / Success Criteria) as the acceptance checklist for this module.
- **T8.1** — Test and fix: empty/blank submit; very long rambling message extraction; Urdu→Roman-Urdu mid-session switch consistency.
- **T8.2** — Test and fix: voice input with noise/silence/short clips; user refuses name/email (bot proceeds gracefully, doesn't get stuck).
- **T8.3** — Test and fix: off-topic redirect (e.g. "who will win the cricket match") and jailbreak rephrasing attempts ("ignore previous instructions...") — must redirect 100% of the time per the success criteria.
- **T8.4** — Test and fix: crisis-pattern message at conversation start AND mid-conversation; rapid double-message race condition on `st.session_state`.
- **T8.5** — Test and fix: Groq API timeout/error recovery; SMTP failure with PDF-download fallback still working; SQLite write failure not interrupting chat; PDF generation with incomplete/partial session data.
- **T8.6** — Run the full response-latency check (`IDEA.md` §14 — target <3s per text turn) and note any turn that's consistently slower, optimizing the JSON-parse/DB-write path if needed.
- **T8.7** — **Hardening pass:** run through the entire `IDEA.md` §13 Functional Requirements Checklist top to bottom and tick off each item against the live app; confirm codebase is still ≤8 Python files with no nested folder sprawl (`IDEA.md` §14); confirm zero secrets anywhere in git history.
- **T8.8** — Commit & push: branch `fix/edge-case-hardening` off `dev` → PR into `dev`. Commit message: `fix: resolve edge cases and regressions from IDEA.md §16 checklist`. Merge once verified.

---

## M9 — Deployment & Release

**Goal:** Get a live, working link on Streamlit Community Cloud from a clean `main`, per `IDEA.md` §15 and §17 (final build step).

- **T9.0** — Re-read `IDEA.md` §15 (Git Workflow) and §17 (Build Order, final step) to confirm the exact promotion sequence: `dev` fully stable → PR `dev` → `main`.
- **T9.1** — Final full smoke test on `dev`: fresh clone into a clean environment, `pip install -r requirements.txt`, run locally end to end (text chat, voice, crisis trigger, report generation, email send) with zero manual patching required.
- **T9.2** — Open PR `dev` → `main`, self-review the diff one more time for stray debug code, print statements, or hardcoded test values.
- **T9.3** — Merge to `main`. Tag the release (e.g. `v1.0.0`) as a rollback point.
- **T9.4** — Connect the `SAKOON_AI` repo's `main` branch to Streamlit Community Cloud, configure the Secrets panel with real `GROQ_API_KEY` / `EMAIL_ADDRESS` / `EMAIL_APP_PASSWORD` values (never committed to git).
- **T9.5** — Deploy, then run the full smoke test again against the **live deployed link** (not just localhost) — text chat, voice input, crisis trigger, report download, email delivery.
- **T9.6** — Finalize `README.md` per `DESIGN.md` §14 (overview, setup instructions, how to run locally, screenshot, tech stack summary, link to live deployed app). Optionally start `CHANGELOG.md` with dated bullets per merge, if time allows.
- **T9.7** — **Hardening pass:** confirm the live link is publicly reachable with no auth wall, confirm no console/network errors on the deployed instance, confirm the crisis helpline number is current (explicit re-check called out in `DESIGN.md` §7), confirm mobile viewport doesn't visibly break (even though it's a "nice-to-have," per `DESIGN.md` §5.2 it shouldn't look broken).
- **T9.8** — Commit & push: any final fixes go through `fix/pre-launch-*` branches off `dev` → tested → `main`, tagged as a patch release (e.g. `v1.0.1`) if needed. Commit message convention: `release: v1.0.0 — Sakoon AI live on Streamlit Cloud`.

---

## Appendix A — Module Dependency Order

```
M0 (bootstrap)
 └─ M1 (core chat loop)          ← independently demo-able after this
     ├─ M2 (crisis safety)       ← must sit in front of every Groq call
     ├─ M3 (SQLite persistence)  ← depends on M1's extracted data + M2's risk_level
     ├─ M4 (voice input)         ← feeds into M1's same pipeline
     └─ M5 (PDF report)          ← depends on M3's stored data
         └─ M6 (email delivery)  ← depends on M5's generated PDF
M7 (design system polish)        ← sweep after M1–M6 exist
M8 (edge case pass)               ← sweep after M1–M7 exist
M9 (deployment)                   ← final, only after M8 passes
```

## Appendix B — Definition of Done (applies to every module)

A module is only complete when **all** of the following are true:
- [ ] Functionality matches its section(s) of `IDEA.md` exactly, no scope creep.
- [ ] Visual/copy output matches `DESIGN.md` exactly (colors, spacing, fonts, states, bilingual copy) — no placeholder styling left behind.
- [ ] Every external call (Groq, Whisper, SMTP, SQLite, fpdf2) is wrapped in error handling that degrades gracefully per `DESIGN.md` §8's error-copy table.
- [ ] Relevant edge cases from `IDEA.md` §16 for that module have been tested.
- [ ] No secrets, debug prints, or scratch files are committed.
- [ ] Code lives in the correct file per `IDEA.md` §5 (no new files invented without updating this plan).
- [ ] Merged into `dev` via a reviewed PR with a clean conventional commit message, following `IDEA.md` §15's branch model.

---

*This plan is derived entirely from `IDEA.md` and `DESIGN.md`. If a task here ever seems to contradict either source document, the source documents win — update this plan, not the other way around.*
