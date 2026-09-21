from datetime import datetime, time
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from sqlglot.expressions import Null
from st_supabase_connection import SupabaseConnection

conn = st.connection("supabase", type=SupabaseConnection)
client = conn.client

def submit(file, snum, sname):
    if not file: st.warning("파일을 선택하세요!"); return
    elif not file.name.startswith("pred_Y_") or not file.name.endswith(".nc"):
        st.warning("파일명은 'pred_Y_팀명.nc' 형식이어야 합니다."); return
    if not snum: st.warning("학번을 입력하세요!"); return
    if not sname: st.warning("이름을 입력하세요!"); return

    curr_time = datetime.now(ZoneInfo("Asia/Seoul")).time()
    cutoff_time = time(22, 0, 0)

    if curr_time >= cutoff_time:
        st.warning("답안은 당일 오후 10시 이전에 제출해야 합니다.")
        return

    try:
        rows = client.table("team_member").select("*").execute()
        df = pd.DataFrame(rows.data)

        target_row = df[(df["student_number"] == snum) & (df["student_name"] == sname)]
        if target_row.empty:
            st.error(
                f"❌ {snum} {sname} 학생은 참가자 명단에 없습니다."
                f"문제가 있다면 'ycj1219@pukyong.ac.kr'로 연락하시기 바랍니다."
            )
            return

        row_dict = target_row.iloc[0].to_dict()
        team_name = row_dict["team_name"]
        submit_team_name = file.name[7:-3]

        if team_name is None:
            st.error(
                f"❌ {snum} {sname} 학생은 참가자 명단에 있지만 팀이 없습니다."
                f"문제가 있다면 'ycj1219@pukyong.ac.kr'로 연락하시기 바랍니다."
            )
            return
        elif team_name != submit_team_name:
            st.error(
                f"❌ {snum} {sname} 학생은 참가자 명단에 있지만 {submit_team_name} 팀이 아닙니다."
                f"문제가 있다면 'ycj1219@pukyong.ac.kr'로 연락하시기 바랍니다."
            )
            return

    except Exception as e:
        st.error(f"❌ 자격 검증 실패: {str(e)}")
        return

    upload(file)

def upload(file):
    with st.spinner("업로드 중..."):
        try:
            file_bytes = file.getvalue()

            curr_date = datetime.now(ZoneInfo("Asia/Seoul"))
            curr_mm_dd = curr_date.strftime("%m-%d")

            # 저장할 스토리지 경로 지정
            bucket_name = "pknu_climate_big_data_contest_2026"
            storage_path = f"submissions/{curr_mm_dd}/{file.name}"

            # Supabase Storage 표준 업로드 실행
            response = client.storage.from_(bucket_name).upload(
                path=storage_path,
                file=file_bytes,
                file_options={
                    "content-type": "application/x-netcdf",
                    "x-upsert": "true"
                }
            )

            st.success(f"🎉 업로드 성공!")

        except Exception as e:
            st.error(f"❌ 업로드 실패: {str(e)}")
