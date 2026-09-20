import streamlit as st
from st_supabase_connection import SupabaseConnection

from datetime import datetime, time
from zoneinfo import ZoneInfo


conn = st.connection("supabase", type=SupabaseConnection)
supabase = conn.client

def submit(file, snum, sname):
    if not file: st.warning("파일을 선택하세요!"); return
    elif not file.name.startswith("pred_Y_") or not file.name.endswith(".nc"):
        st.warning("파일명은 'pred_Y_팀명.nc' 형식이어야 합니다."); return
    if not snum: st.warning("학번을 입력하세요!"); return
    if not sname: st.warning("이름을 입력하세요!"); return

    current_time = datetime.now(ZoneInfo("Asia/Seoul")).time()
    cutoff_time = time(22, 0, 0)

    if current_time >= cutoff_time:
        st.warning("답안은 당일 오후 10시 이전에 제출해야 합니다.")

    upload(file)

def upload(file):
    with st.spinner("업로드 중..."):
        try:
            # 메모리에 로드된 바이너리 데이터 읽기
            file_bytes = file.getvalue()

            # 저장할 스토리지 경로 지정
            bucket_name = "pknu_climate_big_data_contest_2026"
            storage_path = f"submissions/09_19/{file.name}"

            # Supabase Storage 표준 업로드 실행
            response = supabase.storage.from_(bucket_name).upload(
                path=storage_path,
                file=file_bytes,
                file_options={
                    "content-type": "application/x-netcdf",
                    "x-upsert": "true"
                }
            )

            st.success(f"🎉 업로드 성공! 경로: `{storage_path}`")

        except Exception as e:
            st.error(f"❌ 업로드 실패: {str(e)}")
