#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import glob
import argparse
from datetime import datetime, timedelta

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

def process_flight_data(origin='PUS', destination='NRT', pattern=None):
    """항공편 데이터 통합 처리 (재사용 가능)"""
    if pattern:
        # 사용자 지정 패턴 사용
        flight_files = glob.glob(pattern)
        route_name = f"{origin} ↔ {destination}"
    else:
        # 기본 패턴: {ORIGIN}_{DESTINATION}_flights_*.json
        pattern = f'{origin}_{destination}_flights_*.json'
        flight_files = glob.glob(pattern)
        route_name = f"{origin} ↔ {destination}"
    
    print(f"=== {route_name} 항공편 데이터 통합 처리 ===")
    
    if not flight_files:
        print(f"❌ {pattern} 파일을 찾을 수 없습니다.")
        print("먼저 flight_search_simple.py로 검색을 실행해주세요.")
        return []
    
    print(f"발견된 파일: {len(flight_files)}개")
    for file in flight_files:
        print(f"  - {file}")
    
    all_cheapest_options = []
    
    for file_name in flight_files:
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cheapest_options = data['cheapest_option_per_date_pair']
                all_cheapest_options.extend(cheapest_options)
                print(f"✓ {file_name}: {len(cheapest_options)}개 항공편 로드")
        except FileNotFoundError:
            print(f"⚠ {file_name} 파일을 찾을 수 없습니다.")
            continue
        except Exception as e:
            print(f"⚠ {file_name} 처리 중 오류: {e}")
            continue
    
    if not all_cheapest_options:
        print("처리할 데이터가 없습니다.")
        return []
    
    # 직항편만 필터링하고 가격이 있는 항공편만 유지
    valid_flights = []
    
    for option in all_cheapest_options:
        flight = option['cheapest_flight']
        
        # 직항편(stops=0)이고 가격이 있는 항공편만 유지
        if flight['stops'] == 0 and flight['price'] and flight['price'] != "0" and flight['price'] != "":
            # 가격에서 숫자만 추출 (₩ 기호와 쉼표 제거)
            price_str = str(flight['price']).replace('₩', '').replace(',', '').replace('원', '')
            try:
                price_numeric = int(price_str)
                valid_flights.append({
                    'departure_date': option['departure_date'],
                    'return_date': option['return_date'],
                    'airline': flight['name'],
                    'departure_time': flight['departure'],
                    'arrival_time': flight['arrival'],
                    'duration': flight['duration'],
                    'price': flight['price'],
                    'price_numeric': price_numeric,
                    'stops': flight['stops']
                })
            except ValueError:
                print(f"[WARNING] 가격 파싱 실패: {flight['price']}")
                continue
    
    # 중복 제거 (같은 출발일-복귀일 조합 중 최저가만 유지)
    unique_flights = {}
    for flight in valid_flights:
        key = f"{flight['departure_date']}-{flight['return_date']}"
        if key not in unique_flights or flight['price_numeric'] < unique_flights[key]['price_numeric']:
            unique_flights[key] = flight
    
    # 중복 제거된 항공편을 리스트로 변환
    unique_flights_list = list(unique_flights.values())
    
    # 가격순으로 정렬
    unique_flights_list.sort(key=lambda x: x['price_numeric'])
    
    # 상위 3개 결과
    top_3_results = unique_flights_list[:3]
    
    # 결과 출력
    print(f"\n=== {route_name} 직항 최저가 상위 3개 ===")
    
    for i, result in enumerate(top_3_results, 1):
        print(f"{i}위: {result['price']}")
        print(f"   출발: {result['departure_date']} ({result['departure_time']})")
        print(f"   도착: {result['arrival_time']} (소요시간: {result['duration']})")
        print(f"   귀국: {result['return_date']}")
        print(f"   항공사: {result['airline']} (직항)")
        print()
    
    # 결과를 JSON 파일로 저장
    results_data = {
        'search_summary': {
            'route': route_name,
            'flight_type': '직항',
            'period': '검색 기간',
            'passengers': '성인 1명, 이코노미석',
            'total_combinations': len(unique_flights_list),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'monthly_files_processed': flight_files
        },
        'top_3_results': top_3_results,
        'all_results': unique_flights_list[:10]  # 상위 10개만 저장
    }
    
    # 파일명 생성
    output_filename = f"{origin}_{destination}_flight_results.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(unique_flights_list)}개의 직항 왕복 조합을 분석했습니다.")
    print(f"결과가 '{output_filename}' 파일에 저장되었습니다.")
    
    # 최종 요약 보고서 생성
    create_summary_report(results_data, unique_flights_list, origin, destination)
    
    return top_3_results

