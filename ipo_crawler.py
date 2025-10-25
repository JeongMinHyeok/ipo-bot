"""
피너츠 공모주 정보 크롤러

https://www.finuts.co.kr 공모주 API를 사용하여 특정 날짜의 공모주 정보를 수집합니다.
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime


class FinutsIPOCrawler:
    """피너츠 공모주 API 크롤러"""
    
    def __init__(self):
        self.api_url = "https://www.finuts.co.kr/html/task/ipo/ipoListQuery.php"
        self.base_url = "https://www.finuts.co.kr/html/ipo/ipoList.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.base_url,
            'Origin': 'https://www.finuts.co.kr'
        }
        self.data_cache = None
    
    def fetch_all_ipo_data(self) -> Optional[List[Dict]]:
        """
        모든 공모주 데이터를 API로부터 가져옵니다.
        
        Returns:
            공모주 데이터 리스트 또는 None (실패 시)
        """
        try:
            response = requests.post(
                self.api_url,
                data={},
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    self.data_cache = data['data']
                    return self.data_cache
            return None
            
        except Exception as e:
            print(f"❌ 데이터 가져오기 실패: {e}")
            return None
    
    def get_ipo_by_date(self, target_date: str, date_type: str = 'all') -> List[Dict]:
        """
        특정 날짜의 공모주 정보를 가져옵니다.
        
        Args:
            target_date: 검색할 날짜 (YYYY-MM-DD 형식)
            date_type: 날짜 유형
                - 'all': 모든 날짜 필드 검색 (기본값)
                - 'subscription_start': 청약 시작일 (BGNG_YMD)
                - 'subscription_end': 청약 종료일 (END_YMD)
                - 'listing': 상장일 (IPO_DATE)
        
        Returns:
            매칭되는 공모주 정보 리스트
        """
        if self.data_cache is None:
            data = self.fetch_all_ipo_data()
            if not data:
                return []
        else:
            data = self.data_cache
        
        matched = []
        for item in data:
            if date_type == 'subscription_start':
                if item.get('BGNG_YMD') == target_date:
                    matched.append(item)
            elif date_type == 'subscription_end':
                if item.get('END_YMD') == target_date:
                    matched.append(item)
            elif date_type == 'listing':
                if item.get('IPO_DATE') == target_date:
                    matched.append(item)
            else:  # 'all'
                if any(target_date in str(value) for value in item.values()):
                    matched.append(item)
        
        return matched
    
    def get_ipo_by_date_and_status(self, target_date: str) -> Dict[str, List[Dict]]:
        """
        특정 날짜의 공모주 정보를 상태별로 분류하여 가져옵니다.
        
        Args:
            target_date: 검색할 날짜 (YYYY-MM-DD 형식)
        
        Returns:
            상태별로 분류된 공모주 정보 딕셔너리
            {'subscription': [...], 'listing': [...]}
        """
        if self.data_cache is None:
            data = self.fetch_all_ipo_data()
            if not data:
                return {'subscription': [], 'listing': []}
        else:
            data = self.data_cache
        
        result = {
            'subscription': [],
            'listing': []
        }
        
        for item in data:
            bgng_ymd = item.get('BGNG_YMD', '')
            end_ymd = item.get('END_YMD', '')
            schdl_se_cd = item.get('SCHDL_SE_CD', '')
            
            # 청약 상태 (S) - 청약 시작일 또는 종료일이 target_date인 경우
            if schdl_se_cd == 'S' and (bgng_ymd == target_date or end_ymd == target_date):
                result['subscription'].append(item)
            # 상장 상태 (L) - BGNG_YMD가 target_date인 경우
            elif schdl_se_cd == 'L' and bgng_ymd == target_date:
                result['listing'].append(item)
        
        return result
    
    def format_ipo_info(self, ipo: Dict) -> str:
        """
        공모주 정보를 읽기 쉬운 형식으로 포맷합니다.
        
        Args:
            ipo: 공모주 데이터 딕셔너리
        
        Returns:
            포맷된 문자열
        """
        name = ipo.get('ENT_NM', 'N/A')
        
        # 공모가 범위
        band_start = ipo.get('BAND_BGNG_AMT', '0')
        band_end = ipo.get('BAND_END_AMT', '0')
        if band_start and band_end and band_start != '0' and band_end != '0':
            price_range = f"{int(band_start):,}~{int(band_end):,}원"
        else:
            price_range = "미정"
        
        # 주간사
        underwriter = ipo.get('INDCT_JUGANSA_NM', 'N/A')
        
        # 날짜 정보
        sub_start = ipo.get('BGNG_YMD', 'N/A')
        sub_end = ipo.get('END_YMD', 'N/A')
        listing_date = ipo.get('IPO_DATE', 'N/A')
        
        # 공모금액
        pss_amt = ipo.get('PSS_AMT', '0')
        if pss_amt and pss_amt != '0':
            pss_amt_formatted = f"{int(pss_amt)/100000000:.0f}억원"
        else:
            pss_amt_formatted = "N/A"
        
        info = f"""
