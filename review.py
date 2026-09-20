# TODO: Database와 Bucket에서 RLS 정책 수정하기(임시로 secret key로 접속함)

import os
import tempfile
from pathlib import Path

import numpy as np
import streamlit as st
import xarray as xr
from st_supabase_connection import SupabaseConnection

ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

TARGET_VAR = os.environ.get("TARGET_VAR", "Vcmax25")
REQUIRED_DIMS = ("time", "lat", "lon")


conn = st.connection("supabase", type=SupabaseConnection)
client = conn.client

def review(password):
    if not verify(password):
        st.warning("비밀번호가 일치하지 않습니다."); return
    else: st.info("비밀번호가 일치합니다.")
    result = download_submissions()
    if not result:
        st.error(f"❌ 채점 결과가 없습니다."); return
    update_leaderboard(result)

def verify(password):
    return password == ADMIN_PASSWORD

def download_submissions():
    bucket_name = "pknu_climate_big_data_contest_2026"
    submission_path = "/submissions/09_19/"
    answer_path = "/answer"

    with st.spinner("Supabase에서 파일 목록을 가져오는 중..."):
        answer_storage = client.storage.from_(bucket_name).list(answer_path)
        answer_files =  [f for f in answer_storage]
        # answer_files =  [f for f in answer_storage if f["name"].endswith(".nc")]
        submission_storage = client.storage.from_(bucket_name).list(submission_path)
        submission_files = [f for f in submission_storage if f["name"].endswith(".nc")]
        answer_file = answer_files[0] if answer_files else None

        if not answer_file:
            st.error(f"⚠️ `{answer_path}` 폴더에 정답 NetCDF 파일이 존재하지 않습니다.")
            return None
        elif not submission_files:
            st.warning(f"⚠️ `{submission_path}` 폴더에 답안 NetCDF 파일이 존재하지 않습니다.")
        else:
            st.write(f"📦 `{answer_path}`폴더와 `{submission_path}` 폴더에서 총 {len(submission_files) + 1}개의 NetCDF 파일을 발견했습니다.")

    # 임시 디렉토리 생성 (with 블록을 빠져나오면 자동으로 삭제됨)
    with tempfile.TemporaryDirectory() as temp_dir:
        st.write(f"📁 임시 로컬 공간 생성 완료: `{temp_dir}`")
        st.info("🔄 다운로드 시작")
        progress_bar = st.progress(0)

        try:
            answer_file_name = answer_file["name"]
            full_answer_path = f"{answer_path}/{answer_file_name}"
            local_answer_file_path = os.path.join(temp_dir, answer_file_name)

            st.write(f"📥 다운로드 중 (1/{len(submission_files) + 1}): `{answer_file_name}`")

            answer_file_data = client.storage.from_(bucket_name).download(full_answer_path)
            with open(local_answer_file_path, "wb") as f:
                f.write(answer_file_data)

            progress_bar.progress(1 / (len(submission_files) + 1))

        except Exception as e:
            st.error(f"❌ 정답 파일 다운로드 중 에러 발생: {str(e)}")
            return None

        # 파일 다운로드
        for idx, submission_file_info in enumerate(submission_files):
            try:
                submission_file_name = submission_file_info["name"]
                full_submission_path = f"{submission_path}/{submission_file_name}"
                local_submission_file_path = os.path.join(temp_dir, submission_file_name)

                st.write(f"📥 다운로드 중 ({idx + 2}/{len(submission_files) + 1}): `{submission_file_name}`")

                # Supabase에서 바이너리 다운로드 및 로컬 임시 파일로 저장
                submission_file_data = client.storage.from_(bucket_name).download(full_submission_path)
                with open(local_submission_file_path, "wb") as f:
                    f.write(submission_file_data)

                progress_bar.progress((idx + 2) / (len(submission_files) + 1))

            except Exception as e:
                st.error(f"❌ 제출 파일 다운로드 중 에러 발생: {str(e)}")
                return None

        st.success("✅ 파일 다운로드 완료!")

        return analyze_submissions(temp_dir)

