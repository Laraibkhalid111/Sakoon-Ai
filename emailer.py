"""
emailer.py — Sakoon AI
Gmail SMTP delivery (smtplib.SMTP_SSL/smtplib.SMTP, port 465/587) of the wellness report PDF
as an attachment. Sends a multipart/alternative email with an HTML body
(inline CSS, table-based layout per DESIGN.md §10) and a plain-text fallback.
All sends are wrapped in try/except — a failure here never crashes the app;
the in-app download button remains the fallback.
"""

import os
import smtplib
import traceback
import logging
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st

def send_email_report(
    recipient: str,
    pdf_bytes: bytes,
    filename: str,
    session_data: dict,
    narrative: str
) -> bool:
    """
    Constructs and sends a multipart wellness report email with a PDF attachment.
    
    Args:
        recipient: Email address of the recipient.
        pdf_bytes: Raw bytes of the generated PDF report.
        filename: Filename for the attachment.
        session_data: Dictionary containing extracted session details.
        narrative: One-paragraph narrative summary of the session.
        
    Returns:
        True if sent successfully, False otherwise.
    """
    try:
        sender_email = st.secrets.get("EMAIL_ADDRESS")
        app_password = st.secrets.get("EMAIL_APP_PASSWORD")
        smtp_host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port_val = st.secrets.get("SMTP_PORT", 465)
        
        if not sender_email or not app_password:
            logging.getLogger(__name__).error("SMTP credentials missing from st.secrets.")
            return False
            
        smtp_port = int(smtp_port_val)
        lang = session_data.get("session_language", "english")
        name = session_data.get("name") or ("پیارے دوست" if lang == "urdu" else "there")

        # ── Setup content based on language ───────────────────────────────────
        care_items = [
            "Take a few slow, deep breaths when you feel overwhelmed - even 3 breaths can help.",
            "Try to keep a consistent sleep schedule, even if sleep is difficult right now.",
            "Share how you're feeling with someone you trust - you don't have to carry this alone.",
            "Keep this session open - come back to Sakoon AI anytime you need to talk."
        ]
        support_items = [
            "If your feelings are becoming overwhelming and interfering with daily life.",
            "If you're having thoughts of harming yourself or others.",
            "If you've been struggling for more than two weeks.",
            "<strong>Umang Mental Health Helpline (Pakistan): 0311-7786264</strong>",
            "You can also reach out to a licensed counsellor or therapist in your area."
        ]

        if lang == "urdu":
            greeting = f"السلام علیکم {name}"
            intro = "ساکون کے ساتھ آج کی گفتگو کا خلاصہ اور آپ کا فلاحی منصوبہ نیچے دیا گیا ہے۔"
            
            summary_title = "گفتگو کا خلاصہ"
            symptoms_triggers_title = "علامات اور محرکات"
            self_care_title = "خود کی دیکھ بھال کا منصوبہ"
            support_title = "مدد حاصل کرنے کے اوقات"
            
            narrative_display = narrative or "خلاصہ دستیاب نہیں ہے۔"
            
            symptoms = session_data.get("symptoms", [])
            if symptoms:
                symptoms_html = "".join(f"<li style='margin-bottom: 6px; direction: rtl; text-align: right;'>{s}</li>" for s in symptoms)
            else:
                symptoms_html = "<li style='margin-bottom: 6px; direction: rtl; text-align: right;'>کوئی مخصوص علامات درج نہیں کی گئیں۔</li>"
                
            triggers = session_data.get("possible_triggers", [])
            if triggers:
                triggers_html = "".join(f"<li style='margin-bottom: 6px; direction: rtl; text-align: right;'>{t}</li>" for t in triggers)
            else:
                triggers_html = "<li style='margin-bottom: 6px; direction: rtl; text-align: right;'>کوئی مخصوص محرکات درج نہیں کیے گئے۔</li>"
                
            care_items_ur = [
                "جب آپ خود پر دباؤ محسوس کریں تو چند گہرے اور سست سانسیں لیں - صرف 3 سانسیں بھی مددگار ثابت ہو سکتی ہیں۔",
                "نیند کا ایک باقاعدہ شیڈول رکھنے کی کوشش کریں، چاہے اس وقت سونا کتنا ہی مشکل کیوں نہ ہو۔",
                "اپنے کسی معتبر شخص کے ساتھ اپنے احساسات شیئر کریں - آپ کو یہ اکیلے برداشت کرنے کی ضرورت نہیں ہے۔",
                "ساکون کے پاس کسی بھی وقت دوبارہ بات کرنے کے لیے آئیں۔"
            ]
            care_html = "".join(f"<li style='margin-bottom: 6px; direction: rtl; text-align: right;'>{item}</li>" for item in care_items_ur)
            
            support_items_ur = [
                "اگر آپ کے احساسات حد سے زیادہ بڑھ جائیں اور روزمرہ کی زندگی میں رکاوٹ بنیں۔",
                "اگر آپ خود کو یا دوسروں کو نقصان پہنچانے کے بارے میں سوچ رہے ہوں۔",
                "اگر آپ دو ہفتوں سے زیادہ وقت سے جدوجہد کر رہے ہوں۔",
                "<strong>امنگ مینٹل ہیلتھ ہیلپ لائن (پاکستان): 0311-7786264</strong>",
                "آپ اپنے قریبی کسی لائسنس یافتہ کونسلر یا تھراپسٹ سے بھی رابطہ کر سکتے ہیں۔"
            ]
            support_html = "".join(f"<li style='margin-bottom: 6px; direction: rtl; text-align: right;'>{item}</li>" for item in support_items_ur)
            
            attachment_notice = "📎 <strong>آپ کی مکمل پی ڈی ایف فلاحی رپورٹ اس ای میل کے ساتھ منسلک ہے۔</strong>"
            disclaimer_text = "دستبرداری: ساکون عام دماغی صحت کی صحبت اور خود کی دیکھ بھال کے وسائل فراہم کرتا ہے۔ یہ طبی تشخیص، علاج یا تھراپی فراہم نہیں کرتا۔"
            sent_with_care = "ساکون کی طرف سے پیار کے ساتھ بھیجا گیا 🫶"
        else:
            greeting = f"Hi {name}"
            intro = "Here is a summary and wellness plan from your session with Sakoon AI today."
            
            summary_title = "Session Summary"
            symptoms_triggers_title = "Symptoms & Triggers Noted"
            self_care_title = "Your Self-Care Plan"
            support_title = "When to Reach Out for More Support"
            
            narrative_display = narrative or "No narrative summary available."
            
            symptoms = session_data.get("symptoms", [])
            if symptoms:
                symptoms_html = "".join(f"<li style='margin-bottom: 6px;'>{s}</li>" for s in symptoms)
            else:
                symptoms_html = "<li style='margin-bottom: 6px;'>No specific symptoms noted.</li>"
                
            triggers = session_data.get("possible_triggers", [])
            if triggers:
                triggers_html = "".join(f"<li style='margin-bottom: 6px;'>{t}</li>" for t in triggers)
            else:
                triggers_html = "<li style='margin-bottom: 6px;'>No specific triggers noted.</li>"
                
            care_html = "".join(f"<li style='margin-bottom: 6px;'>{item}</li>" for item in care_items)
            support_html = "".join(f"<li style='margin-bottom: 6px;'>{item}</li>" for item in support_items)
            
            attachment_notice = "📎 <strong>Your full PDF wellness report is attached to this email.</strong>"
            disclaimer_text = "Disclaimer: Sakoon AI provides general mental wellness companionship and self-care resources. It does not provide clinical diagnosis, medical treatment, or therapy."
            sent_with_care = "Sent with care by Sakoon AI 🫶"

        # ── Plain Text Fallback ───────────────────────────────────────────────
        if lang == "urdu":
            plain_body = f"""\
{greeting}

{intro}

=== {summary_title} ===
{narrative_display}

=== {symptoms_triggers_title} ===
علامات:
""" + ("\n".join(f"- {s}" for s in symptoms) if symptoms else "- کوئی مخصوص علامات درج نہیں کی گئیں۔") + f"""

محرکات:
""" + ("\n".join(f"- {t}" for t in triggers) if triggers else "- کوئی مخصوص محرکات درج نہیں کیے گئے۔") + f"""

=== {self_care_title} ===
""" + "\n".join(f"- {item}" for item in care_items_ur) + f"""

=== {support_title} ===
""" + "\n".join(f"- {item.replace('<strong>','').replace('</strong>','')}" for item in support_items_ur) + f"""

{attachment_notice.replace("<strong>", "").replace("</strong>", "")}

{disclaimer_text}
{sent_with_care}
"""
        else:
            plain_body = f"""\
{greeting}

{intro}

=== {summary_title} ===
{narrative_display}

=== {symptoms_triggers_title} ===
Symptoms:
""" + ("\n".join(f"- {s}" for s in symptoms) if symptoms else "- No specific symptoms noted.") + f"""

Possible Triggers:
""" + ("\n".join(f"- {t}" for t in triggers) if triggers else "- No specific triggers noted.") + f"""

=== {self_care_title} ===
""" + "\n".join(f"- {item}" for item in care_items) + f"""

=== {support_title} ===
""" + "\n".join(f"- {item.replace('<strong>','').replace('</strong>','')}" for item in support_items) + f"""

{attachment_notice.replace("<strong>", "").replace("</strong>", "")}

{disclaimer_text}
{sent_with_care}
"""

        # ── HTML Email Layout (DESIGN.md §10.2 / §10.3) ──────────────────────
        html_body = f"""\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{summary_title}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #FAF9F7; font-family: Arial, Helvetica, sans-serif;-webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FAF9F7; padding: 20px 0; border-collapse: collapse;">
    <tr>
      <td align="center">
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #FFFFFF; border: 1px solid #E4E1DB; border-radius: 12px; overflow: hidden; text-align: left; border-collapse: collapse; max-width: 600px;">
          <!-- Header Band -->
          <tr style="background-color: #EAF2F6;">
            <td style="padding: 24px 30px; border-bottom: 1px solid #E4E1DB;">
              <span style="font-size: 24px; font-weight: bold; color: #3F6C86;">Sakoon AI 🫶</span>
            </td>
          </tr>
          <!-- Main Content -->
          <tr>
            <td style="padding: 30px;">
              <p style="font-size: 16px; color: #2B2B2B; margin-top: 0; font-weight: bold; {'direction: rtl; text-align: right;' if lang == 'urdu' else ''}">{greeting},</p>
              <p style="font-size: 14px; color: #2B2B2B; line-height: 1.5; margin-bottom: 24px; {'direction: rtl; text-align: right;' if lang == 'urdu' else ''}">{intro}</p>
              
              <!-- Card: Session Summary -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FAF9F7; border: 1px solid #E4E1DB; border-radius: 8px; margin-bottom: 16px; border-collapse: collapse;">
                <tr>
                  <td style="padding: 16px; {'direction: rtl; text-align: right;' if lang == 'urdu' else ''}">
                    <h4 style="margin: 0 0 8px 0; font-size: 15px; color: #3F6C86;">{summary_title}</h4>
                    <p style="margin: 0; font-size: 14px; color: #2B2B2B; line-height: 1.5; font-style: italic;">{narrative_display}</p>
                  </td>
                </tr>
              </table>

              <!-- Card: Symptoms & Triggers -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FAF9F7; border: 1px solid #E4E1DB; border-radius: 8px; margin-bottom: 16px; border-collapse: collapse;">
                <tr>
                  <td style="padding: 16px; {'direction: rtl; text-align: right;' if lang == 'urdu' else ''}">
                    <h4 style="margin: 0 0 8px 0; font-size: 15px; color: #3F6C86;">{symptoms_triggers_title}</h4>
                    
                    <p style="margin: 8px 0 4px 0; font-size: 13px; font-weight: bold; color: #3F6C86;">{"علامات:" if lang == "urdu" else "Symptoms:"}</p>
                    <ul style="margin: 0 0 12px 0; padding-left: 20px; font-size: 14px; color: #2B2B2B; line-height: 1.5; {'padding-right: 20px; padding-left: 0;' if lang == 'urdu' else ''}">
                      {symptoms_html}
                    </ul>

                    <p style="margin: 0 0 4px 0; font-size: 13px; font-weight: bold; color: #3F6C86;">{"محرکات:" if lang == "urdu" else "Possible Triggers:"}</p>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #2B2B2B; line-height: 1.5; {'padding-right: 20px; padding-left: 0;' if lang == 'urdu' else ''}">
                      {triggers_html}
                    </ul>
                  </td>
                </tr>
              </table>

              <!-- Card: Self-Care Plan -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FAF9F7; border: 1px solid #E4E1DB; border-radius: 8px; margin-bottom: 16px; border-collapse: collapse;">
                <tr>
                  <td style="padding: 16px; {'direction: rtl; text-align: right;' if lang == 'urdu' else ''}">
                    <h4 style="margin: 0 0 8px 0; font-size: 15px; color: #3F6C86;">{self_care_title}</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #2B2B2B; line-height: 1.5; {'padding-right: 20px; padding-left: 0;' if lang == 'urdu' else ''}">
                      {care_html}
                    </ul>
                  </td>
                </tr>
              </table>

              <!-- Card: Support -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FAF9F7; border: 1px solid #E4E1DB; border-radius: 8px; margin-bottom: 24px; border-collapse: collapse;">
                <tr>
                  <td style="padding: 16px; {'direction: rtl; text-align: right;' if lang == 'urdu' else ''}">
                    <h4 style="margin: 0 0 8px 0; font-size: 15px; color: #3F6C86;">{support_title}</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #2B2B2B; line-height: 1.5; {'padding-right: 20px; padding-left: 0;' if lang == 'urdu' else ''}">
                      {support_html}
                    </ul>
                  </td>
                </tr>
              </table>
              
              <p style="font-size: 14px; color: #6B6B6B; line-height: 1.5; {'direction: rtl; text-align: right;' if lang == 'urdu' else ''}">{attachment_notice}</p>
            </td>
          </tr>
          <!-- Footer -->
          <tr style="background-color: #FAF9F7; border-top: 1px solid #E4E1DB;">
            <td style="padding: 24px 30px; text-align: center;">
              <p style="margin: 0 0 8px 0; font-size: 11px; color: #6B6B6B; line-height: 1.4; font-style: italic;">
                {disclaimer_text}
              </p>
              <p style="margin: 0; font-size: 12px; color: #6B6B6B; font-weight: bold;">
                {sent_with_care}
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

        # ── Build MIMEMultipart Email ────────────────────────────────────────
        msg = MIMEMultipart("mixed")
        msg["From"] = sender_email
        msg["To"] = recipient
        msg["Subject"] = Header("Your Wellness Session Summary — Sakoon AI 🫶", "utf-8")
        
        alt_part = MIMEMultipart("alternative")
        alt_part.attach(MIMEText(plain_body, "plain", "utf-8"))
        alt_part.attach(MIMEText(html_body, "html", "utf-8"))
        msg.attach(alt_part)
        
        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(pdf_part)
        
        # ── SMTP Connect and Login ───────────────────────────────────────────
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipient, msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipient, msg.as_string())
                
        logging.getLogger(__name__).info(f"Email wellness report successfully sent to {recipient}")
        return True
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to send email to {recipient}: {e}\n{traceback.format_exc()}")
        return False
