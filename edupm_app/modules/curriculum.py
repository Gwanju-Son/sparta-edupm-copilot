import streamlit as st


def run():
    st.subheader("커리큘럼 제안")
    if not st.session_state.get("brief"):
        st.info("먼저 Discovery에서 브리프를 생성해 주세요.")
        return
    b = st.session_state.brief
    modules = [
        f"[Week1] {b['role']} 업무 이해 & 데이터 리터러시",
        "[Week2] AI 활용 사례 & 프롬프트 엔지니어링",
        "[Week3] 실습: 사내 데이터로 KPI 정의 & 미니분석",
        "[Week4] 자동화: 노코드/파이썬으로 리포트 생성",
        "Capstone: 우리팀 Use-case 설계 & 발표",
    ]
    st.write("추천 모듈")
    st.markdown("\n".join([f"- {m}" for m in modules]))
    st.session_state.outputs["modules"] = modules
    st.success("좌측 메뉴에서 타임라인으로 이동할 수 있습니다.")
