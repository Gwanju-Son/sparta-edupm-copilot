#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 문서를 읽어서 지식 그래프를 생성하고 JSON으로 저장하는 스크립트
"""

import requests
from bs4 import BeautifulSoup
import json
import google.generativeai as genai
import re
import time
from typing import Dict, List, Any


class WebToKnowledgeGraph:
    def __init__(self, api_key: str):
        """
        지식 그래프 생성기 초기화
        
        Args:
            api_key (str): Google Gemini API 키
        """
        # Google Gemini API 설정
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def fetch_web_content(self, url: str) -> str:
        """
        웹 페이지의 HTML 콘텐츠를 가져옵니다.
        
        Args:
            url (str): 대상 웹 페이지 URL
            
        Returns:
            str: HTML 콘텐츠
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            raise Exception(f"웹 페이지를 가져오는 중 오류 발생: {e}")
    
    def extract_plot_section(self, html_content: str) -> str:
        """
        HTML에서 플롯/스토리 섹션을 추출합니다.
        
        Args:
            html_content (str): HTML 콘텐츠
            
        Returns:
            str: 스토리 텍스트
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Plot 섹션 찾기 (여러 가능한 ID와 헤더 시도)
        plot_indicators = ['Plot', 'Story', 'Synopsis', 'plot', 'story', 'synopsis']
        plot_text = ""
        
        for indicator in plot_indicators:
            # span id로 찾기
            plot_span = soup.find('span', {'id': indicator})
            if plot_span:
                # 헤더 다음의 모든 문단 수집
                header = plot_span.find_parent(['h2', 'h3', 'h4'])
                if header:
                    current = header.find_next_sibling()
                    while current and current.name in ['p', 'div']:
                        if current.name == 'p':
                            plot_text += current.get_text().strip() + " "
                        elif current.name == 'div' and 'mw-parser-output' not in current.get('class', []):
                            paragraphs = current.find_all('p')
                            for p in paragraphs:
                                plot_text += p.get_text().strip() + " "
                        
                        current = current.find_next_sibling()
                        # 다음 섹션 헤더를 만나면 중단
                        if current and current.name in ['h2', 'h3', 'h4']:
                            break
                    
                    if plot_text.strip():
                        break
        
        if not plot_text.strip():
            # 대안: 모든 문단에서 스토리 관련 내용 찾기
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 100 and any(keyword in text.lower() for keyword in ['story', 'plot', 'narrative', 'tanjiro', 'demon']):
                    plot_text += text + " "
        
        # 텍스트 정리
        plot_text = re.sub(r'\[.*?\]', '', plot_text)  # 위키피디아 참조 제거
        plot_text = re.sub(r'\s+', ' ', plot_text)     # 다중 공백 정리
        
        return plot_text.strip()
    
    def generate_knowledge_graph(self, story_text: str) -> Dict[str, Any]:
        """
        스토리 텍스트로부터 지식 그래프를 생성합니다.
        
        Args:
            story_text (str): 스토리 텍스트
            
        Returns:
            Dict[str, Any]: 지식 그래프 JSON 구조
        """
        prompt = f"""
다음 귀멸의 칼날 무한열차편 스토리를 기반으로 구조화된 지식 그래프를 생성해 주세요.

스토리 내용:
{story_text}

다음 JSON 형태로 지식 그래프를 구성해 주세요:

{{
    "title": "귀멸의 칼날: 무한열차편",
    "entities": [
        {{
            "id": "entity_id",
            "name": "엔티티 이름",
            "type": "인물|장소|사물|개념",
            "description": "엔티티에 대한 설명",
            "attributes": {{
                "attribute_name": "attribute_value"
            }}
        }}
    ],
    "relationships": [
        {{
            "source": "source_entity_id",
            "target": "target_entity_id",
            "relationship": "관계 유형",
            "description": "관계에 대한 설명"
        }}
    ],
    "events": [
        {{
            "id": "event_id",
            "name": "사건 이름",
            "description": "사건 설명",
            "participants": ["참여자_entity_id들"],
            "location": "장소_entity_id",
            "sequence": 순서번호
        }}
    ]
}}

주요 포함 요소:
- 주요 인물들 (탄지로, 이노스케, 젠이츠, 렌고쿠, 엔무 등)
- 장소 (무한열차, 꿈의 세계 등)
- 주요 사건들 (꿈에 빠짐, 전투, 희생 등)
- 인물간의 관계
- 사건들의 시간적 순서

