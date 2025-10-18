#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 프로필을 더 상세한 지식 그래프로 변환하는 스크립트
"""

import json
import google.generativeai as genai

def create_comprehensive_knowledge_graph():
    try:
        # API 키 설정
        genai.configure(api_key='AIzaSyC4zrhudXJO7DggAHTpivSHTF6f0dnaKww')
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 파일 읽기
        with open('linkedin_profile_assignment.txt', 'r', encoding='utf-8') as f:
            profile_text = f.read()

        print('상세한 LinkedIn 지식 그래프 생성 중...')

        # 더 상세한 프롬프트
        prompt = f"""
다음은 손관주님의 LinkedIn 프로필 전체 내용입니다. 이를 바탕으로 상세한 지식 그래프를 생성해주세요.

프로필 내용:
{profile_text}

다음 JSON 형식으로 모든 중요한 정보를 포함해서 응답해주세요:

{{
    "title": "손관주(Gwan-Ju Son)의 LinkedIn 지식 그래프",
    "entities": [
        // 인물
        {{"id": "person1", "name": "손관주", "type": "인물", "description": "한국외국어대학교 철학과 AI 비즈니스 컴퓨팅 복수전공, GPA 3.98"}},
        
        // 기관 (회사, 학교, 교육기관)
        {{"id": "univ1", "name": "한국외국어대학교", "type": "교육기관", "description": "철학과 AI 비즈니스 컴퓨팅 복수전공, 2018-2025"}},
        {{"id": "company1", "name": "ReadingStar Institute", "type": "기업", "description": "원어 수업 교사 및 담임교사로 근무"}},
        
        // 기술 및 역량
        {{"id": "skill1", "name": "Python", "type": "기술", "description": "Data Analysis with Python, Python Fundamentals"}},
        {{"id": "skill2", "name": "SQL", "type": "기술", "description": "SQL Data Analysis"}},
        
        // 프로젝트
        {{"id": "project1", "name": "Better World 아이디어 공작소", "type": "프로젝트", "description": "한국외대 제10회 Better World 아이디어 공작소 참여"}},
        
        // 직책
        {{"id": "position1", "name": "이벤트 프로젝트 매니저", "type": "직책", "description": "(주)오오칠팔구에서 담당한 직책"}},
        
        // 자격증
        {{"id": "cert1", "name": "국제무역사 1급", "type": "자격증", "description": "보유 자격증"}},
        
        // 수상
        {{"id": "award1", "name": "창업 아이디어 경진대회 최우수상", "type": "수상", "description": "전국 대학생 창업 아이디어 경진대회에서 수상"}}
    ],
    "relationships": [
        {{"source": "person1", "target": "univ1", "relationship": "재학"}},
        {{"source": "person1", "target": "company1", "relationship": "근무"}},
        {{"source": "person1", "target": "skill1", "relationship": "보유 기술"}},
        {{"source": "person1", "target": "project1", "relationship": "참여"}},
        {{"source": "person1", "target": "position1", "relationship": "담당"}},
        {{"source": "person1", "target": "cert1", "relationship": "보유"}},
        {{"source": "person1", "target": "award1", "relationship": "수상"}}
    ]
}}

요구사항:
1. 모든 경력 (12개 경력사항 모두 포함)
2. 학력 정보 (한국외국어대학교)
3. 기술/역량 (Python, SQL, Data Analysis 등 모든 Skills 포함)
4. 프로젝트 (8개 프로젝트 모두 포함)
5. 자격증 (6개 자격증 모두 포함)
6. 수상 경력
7. 각 엔티티 간의 관계

모든 정보를 빠짐없이 포함해서 최소 50개 이상의 엔티티와 관계를 생성해주세요.
JSON 형식을 정확히 지켜주세요.
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
        with open('linkedin_kg_detailed.json', 'w', encoding='utf-8') as f:
            json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)

        print('linkedin_kg_detailed.json 파일 생성 완료!')
        print(f'엔티티 수: {len(knowledge_graph.get("entities", []))}')
        print(f'관계 수: {len(knowledge_graph.get("relationships", []))}')
        
        return True

    except Exception as e:
        print(f'오류 발생: {e}')
        return False

if __name__ == "__main__":
    create_comprehensive_knowledge_graph()