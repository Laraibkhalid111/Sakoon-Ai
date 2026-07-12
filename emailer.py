"""
emailer.py — Sakoon AI
Gmail SMTP delivery (smtplib.SMTP_SSL, port 465) of the wellness report PDF
as an attachment. Sends a multipart/alternative email with an HTML body
(inline CSS, table-based layout per DESIGN.md §10) and a plain-text fallback.
All sends are wrapped in try/except — a failure here never crashes the app;
the in-app download button remains the fallback.
"""
# Logic implemented in M6
