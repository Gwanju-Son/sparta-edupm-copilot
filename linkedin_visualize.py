#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn 지식 그래프를 시각화하는 스크립트
"""

import json
import os
from pyvis.network import Network

def create_linkedin_visualization():
    """LinkedIn 지식 그래프를 HTML로 시각화"""
    
    # JSON 파일 읽기
    with open('linkedin_kg.json', 'r', encoding='utf-8') as f:
        kg_data = json.load(f)
    
    # Network 객체 생성
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white")
    
    # 엔티티별 색상 설정
    color_map = {
        "인물": "#FF6B6B",
        "교육 프로그램": "#4ECDC4", 
        "사업체": "#45B7D1",
        "교육기관": "#96CEB4",
        "기업": "#FFEAA7",
        "역량": "#DDA0DD",
        "습관": "#98D8C8",
        "지역": "#F7DC6F",
        "프로그램": "#BB8FCE"
    }
    
    # 노드 추가
    for entity in kg_data['entities']:
        color = color_map.get(entity['type'], "#CCCCCC")
        net.add_node(
            entity['id'], 
            label=entity['name'],
            title=f"타입: {entity['type']}\n설명: {entity['description']}",
            color=color,
            size=20 if entity['type'] == "인물" else 15
        )
    
    # 엣지 추가
    for rel in kg_data['relationships']:
        net.add_edge(
            rel['source'], 
            rel['target'], 
            label=rel['relationship'],
            color="#888888"
        )
    
    # 물리 설정
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": {"iterations": 100}
      }
    }
    """)
    
    # HTML 파일 생성
    output_file = "linkedin_knowledge_graph.html"
    net.save_graph(output_file)
    
    print(f"LinkedIn 지식 그래프 시각화가 '{output_file}'에 저장되었습니다.")
    print(f"엔티티 수: {len(kg_data['entities'])}")
    print(f"관계 수: {len(kg_data['relationships'])}")
    
    return output_file

if __name__ == "__main__":
    create_linkedin_visualization()