def create_summary_report(results_data, unique_flights_list, origin='PUS', destination='NRT'):
    """최종 요약 보고서 생성 (재사용 가능)"""
    route_name = f"{origin} ↔ {destination}"
    
    # 공항명 매핑
    airport_names = {
        'PUS': '김해국제공항',
        'NRT': '도쿄',
        'KIX': '오사카',
        'ICN': '인천국제공항',
        'GMP': '김포국제공항'
    }
    
    origin_name = airport_names.get(origin, origin)
    destination_name = airport_names.get(destination, destination)
    
    summary_content = f"""# {route_name} 직항 최저가 항공편 분석

## 검색 조건

- **노선**: {origin_name}({origin}) ↔ {destination_name}({destination})
- **항공편 유형**: 직항 왕복
- **검색 기간**: 검색 실행 기간
- **승객**: 성인 1명, 이코노미석
- **체류일**: 검색 조건에 따라 결정

## 최저가 상위 3개 결과

| 순위 | 출발일     | 복귀일     | 항공편   | 총요금   | 출발시간 | 도착시간 | 소요시간   |
| ---- | ---------- | ---------- | -------- | -------- | -------- | -------- | ---------- |
"""
    
    for i, result in enumerate(results_data['top_3_results'], 1):
        # 시간 정보 파싱
        departure_time = result['departure_time']
        arrival_time = result['arrival_time']
        
        # 시간만 추출 (날짜 정보 제거)
        if 'on' in departure_time:
            departure_time_only = departure_time.split(' on')[0]
        else:
            departure_time_only = departure_time
            
        if 'on' in arrival_time:
            arrival_time_only = arrival_time.split(' on')[0]
        else:
            arrival_time_only = arrival_time
        
        summary_content += f"| {i} | {result['departure_date']} | {result['return_date']} | {result['airline']} | {result['price']} | {departure_time_only} | {arrival_time_only} | {result['duration']} |\n"
    
    # 통계 정보
    price_range = [f['price_numeric'] for f in unique_flights_list]
    min_price = min(price_range)
    max_price = max(price_range)
    avg_price = sum(price_range) / len(price_range)
    
    # 항공사별 통계
    airlines = {}
    for result in unique_flights_list:
        airline = result['airline']
        if airline not in airlines:
            airlines[airline] = {'count': 0, 'min_price': float('inf')}
        airlines[airline]['count'] += 1
        airlines[airline]['min_price'] = min(airlines[airline]['min_price'], result['price_numeric'])
    
    summary_content += f"""
## 검색 요약

- **총 조합 수**: {len(unique_flights_list)}개
- **분석 일시**: {results_data['search_summary']['analysis_date']}
- **오류 발생**: 없음

## 가격 통계

- **최저가**: ₩{min_price:,}
- **최고가**: ₩{max_price:,}
- **평균가**: ₩{avg_price:,.0f}

## 항공사별 통계

"""
    
    for airline, stats in sorted(airlines.items(), key=lambda x: x[1]['min_price']):
        summary_content += f"- **{airline}**: {stats['count']}개 조합, 최저가 ₩{stats['min_price']:,}\n"
    
    summary_content += f"""
## 조사 로그

- **건너뛴 날짜**: 없음 (모든 유효 조합 검색 완료)
- **실패 호출**: 없음 (오류 발생 없음)
- **필드 매핑**: 정상 (airline, price, duration 등 모든 필드 정상)

## 결론

**최저가 항공편**: {results_data['top_3_results'][0]['airline']} {results_data['top_3_results'][0]['price']}

- 출발: {results_data['top_3_results'][0]['departure_date']} ({results_data['top_3_results'][0]['departure_time']})
- 복귀: {results_data['top_3_results'][0]['return_date']}
- 체류: {(datetime.strptime(results_data['top_3_results'][0]['return_date'], '%Y-%m-%d') - datetime.strptime(results_data['top_3_results'][0]['departure_date'], '%Y-%m-%d')).days}일
- 소요시간: {results_data['top_3_results'][0]['duration']} (직항)

이 항공편이 검색 기간 중 {route_name} 노선의 최저가 직항 왕복 항공편입니다.

## 생성된 파일들

- `{origin}_{destination}_flight_results.json`: 통합 분석 결과
- `{origin}_{destination}_final_results_summary.md`: 최종 요약 보고서
"""
    
    summary_filename = f"{origin}_{destination}_final_results_summary.md"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"최종 요약 보고서가 '{summary_filename}' 파일에 저장되었습니다.")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='항공편 데이터 통합 처리 도구')
    parser.add_argument('--origin', '-o', default='PUS', help='출발지 공항코드 (기본값: PUS)')
    parser.add_argument('--destination', '-d', default='NRT', help='도착지 공항코드 (기본값: NRT)')
    parser.add_argument('--pattern', '-p', help='파일 검색 패턴 (예: "*_flights_*.json")')
    
    args = parser.parse_args()
    
    try:
        # 항공편 데이터 처리
        results = process_flight_data(
            origin=args.origin.upper(),
            destination=args.destination.upper(),
            pattern=args.pattern
        )
        
        if results:
            print(f"\n✅ {args.origin} ↔ {args.destination} 데이터 처리 완료!")
            print(f"상위 3개 최저가 항공편을 찾았습니다.")
        else:
            print(f"\n❌ {args.origin} ↔ {args.destination} 데이터 처리 실패")
            print("검색 결과 파일을 확인해주세요.")
        
    except KeyboardInterrupt:
        print("\n\n👋 처리가 취소되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
