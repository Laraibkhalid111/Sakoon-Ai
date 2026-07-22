"""Login / register gate UI (Phase 5)."""

from __future__ import annotations

import streamlit as st

from sakoon.core.metrics import emit
from sakoon.core.rate_limit import allow_auth
from sakoon.services.auth import authenticate, register_user
from sakoon.ui.components import render_brand_header
from sakoon.ui.session_ops import bootstrap_authenticated_session


def render_auth_gate(lang: str = "english") -> bool:
    """
    Show login/register. Returns True when the user is authenticated.
    """
    if st.session_state.get("authenticated") and st.session_state.get("db_user_id"):
        return True

    render_brand_header(lang)
    st.markdown('<div class="sakoon-auth-shell">', unsafe_allow_html=True)
    st.markdown("### Sign in to Sakoon")
    st.caption(
        "Your chats, mood logs, and journal stay private to your account."
        if lang != "urdu"
        else "آپ کی گفتگو، مزاج اور جرنل صرف آپ کے اکاؤنٹ میں محفوظ رہتے ہیں۔"
    )

    tab_login, tab_register = st.tabs(
        ["Sign in", "Create account"] if lang != "urdu" else ["سائن اِن", "اکاؤنٹ بنائیں"]
    )

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            key = (username or "").strip().lower() or "unknown"
            rl = allow_auth(key)
            if not rl.allowed:
                emit("rate_limited_auth", action="login")
                st.error(f"Too many attempts. Try again in {max(1, int(rl.retry_after_sec) + 1)} seconds.")
            else:
                ok, msg, user = authenticate(username, password)
                if ok and user:
                    emit("auth_login_ok", user_id=user.get("id"))
                    bootstrap_authenticated_session(user)
                    st.success(msg)
                    st.rerun()
                else:
                    emit("auth_login_fail")
                    st.error(msg)

    with tab_register:
        with st.form("register_form", clear_on_submit=False):
            r_user = st.text_input("Username", key="reg_username", help="3–32 letters, numbers, underscore")
            r_name = st.text_input("Display name (optional)", key="reg_name")
            r_email = st.text_input("Email (optional)", key="reg_email")
            r_pass = st.text_input("Password", type="password", key="reg_password")
            r_pass2 = st.text_input("Confirm password", type="password", key="reg_password2")
            created = st.form_submit_button("Create account", type="primary", use_container_width=True)
        if created:
            key = (r_user or "").strip().lower() or "unknown"
            rl = allow_auth(f"reg:{key}")
            if not rl.allowed:
                emit("rate_limited_auth", action="register")
                st.error(f"Too many attempts. Try again in {max(1, int(rl.retry_after_sec) + 1)} seconds.")
            elif r_pass != r_pass2:
                st.error("Passwords do not match.")
            else:
                ok, msg, uid = register_user(
                    username=r_user,
                    password=r_pass,
                    name=r_name or None,
                    email=r_email or None,
                    preferred_language=lang if lang in ("english", "urdu", "roman_urdu") else "english",
                )
                if ok:
                    emit("auth_register_ok", user_id=uid)
                    st.success(msg)
                    # Auto sign-in after register
                    ok2, _, user = authenticate(r_user, r_pass)
                    if ok2 and user:
                        bootstrap_authenticated_session(user)
                        st.rerun()
                else:
                    emit("auth_register_fail")
                    st.error(msg)

    st.caption(
        "Sakoon AI is not a substitute for professional mental health care."
    )
    st.markdown("</div>", unsafe_allow_html=True)
    return False


def render_account_sidebar() -> None:
    """Show signed-in user + logout in the sidebar."""
    username = st.session_state.get("auth_username") or "user"
    st.caption(f"Signed in as **{username}**")
    if st.button("Log out", use_container_width=True, key="btn_logout"):
        from sakoon.ui.session_ops import logout_user

        logout_user()
        st.rerun()
