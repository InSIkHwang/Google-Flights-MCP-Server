#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from datetime import datetime, timedelta

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

def process_flight_data():
    # JSON 파일 읽기
    with open('pus_nrt_flights_2025_12_2026_01.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 검색 결과에서 왕복 항공편 데이터 추출
    cheapest_options = data['cheapest_option_per_date_pair']
    
    # 직항편만 필터링하고 가격이 있는 항공편만 유지
    valid_flights = []
    
    for option in cheapest_options:
        flight = option['cheapest_flight']
        
        # 직항편(stops=0)이고 가격이 있는 항공편만 유지
        if flight['stops'] == 0 and flight['price'] != "0" and flight['price'] != "":
            # 가격에서 숫자만 추출
            price_str = flight['price'].replace('₩', '').replace(',', '')
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
                continue
    
    # 가격순으로 정렬
    valid_flights.sort(key=lambda x: x['price_numeric'])
    
    # 상위 3개 결과
    top_3_results = valid_flights[:3]
    
    # 결과 출력
    print("=== 2025년 12월 ~ 2026년 1월 PUS ↔ NRT 직항 최저가 상위 3개 ===\n")
    
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
            'route': 'PUS ↔ NRT',
            'flight_type': '직항',
            'period': '2025-12-01 ~ 2026-01-31',
            'passengers': '성인 1명, 이코노미석',
            'total_combinations': len(valid_flights),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'top_3_results': top_3_results,
        'all_results': valid_flights[:10]  # 상위 10개만 저장
    }
    
    with open('flight_results.json', 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(valid_flights)}개의 직항 왕복 조합을 분석했습니다.")
    print("결과가 'flight_results.json' 파일에 저장되었습니다.")
    
    return top_3_results

if __name__ == "__main__":
    process_flight_data()
