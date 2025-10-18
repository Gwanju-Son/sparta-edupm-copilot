import streamlit as st


def run():
    st.subheader("타임라인 & RACI")
    st.markdown(
        """
- **T-14 ~ T-7**: 선발/OT/환경점검 (고객사: 대상자 공지, Sparta: 튜터배정/콘텐츠 점검)
- **W1~W4**: 주차별 교육(과제/퀴즈/피드백)
- **W4+1**: 수료, 보고서 제출

**RACI**: PM(A), 튜터(R), 운영(C), 고객사 담당자(I)
"""
    )
    st.success("좌측 메뉴에서 운영 체크리스트로 이동하세요.")
