import streamlit as st
from st_supabase_connection import SupabaseConnection

conn = st.connection("supabase", type=SupabaseConnection)
supabase = conn.client

def upload(nc_file):
    with st.spinner("업로드 중..."):
        try:
            # 메모리에 로드된 바이너리 데이터 읽기
            file_bytes = nc_file.getvalue()

            # 저장할 스토리지 경로 지정
            bucket_name = "submissions"
            storage_path = f"2026_09_19/{nc_file.name}"

            # Supabase Storage 표준 업로드 실행
            response = supabase.storage.from_(bucket_name).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": "application/x-netcdf", "x-upsert": "false"}
            )

            st.success(f"🎉 업로드 성공! 경로: `{storage_path}`")

        except Exception as e:
            st.error(f"❌ 업로드 실패: {str(e)}")
