#!/usr/bin/env python3
"""
간단한 항공편 검색 도구
명령행 인수나 기본값으로 검색 조건을 설정할 수 있습니다.
"""
import json
import sys
import argparse
from datetime import datetime, timedelta
from fast_flights import FlightData, Passengers, get_flights

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

def parse_price(price_str):
    """가격 문자열에서 숫자 추출"""
    if not price_str or not isinstance(price_str, str):
        return float('inf')
    try:
        return int(price_str.replace('₩', '').replace(',', '').replace('원', ''))
    except ValueError:
        return float('inf')

def search_flights(params):
    """항공편 검색 실행"""
    print(f"=== {params['origin']} ↔ {params['destination']} 항공편 검색 ===")
    print(f"검색 조건:")
    print(f"  - 노선: {params['origin']} ↔ {params['destination']} (왕복)")
    print(f"  - 기간: {params['start_date']} ~ {params['end_date']}")
    print(f"  - 체류일: {params['min_stay_days']}~{params['max_stay_days']}일")
    print(f"  - 승객: 성인 {params['adults']}명, {params['seat_type']}석")
    
    try:
        # 날짜 범위 생성
        start_dt = datetime.strptime(params['start_date'], '%Y-%m-%d').date()
        end_dt = datetime.strptime(params['end_date'], '%Y-%m-%d').date()
        
        date_list = []
        current_date = start_dt
        while current_date <= end_dt:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        
        print(f"\n검색할 날짜: {len(date_list)}개")
        
        # 각 날짜 조합에 대해 검색
        results_data = []
        total_combinations = 0
        valid_combinations = 0
        error_count = 0
        
        for i, depart_date in enumerate(date_list):
            for j, return_date in enumerate(date_list[i:]):
                stay_duration = (return_date - depart_date).days
                total_combinations += 1
                
                # 체류일 조건 확인
                if params['min_stay_days'] <= stay_duration <= params['max_stay_days']:
                    valid_combinations += 1
                    
                    # 진행률 표시
                    if valid_combinations % 10 == 0:
                        print(f"진행률: {valid_combinations}개 조합 검색 중...")
                    
                    try:
                        flight_data = [
                            FlightData(date=depart_date.strftime('%Y-%m-%d'), 
                                      from_airport=params['origin'], 
                                      to_airport=params['destination']),
                            FlightData(date=return_date.strftime('%Y-%m-%d'), 
                                      from_airport=params['destination'], 
                                      to_airport=params['origin']),
                        ]
                        passengers_info = Passengers(adults=params['adults'])
                        
                        result = get_flights(
                            flight_data=flight_data,
                            trip="round-trip",
                            seat=params['seat_type'],
                            passengers=passengers_info,
                        )
                        
                        if result and result.flights:
                            # 최저가 항공편 찾기
                            cheapest_flight = min(result.flights, key=lambda f: parse_price(f.price))
                            
                            flight_dict = {
                                'departure_date': depart_date.strftime('%Y-%m-%d'),
                                'return_date': return_date.strftime('%Y-%m-%d'),
                                'stay_days': stay_duration,
                                'cheapest_flight': {
                                    'name': getattr(cheapest_flight, 'name', None),
                                    'departure': getattr(cheapest_flight, 'departure', None),
                                    'arrival': getattr(cheapest_flight, 'arrival', None),
                                    'duration': getattr(cheapest_flight, 'duration', None),
                                    'stops': getattr(cheapest_flight, 'stops', None),
                                    'price': getattr(cheapest_flight, 'price', None),
                                    'delay': getattr(cheapest_flight, 'delay', None),
                                    'is_best': getattr(cheapest_flight, 'is_best', None),
                                }
                            }
                            results_data.append(flight_dict)
                        else:
                            print(f"결과 없음: {depart_date} -> {return_date}")
                            
                    except Exception as e:
                        error_count += 1
                        print(f"오류: {depart_date} -> {return_date}: {type(e).__name__}")
                        if error_count <= 5:  # 처음 5개 오류만 상세 출력
                            print(f"  상세: {str(e)}")
        
        print(f"\n검색 완료!")
        print(f"총 조합: {total_combinations}개")
        print(f"유효 조합: {valid_combinations}개")
        print(f"검색 성공: {len(results_data)}개")
        print(f"오류 발생: {error_count}개")
        
        return results_data
        
    except Exception as e:
        print(f"[ERROR] 검색 중 오류 발생: {type(e).__name__}: {str(e)}")
        return []

