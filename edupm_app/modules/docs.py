import streamlit as st


def run():
    st.subheader("문서 자동화 데모")
    st.markdown("**제안서 본문, 안내 메일, 회고 리포트 요약** 초안이 생성됩니다. (샘플 텍스트)")
    if st.session_state.get("brief"):
        b = st.session_state.brief
        st.write("제안서 개요")
        st.json({
            "고객 산업": b.get("industry"),
            "대상": f"{b.get('role')} / {b.get('level')}",
            "인원/기간": f"{b.get('size')}명 / {b.get('duration')}",
            "목표": b.get("goals"),
            "제약": b.get("constraints"),
            "예산": b.get("budget"),
        })
        st.write("메일 템플릿 예시")
        st.code(
            """
[제안 메일 초안]
안녕하세요, 고객사 담당자님.
요청하신 교육 제안 초안을 공유드립니다.
목표 및 제약을 반영하여 4주 트랙과 운영방안을 설계했습니다.
첨부 문서를 검토 부탁드리며, 세부 조정은 미팅에서 논의하면 좋겠습니다.
감사합니다.
""",
            language="text",
        )
    else:
        st.info("Discovery 단계에서 브리프 생성 후 이용해 주세요.")
    st.success("좌측 메뉴에서 사후 회고로 이동하세요.")
