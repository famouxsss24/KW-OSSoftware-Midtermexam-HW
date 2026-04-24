import streamlit as st
import json
import os

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="무기체계 개발자 유형 테스트",
    page_icon="🎯",
    layout="centered"
)

# ── 과제 조건: 학번 / 이름 ────────────────────────────────────────────────────
STUDENT_ID   = "2023204088"
STUDENT_NAME = "유명현"

# ── 로그인용 사용자 정보 (미리 정의) ─────────────────────────────────────────
USERS = {
    "유명현":  "2023204088",
    "admin":   "admin123",
    "guest":   "guest",
}

# ── 캐싱: 퀴즈 데이터 로드 ───────────────────────────────────────────────────
# @st.cache_data 를 사용하면, 앱이 재렌더링될 때마다 JSON 파일을 반복해서
# 읽지 않고 처음 로드한 결과를 메모리에 저장해 재사용합니다.
# 퀴즈 데이터처럼 앱 실행 중 변하지 않는 데이터에 캐싱을 적용하면
# 불필요한 파일 I/O를 줄여 앱 성능을 높일 수 있습니다.
@st.cache_data
def load_quiz_data():
    path = os.path.join(os.path.dirname(__file__), "data", "quiz_data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── session_state 초기화 ──────────────────────────────────────────────────────
# session_state는 Streamlit이 재렌더링되어도 값을 유지하는 저장소입니다.
# 로그인 상태, 현재 문제 번호, 점수 등을 여기에 보관합니다.
def init_state():
    defaults = {
        "page":      "welcome",   # 현재 화면
        "logged_in": False,       # 로그인 여부
        "username":  "",          # 로그인한 사용자명
        "current_q": 0,           # 현재 문제 인덱스 (0~9)
        "scores": {               # 유형별 누적 점수
            "유도무기": 0,
            "전자전":   0,
            "사격통제": 0,
            "임베디드": 0,
        },
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()


# ── 헬퍼: 페이지 이동 ────────────────────────────────────────────────────────
def go_to(page: str):
    st.session_state.page = page
    st.rerun()


# ────────────────────────────────────────────────────────────────────────────
# 페이지 1 : 첫 화면 (학번/이름 + 앱 소개)
# ────────────────────────────────────────────────────────────────────────────
def page_welcome():
    # 과제 조건 — 첫 화면에 학번과 이름 표시
    st.caption(f"학번: {STUDENT_ID}　|　이름: {STUDENT_NAME}")
    st.divider()

    st.title("🎯 나는 어떤 무기체계 개발자일까?")
    st.caption("만약 내가 무기체계 개발자라면?")
    st.subheader("방산 SW 개발자 유형 테스트")
    st.write("")

    st.markdown(
        """
        **내 손으로 만든 소프트웨어로 나라를 지킬 수 있다면**, 그를 바탕으로 한 자긍심은 어마어마 합니다.

        개발 직무를 희망하지만, **어떤 분야의 개발이 적성에 맞는지** 고민하는 학우들을 보며,
        같은 길을 걷자고 설득함과 동시에 조금이나마 방향을 잡는 데 도움이 되고자 이 앱을 만들었습니다.

        **10가지 상황 질문**에 답하면, 당신에게 어울리는 무기체계 개발 직군과
        다양한 커리어 방향을 알려드립니다.
        """
    )

    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎯 유도무기 SW",    "정밀·분석형")
    col2.metric("⚡ 전자전 시스템",   "창의·도전형")
    col3.metric("🔭 사격통제 SW",    "체계·리더형")
    col4.metric("🔧 임베디드 펌웨어", "장인·집중형")

    st.divider()

    if st.button("테스트 시작하기 →", type="primary", use_container_width=True):
        go_to("login")


# ────────────────────────────────────────────────────────────────────────────
# 페이지 2 : 로그인
# ────────────────────────────────────────────────────────────────────────────
def page_login():
    st.title("🔐 로그인")
    st.write("테스트를 시작하려면 로그인이 필요합니다.")
    st.divider()

    username = st.text_input("아이디", placeholder="아이디를 입력하세요")
    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")

    col_login, col_back = st.columns(2)

    with col_login:
        if st.button("로그인", type="primary", use_container_width=True):
            # 로그인 처리: 미리 정의된 USERS 딕셔너리와 비교
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username  = username
                # 퀴즈 상태 초기화 (재시도 대비)
                st.session_state.current_q = 0
                st.session_state.scores    = {"유도무기": 0, "전자전": 0, "사격통제": 0, "임베디드": 0}
                st.success(f"환영합니다, {username}님!")
                go_to("quiz")
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

    with col_back:
        if st.button("← 뒤로", use_container_width=True):
            go_to("welcome")

    st.write("")
    with st.expander("테스트 계정 보기"):
        st.code(
            "아이디: guest    /  비밀번호: guest\n"
            "아이디: admin    /  비밀번호: admin123"
        )


# ────────────────────────────────────────────────────────────────────────────
# 페이지 3 : 퀴즈
# ────────────────────────────────────────────────────────────────────────────
def page_quiz():
    # 로그인 체크
    if not st.session_state.logged_in:
        go_to("login")
        return

    # 캐싱된 퀴즈 데이터 불러오기
    data      = load_quiz_data()
    questions = data["questions"]
    total     = len(questions)
    idx       = st.session_state.current_q

    # ── 상단: 진행 상황 ──
    st.caption(f"안녕하세요, {st.session_state.username}님!")
    st.progress((idx) / total, text=f"진행: {idx} / {total} 문제 완료")
    st.divider()

    # ── 현재 문제 ──
    q       = questions[idx]
    options = [opt["text"] for opt in q["options"]]
    opt_map = {opt["text"]: opt["type"] for opt in q["options"]}

    st.subheader(f"Q{idx + 1}. {q['question']}")
    st.write("")

    # index=None → 아무것도 선택되지 않은 상태로 시작
    selected = st.radio(
        "보기를 선택하세요",
        options,
        index=None,
        key=f"q_{idx}",
        label_visibility="collapsed"
    )

    st.divider()

    # 보기를 선택해야 다음 버튼 활성화
    _, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button(
            "다음 →" if idx + 1 < total else "결과 보기 →",
            type="primary",
            use_container_width=True,
            disabled=(selected is None)
        ):
            # 선택한 보기에 해당하는 유형의 점수 +1
            st.session_state.scores[opt_map[selected]] += 1

            if idx + 1 < total:
                st.session_state.current_q += 1
                st.rerun()
            else:
                go_to("result")


# ────────────────────────────────────────────────────────────────────────────
# 페이지 4 : 결과
# ────────────────────────────────────────────────────────────────────────────
def page_result():
    # 로그인 체크
    if not st.session_state.logged_in:
        go_to("login")
        return

    data    = load_quiz_data()
    scores  = st.session_state.scores

    # 가장 점수가 높은 유형을 결과로 판별
    result_type = max(scores, key=scores.get)
    result      = data["results"][result_type]

    st.balloons()

    st.caption(f"학번: {STUDENT_ID}　|　이름: {STUDENT_NAME}")
    st.title("📊 테스트 결과")
    st.divider()

    # ── 결과 유형 제목 ──
    st.header(f"{result['emoji']} {result['title']}")
    st.write("")

    # ── 점수 분포 ──
    with st.expander("내 점수 분포 보기"):
        for type_name, score in scores.items():
            r = data["results"][type_name]
            label = f"{r['emoji']} {type_name}: {score}점"
            st.progress(score / 10, text=label)

    st.divider()

    # ── 성격 설명 ──
    st.subheader("당신의 성격")
    st.info(result["personality"])

    # ── 방산 강점 ──
    st.subheader("방산 업계에서의 강점")
    st.success(
        f"**{result['role']}** 가 된다면,\n\n{result['strengths']}"
    )

    # ── 어울리는 직군 ──
    st.subheader("어울리는 직군")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🛡️ 방산 / 항공**")
        for c in result["careers"]["defense"]:
            st.markdown(f"- {c}")

    with col2:
        st.markdown("**💻 앱 / 웹 / 데이터**")
        for c in result["careers"]["dev"]:
            st.markdown(f"- {c}")

    with col3:
        st.markdown("**🌏 그 외 분야**")
        for c in result["careers"]["other"]:
            st.markdown(f"- {c}")

    st.divider()

    col_retry, col_home = st.columns(2)
    with col_retry:
        if st.button("🔄 다시 테스트하기", use_container_width=True):
            st.session_state.current_q = 0
            st.session_state.scores    = {"유도무기": 0, "전자전": 0, "사격통제": 0, "임베디드": 0}
            go_to("quiz")
    with col_home:
        if st.button("🏠 처음으로", use_container_width=True):
            st.session_state.current_q = 0
            st.session_state.scores    = {"유도무기": 0, "전자전": 0, "사격통제": 0, "임베디드": 0}
            st.session_state.logged_in = False
            go_to("welcome")


# ────────────────────────────────────────────────────────────────────────────
# 라우터: session_state.page 값에 따라 해당 페이지 함수 실행
# ────────────────────────────────────────────────────────────────────────────
PAGES = {
    "welcome": page_welcome,
    "login":   page_login,
    "quiz":    page_quiz,
    "result":  page_result,
}

PAGES[st.session_state.page]()