종목명: {name}
공모가 범위: {price_range}
주간사: {underwriter}
청약 기간: {sub_start} ~ {sub_end}
상장 예정일: {listing_date}
공모금액: {pss_amt_formatted}
""".strip()
        
        return info
    
    def format_ipo_simple(self, ipo: Dict, include_schedule: bool = False) -> str:
        """
        공모주 정보를 간단한 형식으로 포맷합니다.
        
        Args:
            ipo: 공모주 데이터 딕셔너리
            include_schedule: 청약 일정 포함 여부
        
        Returns:
            포맷된 문자열
        """
        ent_nm = ipo.get('ENT_NM', 'N/A')
        ipo_sn = ipo.get('IPO_SN', 'N/A')
        pss_prc = ipo.get('PSS_PRC', '')
        indct_jugansa_nm = ipo.get('INDCT_JUGANSA_NM', 'N/A')
        pss_amt = ipo.get('PSS_AMT', '0')
        
        # 공모가
        if pss_prc and pss_prc != '':
            pss_prc_formatted = f"{int(pss_prc):,}원"
        else:
            pss_prc_formatted = "미정"
        
        # 공모금액 (억원 단위)
        if pss_amt and pss_amt != '0':
            pss_amt_formatted = f"{int(pss_amt)/100000000:.0f}억원"
        else:
            pss_amt_formatted = "미정"
        
        info = f"""- {ent_nm} ({ipo_sn})
  공모가: {pss_prc_formatted}"""
        
        # 청약 일정 추가
        if include_schedule:
            bgng_ymd = ipo.get('BGNG_YMD', 'N/A')
            end_ymd = ipo.get('END_YMD', 'N/A')
            info += f"\n  청약일정: {bgng_ymd} ~ {end_ymd}"
        
        info += f"""
  주간사: {indct_jugansa_nm}
  공모금액: {pss_amt_formatted}"""
        
        return info
    
    def get_ipo_message(self, target_date: str) -> str:
        """
        특정 날짜의 공모주 정보를 Discord 메시지 형식으로 반환합니다.
        
        Args:
            target_date: 검색할 날짜 (YYYY-MM-DD 형식)
        
        Returns:
            Discord 메시지용 문자열
        """
        data = self.get_ipo_by_date_and_status(target_date)
        
        subscription_list = data['subscription']
        listing_list = data['listing']
        
        # 데이터가 하나도 없으면
        if not subscription_list and not listing_list:
            return f'**{target_date}**\n\nData not found'
        
        message = f'**{target_date}**\n\n'
        
        # 청약 (청약 일정 포함)
        if subscription_list:
            message += "**[청약]**\n"
            for ipo in subscription_list:
                message += self.format_ipo_simple(ipo, include_schedule=True) + "\n"
            message += "\n"
        
        # 상장 (청약 일정 미포함)
        if listing_list:
            message += "**[상장]**\n"
            for ipo in listing_list:
                message += self.format_ipo_simple(ipo, include_schedule=False) + "\n"
            message += "\n"
        
        return message.strip()

    def print_ipo_by_status(self, target_date: str):
        """
        특정 날짜의 공모주를 상태별로 출력합니다.
        
        Args:
            target_date: 검색할 날짜 (YYYY-MM-DD 형식)
        """
        data = self.get_ipo_by_date_and_status(target_date)
        
        subscription_list = data['subscription']
        listing_list = data['listing']
        
        # 데이터가 하나도 없으면
        if not subscription_list and not listing_list:
            print(f'"{target_date}"\n\nData not found')
            return
        
        print(f'"{target_date}"\n')
        
        # 청약 (청약 일정 포함)
        if subscription_list:
            print("[청약]")
            for ipo in subscription_list:
                print(self.format_ipo_simple(ipo, include_schedule=True))
            print()
        
        # 상장 (청약 일정 미포함)
        if listing_list:
            print("[상장]")
            for ipo in listing_list:
                print(self.format_ipo_simple(ipo, include_schedule=False))
            print()
    
    def print_ipo_list(self, ipo_list: List[Dict], title: str = "공모주 정보"):
        """
        공모주 리스트를 예쁘게 출력합니다.
        
        Args:
            ipo_list: 공모주 데이터 리스트
            title: 출력 타이틀
        """
        print("\n" + "="*80)
        print(f"{title} ({len(ipo_list)}개)")
        print("="*80)
        
        if not ipo_list:
            print("⚠️ 해당하는 공모주가 없습니다.")
            return
        
        for idx, ipo in enumerate(ipo_list, 1):
            print(f"\n[{idx}] {self.format_ipo_info(ipo)}")
        
        print("\n" + "="*80)
    
    def save_to_json(self, ipo_list: List[Dict], filename: str):
        """
        공모주 데이터를 JSON 파일로 저장합니다.
        
        Args:
            ipo_list: 공모주 데이터 리스트
            filename: 저장할 파일명
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(ipo_list, f, ensure_ascii=False, indent=2)
            print(f"\n✅ {len(ipo_list)}개의 공모주 정보를 '{filename}'에 저장했습니다.")
        except Exception as e:
            print(f"\n❌ 파일 저장 실패: {e}")


def main():
    """메인 실행 함수"""
    print("="*80)
    print("피너츠 공모주 크롤러")
    print("="*80 + "\n")
    
    # 크롤러 생성
    crawler = FinutsIPOCrawler()
    
    # 특정 날짜의 공모주 조회
    target_date = "2025-10-28"
    
    # 새로운 포맷으로 출력
    crawler.print_ipo_by_status(target_date)


if __name__ == "__main__":
    main()