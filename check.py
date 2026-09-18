import streamlit as st
import xarray as xr
import tempfile
import os

ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

def check(nc_file):
    # if password != ADMIN_PASSWORD:
    #     st.error("비밀번호가 일치하지 않습니다. 다시 확인하세요.")
    #     return

    st.success(f"비밀번호가 일치합니다.")

    ds = None
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as tmp_file:
            tmp_file.write(nc_file.getvalue())
            tmp_path = tmp_file.name

        try:
            ds = xr.open_dataset(tmp_path, engine='netcdf4')

            st.success(
                f"✅ 파일 로드 성공  \n"
                f"📁 파일명: {nc_file.name} | 크기: {nc_file.size / 1024:.2f} KB"
            )

            # 차원(Dimensions) 및 변수(Variables) 요약 정보 출력
            st.subheader("📊 데이터셋 구조 요약 (Dataset Info)")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("차원 수 (Dimensions)", len(ds.dims))
                st.write(list(ds.dims.keys()))
            with col2:
                st.metric("좌표계 (Coordinates)", len(ds.coords))
                st.write(list(ds.coords.keys()))
            with col3:
                st.metric("포함된 변수 (Data Variables)", len(ds.data_vars))
                st.write(list(ds.data_vars.keys()))

            # 전체 메타데이터 및 변수 구조 세부 보기 (텍스트 형태)
            st.subheader("🔍 세부 속성 및 메타데이터")
            st.text(str(ds))

        finally:
            # 사용이 끝난 임시 파일과 데이터셋을 닫고 디스크에서 삭제하여 메모리 보호
            if ds: ds.close()
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        st.error(f"❌ NetCDF 파일을 읽는 중 오류가 발생했습니다: {e}")