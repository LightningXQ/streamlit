import pandas as pd
import streamlit as st
from pandas.io.formats.style_render import CSSDict
from st_supabase_connection import SupabaseConnection
from streamlit_option_menu import option_menu
import base64
from datetime import datetime, time

from check import check
from upload import upload


st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    div[data-testid="stViewerBadge"] {
        display: none !important;
    }
    footer {
        visibility: hidden;
    }
    .st-key-confirm_button button {
        background-color: #4DB343 !important;
        color: white !important;
        border: none !important;
        outline: none !important;
    }
    .st-key-cancel_button button {
        background-color: #C14550 !important;
        color: white !important;
        border: none !important;
    }
    .st-key-submit_button button {
        margin-top: 28px !important;
        outline: none !important;
    }
    .st-key-review-button button {
    div[class*="st-key-email_container"] {
        background-color: #F0F2F6 !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.dialog("제출하시겠습니까?")
def confirm_dialog():
    st.write("답안은 하루에 한 번만 제출할 수 있습니다.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("확인", use_container_width=True, key="confirm_button"):
            st.session_state.confirmed = True
            st.rerun()
    with col2:
        if st.button("취소", use_container_width=True, key="cancel_button"):
            st.session_state.confirmed = False
            st.rerun()

@st.dialog("지금은 제출할 수 없습니다.")
def submit_deny_dialog():
    st.write("답안은 당일 오후 10시 이전에 제출해야 합니다.")

LOGO_BASE64 = base64.b64encode(open("public/CERL_logo.png", "rb").read()).decode()


with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Leaderboard", "Submit", "Rules", "Info"],
        default_index=0,
        styles={
            "container": {"padding": "5px!", "background-color": "#fafafa"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#02ab21"},
        }
    )

left_margin, center, right_margin = st.columns([1, 5, 1])

with center:
    st.markdown(
        "<div style='text-align: center;'>"
        f"<img src='data:image/png;base64,{LOGO_BASE64}' style='width:120px; height:120px; margin-bottom: 4px;'>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h5 style='margin-top: 0px; margin-bottom: 0px; padding-top: 0px; padding-bottom: 0px; line-height: 1.2; text-align:center;'>"
        "Climate Extremes Research Lab"
        "</h5>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h6 style='margin-top: 0px; margin-bottom: 12px; padding-top: 0px; padding-bottom: 0px; line-height: 1.2; text-align:center;'>"
        "Pukyong National University"
        "</h6>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h1 style='margin-top: 0px; margin-bottom: 0px; padding-top: 0px; padding-bottom: 0px; line-height: 1.2; text-align:center;'>"
        "기상·기후 환경분야 빅데이터 경진대회"
        "</h1>",
        unsafe_allow_html=True
    )

    st.divider()

    if selected == "Leaderboard":
        st.markdown(
            "<h2 style='margin-top: 0px; margin-bottom: 0px; line-height: 0.5;'>"
            "Leaderboard"
            "</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            '<p style="margin-top: 0px; color: gray; font-size: 14px;">'
            '매일 0시마다 점수가 반영됩니다.'
            '</p>',
            unsafe_allow_html=True
        )

        conn = st.connection("supabase", type=SupabaseConnection)
        supabase = conn.client

        try:
            rows = supabase.table("leaderboard").select("*").execute()

            if not rows.data:
                st.info("리더보드 데이터가 없습니다.")
            else:
                df = pd.DataFrame(rows.data)

                if "best_score" in df.columns:
                    df = df.sort_values(by="best_score", ascending=False)

                df = df.reset_index(drop=True)
                df.index += 1

                table_styles: list[CSSDict] = [
                    {
                        'selector': '',
                        'props': [
                            ('width', '100%')
                        ]
                    },
                    {
                        'selector': 'th',
                        'props': [
                            ('font-size', '20px'),
                            ('text-align', 'center'),
                            ('font-weight', 'bold'),
                            ('background-color', '#f2f2f2')
                        ]
                    },
                    {'selector': 'th.row_heading, td.row_heading, th.index_name', 'props': [('width', '7%')]},
                    {'selector': 'th.col0, td.col0', 'props': [('width', '31%')]},
                    {'selector': 'th.col1, td.col1', 'props': [('width', '31%')]},
                    {'selector': 'th.col2, td.col2', 'props': [('width', '31%')]}
                ]

                styled_df = df.style \
                    .set_properties(**{
                        'font-size': '18px',
                        'text-align': 'center',
                    }) \
                    .set_table_styles(table_styles) \
                    .to_html()

                st.markdown(
                    f'<div style="width: 100%;">{styled_df}</div>',
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"오류 발생: {e}")

    if selected == "Submit":
        st.markdown(
            "<h2 style='margin-top: 0px; margin-bottom: 0px; line-height: 0.5;'>"
            "Submit"
            "</h2>",
            unsafe_allow_html=True
        )

        st.markdown("#### 대회의 참가자이신가요?")
        st.markdown("##### 답안을 작성한 NetCDF(.nc) 파일을 제출하세요.")
        st.markdown(
            "<p style='color: #909090; font-size: 14px;'>"
            "답안은 하루에 한 번만 제출할 수 있으며, 오후 10시 이전에 제출된 답안만 당일의 답안으로 인정됩니다.<br>"
            "자세한 사항은 규칙을 참고하세요."
            "</p>",
            unsafe_allow_html=True
        )

        is_file_not_exist = False
        is_filename_not_valid = False
        is_num_not_exist = False
        is_name_not_exist = False

        nc_file = st.file_uploader("NetCDF 파일을 선택하세요.", type=["nc"])

        num_input, name_input, submit_button = st.columns([3, 3, 1])
        with num_input:
            student_num = st.text_input("학번을 입력하세요.")
        with name_input:
            student_name = st.text_input("이름을 입력하세요.")
        with submit_button:
            if st.button("제출하기", key="submit_button", use_container_width=True):
                if not nc_file: is_file_not_exist = True
                elif not nc_file.name.startswith("pred_Y_") or not nc_file.name.endswith(".nc"):
                    is_filename_not_valid = True
                if not student_num: is_num_not_exist = True
                if not student_name: is_name_not_exist = True

                if nc_file and student_num and student_name and not is_filename_not_valid:
                    current_time = datetime.now().time()
                    cutoff_time = time(23, 58, 0)

                    if current_time >= cutoff_time:
                        submit_deny_dialog()
                    else:
                        confirm_dialog()

        if st.session_state.get("confirmed"):
            upload(nc_file)
            st.session_state.confirmed = False

        if is_file_not_exist: st.warning("파일을 선택하세요!")
        if is_filename_not_valid: st.warning("파일명은 'pred_Y_팀명.nc' 형식이어야 합니다.")
        if is_num_not_exist: st.warning("학번을 입력하세요!")
        if is_name_not_exist: st.warning("이름을 입력하세요!")

        st.markdown("#### 대회의 관리자이신가요?")
        st.markdown("##### 관리자 비밀번호를 입력하고 제출된 답안을 검토하세요.")

        password = st.text_input("관리자 비밀번호를 입력하세요.")

        if st.button("검토하기", key="review-button"):
            if password and nc_file:
                pass
                # confirm_dialog()
            else:
                if not password: st.warning("관리자 비밀번호를 입력하세요!")
                if not nc_file: st.warning("파일을 선택하세요!")

        if st.session_state.get("confirmed"):
            check(nc_file)
            st.session_state.confirmed = False

    if selected == "Rules":
        st.markdown(
            "<h2 style='margin-top: 0px; margin-bottom: 0px; line-height: 0.5;'>"
            "Rules"
            "</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            """
            - Each team may submit once per day before 10:00 PM.
            - If multiple submissions are received from the same team on the same day, only the latest valid submission received before 10:00 PM will be evaluated.
            - The submission file must be named "pred_Y_팀명.nc". If the file name or format does not follow the specified convention, the submission will not be evaluated and the score will not be released.
            - Only predictions at the predefined valid grid cells will be evaluated. The grid, coordinates, dimensions, and missing-value mask must not be modified.
            - Using the target variable or any information directly derived from the target variable as an input is strictly prohibited.
            - Using the target variable from the evaluation period, or any statistics calculated from it, for model training, validation, tuning, calibration, or post-processing is strictly prohibited.
            - Participants may not use any external Vc,max product or any variable that can serve as a direct proxy for the target variable.
            - Additional external data may be used only if they are related to atmospheric or meteorological variables.
            - All external data must be publicly accessible to all participants.
            - Land-surface or vegetation-related variables, including land cover and LAI, may not be used.
            - For final submissions: If additional external data are used, participants must provide the data source(s) and the pre-processing code used to prepare them.
            - For final submissions: The final prediction file must be named "Final_TeamName_Y.nc". The final submission deadline must be strictly observed; submissions received after the deadline will not be accepted.
            - For final submissions: Participants must submit code that can reproduce the submitted model and training process. If the submitted results cannot be reproduced, the team may be disqualified.
            - For final submissions: If two or more teams submit prediction fields that are identical to five or more decimal places across all valid evaluation grid cells, the submissions will be investigated for unauthorized sharing. If unauthorized sharing of predictions or code is confirmed, all involved teams will be disqualified.
            """
        )

    if selected == "Info":
        st.markdown(
            "<h2 style='margin-top: 0px; margin-bottom: 0px; line-height: 0.5;'>"
            "Info"
            "</h2>",
            unsafe_allow_html=True
        )
        st.markdown("#### Hosted by Climate Extremes Research Lab")
        with st.container(key="email_container-2"):
            st.markdown(
                '<span style="font-size: 20px;">'
                'https://sites.google.com/view/cerl'
                '</span>',
                unsafe_allow_html=True
            )
        st.markdown("#### Managed by Yechan Jeong")
        with st.container(key="email_container-3"):
            st.markdown(
                '<span style="font-size: 20px;">'
                'ycj1219@pukyong.ac.kr'
                '</span>',
                unsafe_allow_html=True
            )
