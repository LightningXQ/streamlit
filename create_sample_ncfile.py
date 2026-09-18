import numpy as np
import xarray as xr

# 1. 가상의 데이터 생성 (경도, 위도, 시간, 기온)
lons = np.linspace(124, 132, 9)  # 경도 9개
lats = np.linspace(33, 43, 11)   # 위도 11개
times = xr.date_range("2026-01-01", "2026-01-05", freq="D")  # 시간 5일

# 3차원 무작위 기온 데이터 (시간 x 위도 x 경도)
temp_data = 15 + 5 * np.random.randn(len(times), len(lats), len(lons))

# 2. Xarray Dataset 생성
ds = xr.Dataset(
    data_vars={
        "temperature": (["time", "lat", "lon"], temp_data)
    },
    coords={
        "lon": lons,
        "lat": lats,
        "time": times
    }
)

# 3. 메타데이터(속성) 추가
ds.attrs["description"] = "간단한 기온 데이터 예제"
ds.temperature.attrs["units"] = "degC"

# 4. .nc 파일로 내보내기
ds.to_netcdf("sample_xarray_1.nc")
print("xarray를 이용한 nc 파일 생성 완료!")