모든 내용을 한글로 작성해 주세요. JSON 형식을 정확히 지켜서 응답해 주세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            # JSON 파싱 시도
            response_text = response.text.strip()
            
            # 코드 블록 마커 제거
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # JSON 파싱
            knowledge_graph = json.loads(response_text)
            return knowledge_graph
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            print(f"응답 내용: {response.text}")
            
            # 대안: 텍스트 응답을 기본 구조로 래핑
            return {
                "title": "귀멸의 칼날: 무한열차편",
                "raw_response": response.text,
                "entities": [],
                "relationships": [],
                "events": [],
                "error": "JSON 파싱 실패 - 원본 응답을 raw_response에 저장"
            }
        
        except Exception as e:
            raise Exception(f"지식 그래프 생성 중 오류 발생: {e}")
    
    def save_to_json(self, knowledge_graph: Dict[str, Any], filename: str = "knowledge_graph.json"):
        """
        지식 그래프를 JSON 파일로 저장합니다.
        
        Args:
            knowledge_graph (Dict[str, Any]): 지식 그래프 데이터
            filename (str): 저장할 파일명
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)
            print(f"지식 그래프가 '{filename}' 파일로 저장되었습니다.")
        except Exception as e:
            raise Exception(f"JSON 파일 저장 중 오류 발생: {e}")
    
    def process_url_to_knowledge_graph(self, url: str, output_filename: str = "knowledge_graph.json") -> Dict[str, Any]:
        """
        URL에서 웹 문서를 읽어 지식 그래프를 생성하고 저장하는 전체 프로세스
        
        Args:
            url (str): 대상 웹 페이지 URL
            output_filename (str): 출력 파일명
            
        Returns:
            Dict[str, Any]: 생성된 지식 그래프
        """
        print("웹 페이지 내용을 가져오는 중...")
        html_content = self.fetch_web_content(url)
        
        print("스토리 섹션을 추출하는 중...")
        story_text = self.extract_plot_section(html_content)
        
        if not story_text:
            raise Exception("스토리 섹션을 찾을 수 없습니다.")
        
        print(f"추출된 스토리 길이: {len(story_text)} 문자")
        print(f"스토리 미리보기: {story_text[:200]}...")
        
        print("지식 그래프를 생성하는 중...")
        knowledge_graph = self.generate_knowledge_graph(story_text)
        
        print("JSON 파일로 저장하는 중...")
        self.save_to_json(knowledge_graph, output_filename)
        
        return knowledge_graph


def main():
    """메인 실행 함수"""
    # 설정
    API_KEY = "AIzaSyC4zrhudXJO7DggAHTpivSHTF6f0dnaKww"
    # 고정 실행 상수
    TARGET_URL = "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_the_Movie:_Mugen_Train"
    JSON_OUTPUT = "demon_slayer_knowledge_graph.json"
    
    # 여러 가능한 URL들을 시도
    POSSIBLE_URLS = [
        "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_the_Movie:_Mugen_Train",
        "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_%E2%80%93_The_Movie:_Mugen_Train",
        "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_–_The_Movie:_Mugen_Train", 
        "https://en.wikipedia.org/wiki/Demon_Slayer:_Kimetsu_no_Yaiba_The_Movie:_Mugen_Train",
        "https://en.wikipedia.org/wiki/Demon_Slayer_Kimetsu_no_Yaiba_The_Movie_Mugen_Train"
    ]
    
    try:
        # 지식 그래프 생성기 초기화
        kg_generator = WebToKnowledgeGraph(API_KEY)
        
        # 여러 URL을 시도하여 작동하는 것 찾기
        print("=== 귀멸의 칼날 무한열차편 지식 그래프 생성 시작 ===")
        
        knowledge_graph = None
        working_url = None

        candidate_urls = [TARGET_URL] if TARGET_URL else POSSIBLE_URLS
        for url in candidate_urls:
            if not url:
                continue
            try:
                print(f"URL 시도 중: {url}")
                # 1) URL에서 스토리 추출 → 2) LLM 그래프 생성 → 3) JSON 저장
                knowledge_graph = kg_generator.process_url_to_knowledge_graph(url, JSON_OUTPUT)
                working_url = url
                break
            except Exception as e:
                print(f"URL {url} 실패: {e}")
                continue
        
        if not knowledge_graph:
            raise Exception("모든 URL이 실패했습니다.")
        
        print(f"성공한 URL: {working_url}")
        print("\n=== 생성 완료 ===")
        print(f"JSON 저장 완료: {JSON_OUTPUT}")
        print(f"엔티티 수: {len(knowledge_graph.get('entities', []))}")
        print(f"관계 수: {len(knowledge_graph.get('relationships', []))}")
        print(f"사건 수: {len(knowledge_graph.get('events', []))}")
        
        # 간단한 통계 출력
        if 'entities' in knowledge_graph:
            entity_types = {}
            for entity in knowledge_graph['entities']:
                entity_type = entity.get('type', '기타')
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            print("\n엔티티 유형별 통계:")
            for entity_type, count in entity_types.items():
                print(f"  {entity_type}: {count}개")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
