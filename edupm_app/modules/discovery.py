import streamlit as st


def run():
    st.subheader("Discovery: 고객 니즈 파악")
    industry = st.selectbox("산업", ["제조", "금융", "IT", "유통", "공공"])  # noqa: F841
    role = st.selectbox("대상 직무", ["마케팅", "영업", "HR", "데이터", "개발"])  # noqa: F841
    level = st.selectbox("레벨", ["입문", "실무", "리더"])  # noqa: F841
    size = st.number_input("예상 인원", 10, 1000, 40)  # noqa: F841
    duration = st.selectbox("기간", ["1일", "2일", "4주", "6주", "8주"])  # noqa: F841
    goals = st.text_area("학습 목표(KPI)", "현업 적용률 70% 달성 / PoC 1건")
    constraints = st.text_area("제약(시간/보안/환경)", "사내망 / 평일 야간만")
    budget = st.text_input("예산 범위(선택)", "2천~3천만원")

    if st.button("요약 브리프 생성"):
        st.session_state.brief = {
            "industry": industry,
            "role": role,
            "level": level,
            "size": size,
            "duration": duration,
            "goals": goals,
            "constraints": constraints,
            "budget": budget,
        }
        st.success("브리프가 생성되었습니다. 좌측 메뉴에서 다음 단계로 이동하세요.")
