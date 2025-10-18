import streamlit as st


def run():
    st.subheader("사후 회고 입력")
    attend = st.slider("수강률(%)", 40, 100, 87)
    assign = st.slider("과제제출률(%)", 40, 100, 92)
    sat = st.slider("만족도(5점)", 1.0, 5.0, 4.6, 0.1)
    nps = st.slider("NPS", -100, 100, 42)
    feedback = st.text_area("핵심 피드백", "2주차 난이도 다소 높음, 실습시간 확장 희망")

    if st.button("개선안 제시"):
        actions = []
        if attend < 80:
            actions.append("다음 기수: 리마인드 시점 확대, 보강 세션 도입")
        if assign < 80:
            actions.append("과제 가이드 명확화, 마감 48/12시간 전 알림")
        if sat < 4.0:
            actions.append("체크인 질문 추가, 인터랙션 강화")
        if nps < 0:
            actions.append("성과 공유 주기 상향, 이해관계자 커뮤니케이션 강화")
        if "난이도" in feedback:
            actions.append("2주차 실습 쉬운 예제 추가, 사전가이드 배포, 실습시간 +20분")
        st.success("다음 기수 액션")
        for a in actions or ["현재 운영 유지, 베스트 프랙티스 문서화"]:
            st.write(f"- {a}")
