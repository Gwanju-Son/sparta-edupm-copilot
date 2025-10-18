#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 프로필 텍스트 파일을 읽어서 지식 그래프를 생성하고 JSON으로 저장하는 스크립트
"""

import json
import google.generativeai as genai
import re
from typing import Dict, Any
import os

class ProfileToKnowledgeGraph:
    def __init__(self, api_key: str):
        """
        지식 그래프 생성기 초기화
        
        Args:
            api_key (str): Google Gemini API 키
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def read_profile_from_file(self, filename: str) -> str:
        """
        로컬 텍스트 파일에서 프로필 내용을 읽어옵니다.
        
        Args:
            filename (str): 프로필 텍스트 파일 경로
            
        Returns:
            str: 파일 내용
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"프로필 파일을 찾을 수 없습니다: {filename}")
        except Exception as e:
            raise Exception(f"프로필 파일을 읽는 중 오류 발생: {e}")

    def generate_knowledge_graph(self, profile_text: str) -> Dict[str, Any]:
        """
        프로필 텍스트로부터 지식 그래프를 생성합니다.
        
        Args:
            profile_text (str): LinkedIn 프로필 텍스트
            
        Returns:
            Dict[str, Any]: 지식 그래프 JSON 구조
        """
        prompt = f"""
다음 텍스트는 LinkedIn 프로필 내용입니다. 이 내용을 분석하여 경력, 학력, 기술, 프로젝트 등을 중심으로 구조화된 지식 그래프를 생성해 주세요.

프로필 내용:
{profile_text}

다음 JSON 형식에 맞춰서 결과를 생성해 주세요. 모든 id는 "p1", "c1", "s1"과 같이 식별자와 숫자의 조합으로 만들어주세요.

{{
    "title": "손관주(Gwan-Ju Son)의 지식 그래프",
    "entities": [
        {{
            "id": "고유 ID (예: person1, company1, skill1)",
            "name": "엔티티 이름 (예: 손관주, 한국외국어대학교, Google, Python)",
            "type": "인물 | 기관 | 기술 | 프로젝트 | 직책",
            "description": "엔티티에 대한 상세 설명"
        }}
    ],
    "relationships": [
        {{
            "source": "출발 엔티티 ID",
            "target": "도착 엔티티 ID",
            "relationship": "관계 (예: 근무, 전공, 보유 기술, 수행)"
        }}
    ]
}}

주요 추출 항목:
- 인물: 프로필 소유자 (1명)
- 기관: 근무했던 회사, 졸업한 학교
- 기술: 보유한 프로그래밍 언어, 도구, 프레임워크
- 프로젝트: 수행한 프로젝트 이름
- 직책: 맡았던 직책 (예: 연구원, 인턴)
- 관계: '손관주'는 'A회사'에서 '근무', 'B대학교'를 '졸업', 'Python' 기술을 '보유'
- 모든 내용을 한글로 작성해 주세요. JSON 형식을 정확히 지켜서 응답해 주세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            knowledge_graph = json.loads(response_text)
            return knowledge_graph
            
        except Exception as e:
            raise Exception(f"지식 그래프 생성 중 오류 발생: {e}")

    def save_to_json(self, knowledge_graph: Dict[str, Any], filename: str):
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

def main():
    """메인 실행 함수"""
    try:
        # API 키 로드
        with open('gwanju_API.txt', 'r') as f:
            api_key = f.read().strip()

        # 입출력 파일 설정
        input_filename = "linkedin_profile_assignment.txt"
        output_filename = "linkedin_kg.json"
        
        # 스크립트가 있는 디렉토리 기준으로 경로 설정
        script_dir = os.path.dirname(__file__)
        input_path = os.path.join(script_dir, input_filename)
        output_path = os.path.join(script_dir, output_filename)

        # 지식 그래프 생성기 초기화
        kg_generator = ProfileToKnowledgeGraph(api_key)

        print(f"=== LinkedIn 프로필 지식 그래프 생성 시작 ===")
        
        print(f"프로필 파일 읽는 중: {input_path}")
        profile_text = kg_generator.read_profile_from_file(input_path)
        
        print("지식 그래프를 생성하는 중... (시간이 걸릴 수 있습니다)")
        knowledge_graph = kg_generator.generate_knowledge_graph(profile_text)
        
        kg_generator.save_to_json(knowledge_graph, output_path)
        
        print("\n=== 생성 완료 ===")
        print(f"JSON 저장 완료: {output_path}")
        print(f"엔티티 수: {len(knowledge_graph.get('entities', []))}")
        print(f"관계 수: {len(knowledge_graph.get('relationships', []))}")

    except Exception as e:
        print(f"오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