def display_results(results_data, params):
    """결과 출력"""
    if not results_data:
        print("\n❌ 검색 결과가 없습니다.")
        return
    
    # 직항편만 필터링하고 가격이 있는 항공편만 유지
    valid_flights = []
    
    for option in results_data:
        flight = option['cheapest_flight']
        
        # 직항편(stops=0)이고 가격이 있는 항공편만 유지
        if flight['stops'] == 0 and flight['price'] and flight['price'] != "0" and flight['price'] != "":
            # 가격에서 숫자만 추출
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
                continue
    
    if not valid_flights:
        print("\n❌ 유효한 직항편이 없습니다.")
        return
    
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
    
    # 상위 5개 결과 출력
    print(f"\n=== {params['origin']} ↔ {params['destination']} 직항 최저가 상위 5개 ===")
    print("| 순위 | 출발일 | 복귀일 | 항공편 | 총요금 | 출발시간 | 도착시간 | 소요시간 |")
    print("| -- | --- | --- | --- | ---- | ---- | ---- | ---- |")
    
    for i, result in enumerate(unique_flights_list[:5], 1):
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
        
        print(f"| {i} | {result['departure_date']} | {result['return_date']} | {result['airline']} | {result['price']} | {departure_time_only} | {arrival_time_only} | {result['duration']} |")
    
    # 통계 정보
    price_range = [f['price_numeric'] for f in unique_flights_list]
    min_price = min(price_range)
    max_price = max(price_range)
    avg_price = sum(price_range) / len(price_range)
    
    print(f"\n### 통계 정보")
    print(f"- **총 조합 수**: {len(unique_flights_list)}개")
    print(f"- **최저가**: ₩{min_price:,}")
    print(f"- **최고가**: ₩{max_price:,}")
    print(f"- **평균가**: ₩{avg_price:,.0f}")
    
    # 항공사별 통계
    airlines = {}
    for result in unique_flights_list:
        airline = result['airline']
        if airline not in airlines:
            airlines[airline] = {'count': 0, 'min_price': float('inf')}
        airlines[airline]['count'] += 1
        airlines[airline]['min_price'] = min(airlines[airline]['min_price'], result['price_numeric'])
    
    print(f"\n### 항공사별 통계")
    for airline, stats in sorted(airlines.items(), key=lambda x: x[1]['min_price']):
        print(f"- **{airline}**: {stats['count']}개 조합, 최저가 ₩{stats['min_price']:,}")

def save_results(results_data, params):
    """결과를 JSON 파일로 저장"""
    if not results_data:
        return
    
    # 파일명 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{params['origin']}_{params['destination']}_flights_{timestamp}.json"
    
    # 결과 데이터 구성
    output_data = {
        'search_parameters': params,
        'cheapest_option_per_date_pair': results_data,
        'search_summary': {
            'total_combinations': len(results_data),
            'search_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    # 파일 저장
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 결과가 '{filename}' 파일에 저장되었습니다.")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='항공편 검색 도구')
    parser.add_argument('--origin', '-o', default='PUS', help='출발지 공항코드 (기본값: PUS)')
    parser.add_argument('--destination', '-d', default='KIX', help='도착지 공항코드 (기본값: KIX)')
    parser.add_argument('--start-date', '-s', help='검색 시작일 (YYYY-MM-DD)')
    parser.add_argument('--end-date', '-e', help='검색 종료일 (YYYY-MM-DD)')
    parser.add_argument('--min-stay', type=int, default=5, help='최소 체류일 (기본값: 5)')
    parser.add_argument('--max-stay', type=int, default=7, help='최대 체류일 (기본값: 7)')
    parser.add_argument('--adults', type=int, default=1, help='성인 승객 수 (기본값: 1)')
    parser.add_argument('--seat', default='economy', choices=['economy', 'business', 'first'], help='좌석 등급 (기본값: economy)')
    parser.add_argument('--save', action='store_true', help='결과를 JSON 파일로 저장')
    
    args = parser.parse_args()
    
    # 기본값 설정
    if not args.start_date:
        args.start_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    if not args.end_date:
        args.end_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    
    params = {
        'origin': args.origin.upper(),
        'destination': args.destination.upper(),
        'start_date': args.start_date,
        'end_date': args.end_date,
        'min_stay_days': args.min_stay,
        'max_stay_days': args.max_stay,
        'adults': args.adults,
        'seat_type': args.seat
    }
    
    try:
        # 항공편 검색
        results_data = search_flights(params)
        
        # 결과 출력
        display_results(results_data, params)
        
        # 결과 저장
        if args.save and results_data:
            save_results(results_data, params)
        
        print("\n✅ 검색 완료!")
        
    except KeyboardInterrupt:
        print("\n\n👋 검색이 취소되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
