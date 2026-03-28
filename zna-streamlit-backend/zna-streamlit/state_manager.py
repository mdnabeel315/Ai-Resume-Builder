"""
State Manager — single source of truth for Streamlit session state.

All pages read/write resume data through these helpers.
This eliminates the bug where page B can't see data set on page A.
"""

import streamlit as st
from typing import Any


# ── Keys ──────────────────────────────────────────────────────────────────────
_PARSED_KEY   = "zna_parsed_data"
_RESUME_KEY   = "zna_resume_data"
_CL_KEY       = "zna_cover_letter"
_ATS_KEY      = "zna_ats_result"
_JOB_DESC_KEY = "zna_job_description"
_ATS_HISTORY  = "zna_ats_history"
_TARGET_TITLE = "zna_target_job_title"


def _init_defaults() -> None:
    defaults = {
        _PARSED_KEY:   None,
        _RESUME_KEY:   None,
        _CL_KEY:       None,
        _ATS_KEY:      None,
        _JOB_DESC_KEY: "",
        _ATS_HISTORY:  [],
        _TARGET_TITLE: "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_defaults()


# ── Getters / Setters ─────────────────────────────────────────────────────────
def get_parsed_data() -> dict | None:
    return st.session_state.get(_PARSED_KEY)

def set_parsed_data(data: dict) -> None:
    st.session_state[_PARSED_KEY] = data


def get_resume() -> dict | None:
    return st.session_state.get(_RESUME_KEY)

def set_resume(data: dict) -> None:
    st.session_state[_RESUME_KEY] = data
    # Track ATS score history for the dashboard chart
    score = data.get("ats_score")
    if isinstance(score, (int, float)) and score > 0:
        history: list = st.session_state.get(_ATS_HISTORY, [])
        history.append(int(score))
        st.session_state[_ATS_HISTORY] = history[-10:]  # keep last 10


def get_cover_letter() -> dict | None:
    return st.session_state.get(_CL_KEY)

def set_cover_letter(data: dict) -> None:
    st.session_state[_CL_KEY] = data


def get_ats_result() -> dict | None:
    return st.session_state.get(_ATS_KEY)

def set_ats_result(data: dict) -> None:
    st.session_state[_ATS_KEY] = data
    # Append to history
    score = data.get("overall_score")
    if isinstance(score, (int, float)):
        history: list = st.session_state.get(_ATS_HISTORY, [])
        history.append(int(score))
        st.session_state[_ATS_HISTORY] = history[-10:]


def get_ats_history() -> list[int]:
    return st.session_state.get(_ATS_HISTORY, [])


def get_job_description() -> str:
    return st.session_state.get(_JOB_DESC_KEY, "")

def set_job_description(jd: str) -> None:
    st.session_state[_JOB_DESC_KEY] = jd


def get_target_title() -> str:
    return st.session_state.get(_TARGET_TITLE, "")

def set_target_title(title: str) -> None:
    st.session_state[_TARGET_TITLE] = title


def has_resume() -> bool:
    return st.session_state.get(_RESUME_KEY) is not None


def clear_all() -> None:
    for k in [_PARSED_KEY, _RESUME_KEY, _CL_KEY, _ATS_KEY, _JOB_DESC_KEY, _TARGET_TITLE]:
        st.session_state[k] = None
