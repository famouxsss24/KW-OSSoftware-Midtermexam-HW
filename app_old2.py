import streamlit as st
import json
import os
import hashlib
import re

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="무기체계 개발자 유형 테스트",
    page_icon="🎯",
    layout="centered"
)

# ── 과제 조건: 학번 / 이름 ────────────────────────────────────────────────────
STUDENT_ID   = "2023204088"
STUDENT_NAME = "유명현"

# ── 경로 / 검증 규칙 설정 ────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
USERS_PATH = os.path.join(BASE_DIR, "data", "users.json")
QUIZ_PATH  = os.path.join(BASE_DIR, "data", "quiz_data.json")

ID_REGEX   = re.compile(r"^[a-zA-Z0-9]+$")  # 영문·숫자만
MIN_ID_LEN = 3
MAX_ID_LEN = 20
MIN_PW_LEN = 4

# 첫 실행 시 users.json이 없으면 이 3계정으로 초기화됨 (비번은 해시됨)
DEFAULT_USERS = {
    "유명현":  "2023204088",
    "admin":   "admin123",
    "guest":   "guest",
}


# ── 비밀번호 해싱 ────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    """SHA256으로 비밀번호를 해시. 평문 저장 금지 원칙."""
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


# ── 사용자 저장소 I/O ────────────────────────────────────────────────────────
# ⚠️ 캐싱하지 않음: 회원가입으로 파일이 변하면 즉시 반영되어야 함.
#    (quiz_data.json은 변하지 않으니 캐싱, users.json은 변하니 비캐싱)
def load_users() -> dict:
    """users.json을 읽어 {username: password_hash} 딕셔너리 반환.
       파일이 없으면 DEFAULT_USERS를 해시해서 최초 생성."""
    if not os.path.exists(USERS_PATH):
        initial = {u: hash_password(p) for u, p in DEFAULT_USERS.items()}
        os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
        with open(USERS_PATH, "w", encoding="utf-8") as f:
            json.dump(initial, f, ensure_ascii=False, indent=2)
        return initial
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users: dict) -> None:
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# ── 캐싱: 퀴즈 데이터 로드 ───────────────────────────────────────────────────
# 퀴즈 데이터처럼 앱 실행 중 변하지 않는 데이터에 캐싱을 적용하면
# 불필요한 파일 I/O를 줄여 앱 성능을 높일 수 있습니다.
@st.cache_data
def load_quiz_data():
    with open(QUIZ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ── session_state 초기화 ──────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page":      "welcome",
        "logged_in": False,
        "username":  "",
        "current_q": 0,
        "scores": {
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


# ── 회원가입 검증 ────────────────────────────────────────────────────────────
def validate_signup(username: str, password: str, password_confirm: str, users: dict):
    """검증 실패 시 (False, 에러메시지), 통과 시 (True, '')"""
    if not username or not password or not password_confirm:
        return False, "모든 항목을 입력해주세요."
    if not (MIN_ID_LEN <= len(username) <= MAX_ID_LEN):
        return False, f"아이디는 {MIN_ID_LEN}~{MAX_ID_LEN}자 사이여야 합니다."
    if not ID_REGEX.match(username):
        return False, "아이디는 영문과 숫자만 사용할 수 있습니다."
    if len(password) < MIN_PW_LEN:
        return False, f"비밀번호는 최소 {MIN_PW_LEN}자 이상이어야 합니다."
    if password != password_confirm:
        return False, "비밀번호가 서로 일치하지 않습니다."
    if username in users:
        return False, "이미 존재하는 아이디입니다."
    return True, ""


# ────────────────────────────────────────────────────────────────────────────
# 페이지 1 : 첫 화면 (학번/이름 + 앱 소개)
# ────────────────────────────────────────────────────────────────────────────
def page_welcome():
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
            users = load_users()
            if username in users and users[username] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.current_q = 0
                st.session_state.scores    = {"유도무기": 0, "전자전": 0, "사격통제": 0, "임베디드": 0}
                st.success(f"환영합니다, {username}님!")
                go_to("quiz")
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

    with col_back:
        if st.button("← 뒤로", use_container_width=True):
            go_to("welcome")

    st.divider()

    # 회원가입 안내
    col_msg, col_btn = st.columns([3, 2])
    with col_msg:
        st.write("아직 계정이 없으신가요?")
    with col_btn:
        if st.button("회원가입하기", use_container_width=True):
            go_to("signup")

    st.write("")
    with st.expander("테스트 계정 보기"):
        st.code(
            "아이디: guest    /  비밀번호: guest\n"
            "아이디: admin    /  비밀번호: admin123"
        )


# ────────────────────────────────────────────────────────────────────────────
# 페이지 2-2 : 회원가입
# ────────────────────────────────────────────────────────────────────────────
def page_signup():
    st.title("📝 회원가입")
    st.write("새 계정을 만들어 테스트를 시작해보세요.")
    st.divider()

    username = st.text_input(
        "아이디",
        placeholder=f"영문·숫자, {MIN_ID_LEN}~{MAX_ID_LEN}자"
    )
    password = st.text_input(
        "비밀번호",
        type="password",
        placeholder=f"최소 {MIN_PW_LEN}자 이상"
    )
    password_confirm = st.text_input(
        "비밀번호 확인",
        type="password",
        placeholder="비밀번호를 한 번 더 입력"
    )

    st.caption(
        f"· 아이디: 영문·숫자만 사용, {MIN_ID_LEN}~{MAX_ID_LEN}자\n"
        f"· 비밀번호: 최소 {MIN_PW_LEN}자 이상"
    )

    st.divider()

    col_submit, col_back = st.columns(2)
    with col_submit:
        if st.button("가입하기", type="primary", use_container_width=True):
            users = load_users()
            ok, msg = validate_signup(username, password, password_confirm, users)
            if not ok:
                st.error(msg)
            else:
                users[username] = hash_password(password)
                save_users(users)
                st.success(f"✅ {username}님, 회원가입이 완료되었습니다!")
                go_to("login")

    with col_back:
        if st.button("← 로그인으로", use_container_width=True):
            go_to("login")


# ────────────────────────────────────────────────────────────────────────────
# 페이지 3 : 퀴즈
# ────────────────────────────────────────────────────────────────────────────
def page_quiz():
    if not st.session_state.logged_in:
        go_to("login")
        return

    data      = load_quiz_data()
    questions = data["questions"]
    total     = len(questions)
    idx       = st.session_state.current_q

    st.caption(f"안녕하세요, {st.session_state.username}님!")
    st.progress((idx) / total, text=f"진행: {idx} / {total} 문제 완료")
    st.divider()

    q       = questions[idx]
    options = [opt["text"] for opt in q["options"]]
    opt_map = {opt["text"]: opt["type"] for opt in q["options"]}

    st.subheader(f"Q{idx + 1}. {q['question']}")
    st.write("")

    selected = st.radio(
        "보기를 선택하세요",
        options,
        index=None,
        key=f"q_{idx}",
        label_visibility="collapsed"
    )

    st.divider()

    _, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button(
            "다음 →" if idx + 1 < total else "결과 보기 →",
            type="primary",
            use_container_width=True,
            disabled=(selected is None)
        ):
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
    if not st.session_state.logged_in:
        go_to("login")
        return

    data    = load_quiz_data()
    scores  = st.session_state.scores

    result_type = max(scores, key=scores.get)
    result      = data["results"][result_type]

    st.balloons()

    st.caption(f"학번: {STUDENT_ID}　|　이름: {STUDENT_NAME}")
    st.title("📊 테스트 결과")
    st.divider()

    st.header(f"{result['emoji']} {result['title']}")
    st.write("")

    with st.expander("내 점수 분포 보기"):
        for type_name, score in scores.items():
            r = data["results"][type_name]
            label = f"{r['emoji']} {type_name}: {score}점"
            st.progress(score / 10, text=label)

    st.divider()

    st.subheader("당신의 성격")
    st.info(result["personality"])

    st.subheader("방산 업계에서의 강점")
    st.success(
        f"**{result['role']}** 가 된다면,\n\n{result['strengths']}"
    )

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
# 라우터
# ────────────────────────────────────────────────────────────────────────────
PAGES = {
    "welcome": page_welcome,
    "login":   page_login,
    "signup":  page_signup,   # ← 신규 추가
    "quiz":    page_quiz,
    "result":  page_result,
}

PAGES[st.session_state.page]()
