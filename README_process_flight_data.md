# 항공편 데이터 통합 처리 도구 사용법

## 개요

`flight_search_simple.py`로 생성된 JSON 파일들을 통합하여 분석하고 최종 요약 보고서를 생성하는 도구입니다.

## 파일 설명

- `process_flight_data_universal.py`: 범용 항공편 데이터 통합 처리 도구

## 사용법

### 1. 기본 사용법

```bash
# 기본값으로 PUS ↔ NRT 데이터 처리
python process_flight_data_universal.py

# 특정 노선 데이터 처리
python process_flight_data_universal.py --origin PUS --destination KIX

# 사용자 지정 파일 패턴으로 처리
python process_flight_data_universal.py --pattern "*_flights_*.json"
```

### 2. 명령행 옵션

| 옵션            | 단축형 | 기본값 | 설명                                    |
| --------------- | ------ | ------ | --------------------------------------- |
| `--origin`      | `-o`   | PUS    | 출발지 공항코드                         |
| `--destination` | `-d`   | NRT    | 도착지 공항코드                         |
| `--pattern`     | `-p`   | -      | 파일 검색 패턴 (예: "_*flights*_.json") |

### 3. 사용 예시

```bash
# PUS → KIX 데이터 처리
python process_flight_data_universal.py -o PUS -d KIX

# ICN → NRT 데이터 처리
python process_flight_data_universal.py -o ICN -d NRT

# 모든 항공편 파일 통합 처리
python process_flight_data_universal.py --pattern "*_flights_*.json"

# 특정 날짜 범위 파일만 처리
python process_flight_data_universal.py --pattern "PUS_KIX_flights_2025*"
```

## 입력 파일 형식

도구는 `flight_search_simple.py`로 생성된 JSON 파일을 읽습니다:

```json
{
  "search_parameters": {
    "origin": "PUS",
    "destination": "KIX",
    "start_date": "2025-10-17",
    "end_date": "2025-10-20",
    "min_stay_days": 1,
    "max_stay_days": 2,
    "adults": 1,
    "seat_type": "economy"
  },
  "cheapest_option_per_date_pair": [
    {
      "departure_date": "2025-10-17",
      "return_date": "2025-10-19",
      "stay_days": 2,
      "cheapest_flight": {
        "name": "Jeju Air",
        "departure": "4:45 PM on Fri, Oct 17",
        "arrival": "6:10 PM on Fri, Oct 17",
        "duration": "1 hr 25 min",
        "stops": 0,
        "price": "₩287100"
      }
    }
  ]
}
```

## 출력 결과

### 1. 콘솔 출력

- 발견된 파일 목록
- 로드된 항공편 수
- 상위 3개 최저가 항공편 정보
- 통계 정보

### 2. 생성되는 파일

#### JSON 결과 파일

- `{출발지}_{도착지}_flight_results.json`: 통합 분석 결과
- 예: `PUS_KIX_flight_results.json`

#### 마크다운 요약 보고서

- `{출발지}_{도착지}_final_results_summary.md`: 최종 요약 보고서
- 예: `PUS_KIX_final_results_summary.md`

## 처리 과정

1. **파일 검색**: 지정된 패턴으로 JSON 파일들을 찾습니다
2. **데이터 로드**: 각 파일에서 항공편 데이터를 읽어옵니다
3. **필터링**: 직항편(stops=0)이고 가격이 있는 항공편만 유지합니다
4. **중복 제거**: 같은 출발일-복귀일 조합 중 최저가만 유지합니다
5. **정렬**: 가격순으로 정렬하여 상위 3개를 선택합니다
6. **통계 계산**: 가격 범위, 평균가, 항공사별 통계를 계산합니다
7. **결과 저장**: JSON과 마크다운 파일로 결과를 저장합니다

## 주의사항

1. **파일 형식**: `flight_search_simple.py`로 생성된 JSON 파일만 처리할 수 있습니다
2. **파일명 규칙**: `{출발지}_{도착지}_flights_*.json` 형식을 따릅니다
3. **데이터 무결성**: 가격 정보가 없는 항공편은 제외됩니다
4. **중복 처리**: 같은 날짜 조합의 항공편은 최저가만 유지됩니다

## 문제 해결

### 파일을 찾을 수 없는 경우

- `flight_search_simple.py`로 먼저 검색을 실행했는지 확인하세요
- 파일명이 올바른 형식인지 확인하세요
- `--pattern` 옵션으로 다른 패턴을 시도해보세요

### 데이터가 없는 경우

- JSON 파일에 유효한 항공편 데이터가 있는지 확인하세요
- 직항편(stops=0)이고 가격이 있는 항공편만 처리됩니다

### 오류가 발생하는 경우

- JSON 파일 형식이 올바른지 확인하세요
- 파일이 손상되지 않았는지 확인하세요
- 충분한 디스크 공간이 있는지 확인하세요

## 통합 워크플로우

```bash
# 1. 항공편 검색
python flight_search_simple.py --origin PUS --destination KIX --save

# 2. 데이터 통합 처리
python process_flight_data_universal.py --origin PUS --destination KIX

# 3. 결과 확인
cat PUS_KIX_final_results_summary.md
```

## 확장 가능성

이 도구는 다음과 같이 확장할 수 있습니다:

- **다중 노선 처리**: 여러 노선의 데이터를 한 번에 처리
- **시간대별 분석**: 출발 시간대별 최저가 분석
- **항공사별 분석**: 항공사별 가격 트렌드 분석
- **날짜별 분석**: 특정 날짜의 가격 변동 분석