def analyze_submissions(temp_dir):
    files = [f for f in os.listdir(temp_dir) if f.endswith('.nc')]
    answer_files = list()
    submission_files = list()

    for f in files:
        if f.startswith("test_") and f.endswith("_Y.nc"):
            answer_files.append(f)
        else: submission_files.append(f)
    if len(answer_files) == 0:
        st.error("정답 파일(.nc)을 찾을 수 없습니다.")
        return None
    if len(answer_files) > 1:
        st.error("정답 파일(.nc)은 오직 하나여야 합니다.")
        return None

    st.info("🔄 채점 시작")
    progress_bar = st.progress(0)

    try:
        answer_file_path = os.path.join(temp_dir, answer_files[0])
        answer, ans_time, ans_lat, ans_lon = load_nc(answer_file_path)
    except Exception as e:
        st.error(f"❌ 정답 파일을 불러올 수 없습니다: {e}")
        return None

    result = list()

    for idx, filename in enumerate(submission_files):
        try:
            full_file_path = os.path.join(temp_dir, filename)
            st.write(f"🔍 채점 중 ({idx + 1}/{len(submission_files)}): `{full_file_path}`")

            if not filename.startswith("pred_Y_") or not filename.endswith(".nc"):
                raise ValueError("파일명은 'pred_Y_팀명.nc' 형식이어야 합니다.")

            submission, sub_time, sub_lat, sub_lon = load_nc(full_file_path)
            mae, n_eval = calculate_mae(
                submission, answer,
                sub_time, ans_time, sub_lat, ans_lat, sub_lon, ans_lon,
            )
            l, m, r = st.columns(3)
            with l: st.metric("Name of team", filename[7:-3])
            with m: st.metric("MAE", f"{mae:.6f}")
            with r: st.metric("평가 격자 수", f"{n_eval:,}")

            result.append({
                "team_name": filename[7:-3],
                "score": round(mae, 6),
                "n_eval": n_eval
            })

            progress_bar.progress((idx + 1) / len(submission_files))

        except Exception as e:
            st.error(f"❌ 채점 중 오류 발생 ({filename}): {e}")
            return None

    st.success("✨ 채점이 완료되었습니다.")

    return result

def update_leaderboard(result):
    st.info("🔄 리더보드 업데이트 시작")
    progress_bar = st.progress(0)

    for idx, row in enumerate(result):
        st.write(f"📤 채점 결과 업데이트 중 ({idx + 1}/{len(result)}): {row["team_name"]} 팀")
        try:
            response = client.rpc(
                "upsert_leaderboard", {
                    "p_team_name": str(row["team_name"]),
                    "p_new_score": float(row["score"])
                }
            ).execute()
            progress_bar.progress((idx + 1) / len(result))
        except Exception as e:
            st.error(f"❌ DB 반영 중 오류 발생 ({row['team_name']}): {e}")
            return

    st.success("✨ 업데이트가 완료되었습니다.")

def load_nc(path: str | Path):
    with xr.open_dataset(path) as ds:
        if TARGET_VAR not in ds:
            raise ValueError(f"'{TARGET_VAR}' variable is missing.")
        da = ds[TARGET_VAR]
        missing_dims = [dim for dim in REQUIRED_DIMS if dim not in da.dims]
        if missing_dims:
            raise ValueError(f"Required dimension(s) missing: {', '.join(missing_dims)}")
        missing_coords = [dim for dim in REQUIRED_DIMS if dim not in ds.coords]
        if missing_coords:
            raise ValueError(f"Required coordinate(s) missing: {', '.join(missing_coords)}")
        da = da.transpose(*REQUIRED_DIMS)
        return (
            np.asarray(da.values, dtype=np.float64),
            np.asarray(ds["time"].values),
            np.asarray(ds["lat"].values),
            np.asarray(ds["lon"].values),
        )

def calculate_mae(submission, answer, sub_time, ans_time, sub_lat, ans_lat, sub_lon, ans_lon):
    if submission.shape != answer.shape:
        raise ValueError(f"Shape mismatch: submission={submission.shape}, expected={answer.shape}")
    if not np.array_equal(sub_time, ans_time):
        raise ValueError("Time coordinates do not match.")
    if not np.allclose(sub_lat, ans_lat):
        raise ValueError("Latitude coordinates do not match.")
    if not np.allclose(sub_lon, ans_lon):
        raise ValueError("Longitude coordinates do not match.")

    answer_nan = ~np.isfinite(answer)
    submission_nan = ~np.isfinite(submission)
    if not np.array_equal(answer_nan, submission_nan):
        raise ValueError("The missing-value mask has been modified.")

    valid = ~answer_nan
    if not valid.any():
        raise ValueError("The answer file contains no finite evaluation cells.")
    if (~np.isfinite(submission[valid])).any():
        raise ValueError("Evaluation cells contain NaN or infinite predictions.")

    return float(np.mean(np.abs(submission[valid] - answer[valid]))), int(valid.sum())