import base64

import pandas as pd
import streamlit as st
from pandas.io.formats.style_render import CSSDict
from st_supabase_connection import SupabaseConnection
from streamlit_option_menu import option_menu

from review import review
from submit import submit

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
    .st-key-review_button button {
        margin-top: 28px !important;
        outline: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.dialog("제출하시겠습니까?")
def submit_confirm_dialog():
    st.write("답안은 하루에 한 번만 제출할 수 있습니다.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("확인", use_container_width=True, key="confirm_button-1"):
            st.session_state.submit_confirmed = True
            st.rerun()
    with col2:
        if st.button("취소", use_container_width=True, key="cancel_button-1"):
            st.session_state.submit_confirmed = False
            st.rerun()

@st.dialog("지금은 제출할 수 없습니다.")
def submit_deny_dialog():
    st.write("답안은 당일 오후 10시 이전에 제출해야 합니다.")

@st.dialog("검토하시겠습니까?")
def review_confirm_dialog():
    st.write("파일을 불러오거나 채점하는 도중 페이지를 새로고침하지 마세요.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("확인", use_container_width=True, key="confirm_button-2"):
            st.session_state.review_confirmed = True
            st.rerun()
    with col2:
        if st.button("취소", use_container_width=True, key="cancel_button-2"):
            st.session_state.review_confirmed = False
            st.rerun()

LOGO_BASE64 = base64.b64encode(open("public/CERL_logo.png", "rb").read()).decode()
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]


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
        f"<img src='data:image/png;base64,{LOGO_BASE64}' style='width:150px; height:150px; margin-bottom: 4px;'>"
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
        "<h1 style='margin-top: 0px; margin-bottom: 0px; padding-top: 0px; padding-bottom: 0px; line-height: 1.5; text-align:center;'>"
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
                    {'selector': 'th.row_heading, td.row_heading, th.index_name', 'props': [('width', '5%')]},
                    {'selector': 'th.col0, td.col0', 'props': [('width', '19%')]},
                    {'selector': 'th.col1, td.col1', 'props': [('width', '19%')]},
                    {'selector': 'th.col2, td.col2', 'props': [('width', '19%')]},
                    {'selector': 'th.col3, td.col3', 'props': [('width', '19%')]},
                    {'selector': 'th.col4, td.col4', 'props': [('width', '19%')]}
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

        is_file_not_exist = None
        is_filename_invalid = None
        is_num_not_exist = None
        is_name_not_exist = None

        file = st.file_uploader("NetCDF 파일을 선택하세요.", type=["nc"])

        num_input, name_input, submit_button = st.columns([3, 3, 1])
        with num_input:
            student_num = st.text_input("학번을 입력하세요.")
        with name_input:
            student_name = st.text_input("이름을 입력하세요.")
        with submit_button:
            if st.button("제출하기", key="submit_button", use_container_width=True):
                submit_confirm_dialog()

        if st.session_state.get("submit_confirmed"):
            st.session_state.submit_confirmed = False
            submit(file, student_num, student_name)

        st.markdown(
            "<p style='color: #909090; font-size: 14px;'>"
            "답안은 하루에 한 번만 제출할 수 있으며, 오후 10시 이전에 제출된 답안만 당일의 답안으로 인정됩니다.<br>"
            "자세한 사항은 규칙을 참고하세요."
            "</p>",
            unsafe_allow_html=True
        )

        st.markdown("#### 대회의 관리자이신가요?")
        st.markdown("##### 관리자 비밀번호를 입력하고 제출된 답안을 검토하세요.")

        password_input, review_button = st.columns([6, 1])

        with password_input:
            password = st.text_input("관리자 비밀번호를 입력하세요.")
        with review_button:
            if st.button("검토하기", key="review_button", use_container_width=True):
                review_confirm_dialog()

        st.markdown(
            "<p style='color: #909090; font-size: 14px;'>"
            "파일을 불러오거나 채점하는 도중 페이지를 새로고침하지 마세요."
            "</p>",
            unsafe_allow_html=True
        )

        if st.session_state.get("review_confirmed"):
            st.session_state.review_confirmed = False
            review(password)


    if selected == "Rules":
        st.markdown(
            "<h2 style='margin-top: 0px; margin-bottom: 0px; line-height: 0.5;'>"
            "Rules"
            "</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<h6 style='line-height: 1.5;'>"
            "대회 참가에 앞서 아래의 규칙을 반드시 확인해 주시기 바랍니다.<br>"
            "규칙을 숙지하지 않거나 준수하지 않아 발생하는 불이익에 대한 책임은 참가자에게 있습니다.<br>"
            "기타 문의 사항은 'ycj1219@pukyong.ac.kr'로 연락하시기 바랍니다."
            "</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            """
            #### 규칙
            - 모든 팀은 매일 22:00 이전까지 하루에 한 번 결과물을 제출할 수 있습니다.
            - 동일한 팀에서 하루에 여러 개의 결과물을 제출한 경우, 22:00 이전에 제출된 파일 중 가장 마지막으로 제출된 결과물만 평가합니다.
            - 제출 파일 이름은 반드시 "pred_Y_팀명.nc" 형식으로 지정해야 합니다. 파일 형식이 일치하지 않는 경우 평가를 진행하지 않습니다.
            - 제공된 "pred_Y_팀명.nc" 파일은 제출용 템플릿입니다. 파일에서 NaN이 아닌 지점의 초기값 0을 모델의 예측값으로 변경하여 제출해야 합니다.
            - 기존 NaN 지점은 그대로 유지해야 하며, 변수명, 차원, 위도·경도·시간 좌표 및 배열 구조를 변경해서는 안 됩니다. 형식이 일치하지 않는 경우 평가를 진행하지 않습니다.
            - 제공된 "train_Y.nc"의 Vc,max,25는 모델의 학습 "목표"만 사용해야 합니다. Vc,max,25를 입력 변수 혹은 튜닝 등 후처리에 사용하는 것을 금지합니다.
            - Vc,max,25로부터 직접 계산된 파생 변수를 입력 자료로 사용하는 것을 금지합니다. 또한 외부의 Vc,max,25 데이터를 모델 학습에 사용할 수 없습니다.
            - 참가자들은 대회에서 제공하는 입력 자료 이외에 대기와 관련한 외부 데이터를 추가적으로 사용할 수 있습니다.
            - Land cover, LAI, GPP 등 지면·식생·생태계와 관련된 변수는 사용할 수 없습니다.
            - 특정 외부 데이터의 사용 가능 여부가 불분명한 경우 반드시 사전에 이메일로 문의해 주시기 바랍니다.
            - 외부 데이터는 모든 참가자가 접근할 수 있는 공개 데이터만 사용할 수 있습니다. (예: ERA5)
            - 참가 팀 간 예측 결과 또는 모델 결과물을 공유하는 것을 금지합니다. 비정상적으로 높은 수준의 일치가 확인되는 경우 주최측은 모델 코드 및 관련 자료의 추가 제출을 요구할 수 있습니다. 무단 공유가 확인될 경우 관련 팀은 실격 처리될 수 있습니다.
            
            #### 최종 파일 제출 및 검증
            - 최종 평가에 사용할 파일은 12월 5일 18:00까지 사이트에 제출해야 합니다. 마감 시간 이후 제출된 파일은 절대 인정하지 않습니다.
            - 최종 평가에 사용할 파일을 별도로 제출하지 않는 경우, 대회 기간 중 제출한 결과물 가운데 가장 높은 성적을 기록한 파일을 자동으로 최종 평가 파일로 선정합니다.
            - 최종 결과는 12월 5일 22:00 이후 사이트를 통해 공개하며, 평가 결과 1위부터 5위까지의 팀을 예비 수상자로 선정합니다.
            - 예비 수상자는 12월 6일부터 12월 8일까지 최종 제출 결과를 생성한 모델의 전체 실행 코드를 제출해야 합니다.
            - 외부 데이터를 사용한 경우 해당 데이터의 출처, 사용 변수 및 전처리 방법을 함께 제출해야 합니다.
            - 제출된 코드는 대회 규칙 준수 여부와 제출 결과의 재현 가능 여부를 검증하는 데 사용됩니다.
            - 검증 과정에서 필요한 경우 주최측은 예비 수상자에게 추가적인 코드, 데이터 또는 설명 자료의 제출을 요구할 수 있습니다.
            - 규칙 위반 또는 결과 재현 실패 중 하나 이상의 결격 사유가 확인되는 경우 해당 팀은 실격 처리되며 예비 수상자 자격이 취소됩니다.
            - 실격으로 인해 수상 인원에 결원이 발생하는 경우, 차순위 팀을 새로운 예비 수상자로 선정하여 동일한 검증 절차를 진행합니다.
            - 모든 검증 절차가 완료된 후 12월 12일 최종 수상자를 발표합니다.            
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
