#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 프로필을 지식 그래프로 변환하는 간단한 스크립트
"""

import json
import google.generativeai as genai

def main():
    try:
        # API 키 설정
        genai.configure(api_key='AIzaSyC4zrhudXJO7DggAHTpivSHTF6f0dnaKww')
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 파일 읽기
        with open('linkedin_profile_assignment.txt', 'r', encoding='utf-8') as f:
            profile_text = f.read()

        print('프로필 텍스트 읽기 완료')
        print('지식 그래프 생성 중...')

        # 더 간단한 프롬프트로 시작
        prompt = f"""
다음은 손관주님의 LinkedIn 프로필입니다. 이 정보를 바탕으로 지식 그래프를 JSON 형식으로 만들어주세요.

프로필 내용:
{profile_text[:2000]}...

다음 형식으로 응답해주세요:
{{
    "title": "손관주의 지식 그래프",
    "entities": [
        {{"id": "person1", "name": "손관주", "type": "인물", "description": "한국외국어대학교 학생"}},
        {{"id": "univ1", "name": "한국외국어대학교", "type": "기관", "description": "철학과 AI 비즈니스 컴퓨팅 복수전공"}}
    ],
    "relationships": [
        {{"source": "person1", "target": "univ1", "relationship": "재학"}}
    ]
}}

간단하고 명확한 JSON만 응답해주세요.
"""

        # Gemini API 호출
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        print('응답 받음, JSON 파싱 중...')

        # JSON 파싱
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        knowledge_graph = json.loads(response_text)

        # 파일 저장
        with open('linkedin_kg.json', 'w', encoding='utf-8') as f:
            json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)

        print('linkedin_kg.json 파일 생성 완료!')
        print(f'엔티티 수: {len(knowledge_graph.get("entities", []))}')
        print(f'관계 수: {len(knowledge_graph.get("relationships", []))}')
        
        return True

    except Exception as e:
        print(f'오류 발생: {e}')
        return False

if __name__ == "__main__":
    main()