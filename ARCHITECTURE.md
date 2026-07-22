# Sakoon AI — Evolutionary Architecture

> Decision record for upgrading the existing Streamlit companion into a
> production-ready mental wellness platform **without a greenfield rewrite**.

## Current foundation (preserve)

| Layer | Today |
|-------|--------|
| UI | Streamlit (`app.py`) |
| LLM / STT | Groq (Llama + Whisper) |
| Safety | Deterministic regex (`safety.py`) before every LLM call |
| Storage | SQLite (`sakoon.db`) |
| Outputs | PDF (`report.py`) + SMTP (`emailer.py`) |

This stack already delivers the bilingual chat, crisis gate, voice, report, and
email loops. All upgrades must keep those working.

## Architectural constraint

Many “million-user” asks (JWT microservices, React code-splitting, reusable
hooks, CSRF middleware) imply a **Next.js + FastAPI** rewrite. That violates
“do not rebuild from scratch” and would discard a working product.

**Decision:** Evolve in place on Streamlit for Phases 0–4. Introduce a thin
service package and richer SQLite schema first. Only in Phase 5+ consider an
optional FastAPI auth/API layer *alongside* Streamlit — never as a big-bang
replacement.

## Target package shape (incremental)

```
Sakoon-Ai/
├── app.py                 # thin Streamlit entry (orchestration only)
├── sakoon/                # introduced in Phase 1
│   ├── ui/                # CSS, bubbles, sidebar fragments
│   ├── services/          # chat, safety, report, email, wellness
│   ├── db/                # schema, migrations, repositories
│   └── core/              # config, logging, validation, security helpers
├── tests/
├── Dockerfile             # Phase 6
└── ...existing modules... # re-exported until callers migrate
```

Phase 1 moves code; it does not change behaviour.

## Phased delivery (no stubs)

| Phase | Goal | Done when |
|-------|------|-----------|
| **0 — Harden** | XSS/email escape, secrets hygiene, PDF footer, helpline link, real upsert, session close, message timestamps, anti-double-submit | App safer than before; no new features |
| **1 — Structure** | Package layout, structured logging, config module, indexes/FKs, history truncation, unit tests for safety/parser | **Done** — `sakoon/` package; root shims; same UX |
| **2 — Premium chat UI** | Modern theme (light/dark), markdown replies, copy, smoother thinking states, session history sidebar, coping/breathing UI | **Done** — theme toggle, safe markdown, copy, loadable history, coping panel |
| **3 — Wellness core** | Mood log, journal, guided breathing, affirmations, emergency resources (fully wired, not placeholders) | **Done** — wellness room + persistent mood/journal tables |
| **4 — Insights** | Mood trends, streaks, weekly summary charts (Plotly/Altair in Streamlit) | **Done** — Insights view with Altair charts, streaks, weekly narrative |
| **5 — Multi-user** | Auth (Streamlit gate + bcrypt), per-user data isolation, optional Fernet journal encryption | **Superseded** — auth gate removed (P0); local device profile + SQLite only |
| **6 — Ops** | Docker, healthcheck, CI, backups, rate limits, monitoring | **Done** — Dockerfile/compose, GH Actions CI, SQLite backups, chat/auth rate limits, health + metrics logs |

## Product decision — No authentication (P0)

Sakoon opens **directly into the experience**. There is no login, signup, or password reset.

- Identity = one local SQLite user (`username=__local__`) on this device
- Chats, mood, and journal stay on-device via `sakoon.db`
- Account UI / auth gate code paths are retired from the product surface

## Premium UI polish (Scope A) — Done

Post–Phase 6 visual/UX pass on Streamlit (no rewrite):

- Fixed chat Copy leaking `onclick`/raw HTML (native `st.button` + clipboard iframe)
- Calm design system (sage/teal tokens, Fraunces + Plus Jakarta Sans, glass sidebar)
- Premium bubbles (avatars, timestamps, voice badge, Regen)
- Wellness + Insights surface polish

### Deferred (out of Scope A) — partly landed later

- Token streaming of `reply_to_user` while JSON completes — **shipped** (live bubble)
- Always-on voice input card — **shipped**
- Auth gate removed (P0) — local device profile
- Chat reliability (P1) — iframe Copy, regen deletes DB row, off-topic stream suppress, rate-limit isolation
- Perf (P2) — compile CSS once/process, skip repeat schema init, cache recent sessions, trim sidebar into expanders
- Stop generation / message edit / file upload / TTS — still deferred

## Explicit non-goals for Phases 0–2

- Full therapist/coaching mode suite as vapourware panels
- Replacing Streamlit with React
- Claiming JWT/CSRF completeness before Phase 5

## Security baseline (all phases)

1. Escape every user/model string before `unsafe_allow_html` or email HTML.
2. Never commit secrets; rotate if exposed.
3. Parameterized SQL only (already true).
4. Crisis detection remains pre-LLM and non-optional.
5. Disclaimers: not a diagnostic or prescribing tool.

## How to use this doc

Implement **one phase at a time**. Merge only when that phase’s “Done when”
criteria are met. Prefer shipping Phase 0 today over half-building Phase 3.
