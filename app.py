# 광운대 정보융합학부 2학년 유명현 (2023204088)
# 오픈소스소프트웨어실습 중간고사 대체과제 - Streamlit
# 주제: 나는 어떤 무기체계 개발자일까?

import os
import re
import json
import base64
import hashlib

import streamlit as st
import plotly.graph_objects as go


# 페이지 기본설정
# 이거 안 해주면 탭 제목이 그냥 streamlit 으로 
st.set_page_config(
    page_title="나는 어떤 무기체계 개발자일까?",
    page_icon="🛡️",
    layout="centered",
)


# ---- 경로 ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_PATH = os.path.join(DATA_DIR, "users.json")
STATS_PATH = os.path.join(DATA_DIR, "stats.json")
BG_IMAGE_PATH = os.path.join(DATA_DIR, "background.png")

# 처음 실행했을 때 data 폴더 없으면 에러나서 추가
os.makedirs(DATA_DIR, exist_ok=True)


# 회원가입 규칙
# 영문/숫자만 - 정규식..? 일단 ^...$ 가 처음~끝까지란 뜻
ID_REGEX = re.compile(r"^[a-zA-Z0-9]+$")
MIN_PW_LEN = 4

# 처음에 비밀번호 평문으로 저장했다가 그러면 안 된다고 해서 해시 적용
# 시연용 기본 계정 
DEFAULT_USERS = {
    "유명현": "2023204088",
    "admin": "admin123",
    "guest": "guest",
}



# 퀴즈 데이터

# 처음엔 개발자스러운 질문(MCU, 프로토콜...) 만 넣었으나
# 친구한테 풀어보라 했더니 못 풀어서 일상 질문으로 다 갈아엎기
# 4가지 유형:
#   guided   = 정확한 계산/모델링 좋아하는 느김
#   ew       = 숨은 단서 찾는 느낌
#   fcs      = 큰 그림/시스템 짜는 느낌
#   embedded = 손으로 직접 만드는 느낌
QUESTIONS = [
    {
        "q": "새로운 프로젝트나 모임을 시작할 때, 나는 주로?",
        "options": [
            ("전체 계획과 숫자를 꼼꼼하게 먼저 짜두는 편", "guided"),
            ("흩어져 있는 정보를 끌어모아 분석하는 편", "ew"),
            ("큰 그림을 그리고 누가 뭘 맡을지 역할을 나누는 편", "fcs"),
            ("일단 뭐라도 만들어보면서 방향을 잡는 편", "embedded"),
        ],
    },
    {
        "q": "학창 시절에 가장 재밌었던 과목은?",
        "options": [
            ("수학 - 답이 딱 떨어지는 게 좋았다", "guided"),
            ("과학 - 어떤 현상이 왜 그런지 파고드는 게 재밌었다", "ew"),
            ("사회/역사 - 큰 흐름을 이해하는 게 좋았다", "fcs"),
            ("기술·가정·미술 - 직접 만드는 수업이 좋았다", "embedded"),
        ],
    },
    {
        "q": "문제가 생기면 나는 본능적으로?",
        "options": [
            ("수치로 계산해서 뭐가 어디서 틀어졌는지 비교해본다", "guided"),
            ("흔적이나 기록을 꼼꼼히 뒤져서 원인을 추적한다", "ew"),
            ("관련된 요소들 사이 관계를 그림으로 그려본다", "fcs"),
            ("일단 만져보고 두들겨봐서 감을 잡는다", "embedded"),
        ],
    },
    {
        "q": "팀 프로젝트에서 내가 자주 맡는 역할은?",
        "options": [
            ("기획·계산같은 머리 쓰는 일", "guided"),
            ("자료 조사, 정보 수집·분석 담당", "ew"),
            ("전체 방향 잡고 팀을 조율하는 역할", "fcs"),
            ("실제 결과물을 내 손으로 만드는 역할", "embedded"),
        ],
    },
    {
        "q": "어떤 영화/드라마가 더 끌려?",
        "options": [
            ("정밀한 작전·저격수가 나오는 미션 영화", "guided"),
            ("스파이·해커·수사물처럼 단서 찾는 이야기", "ew"),
            ("전쟁·정치 드라마처럼 큰 판이 움직이는 이야기", "fcs"),
            ("로봇·메카닉·SF 영화처럼 기계가 움직이는 이야기", "embedded"),
        ],
    },
    {
        "q": "이런 상황은 진짜 답답하다",
        "options": [
            ("근거 없이 '그냥 느낌으로' 결정해야 할 때", "guided"),
            ("단서를 더 볼 수 있는데 대충 넘어가야 할 때", "ew"),
            ("전체 그림 없이 급한 것만 쳐내야 할 때", "fcs"),
            ("손은 대지도 못하고 보고만 해야 할 때", "embedded"),
        ],
    },
    {
        "q": "성취감이 가장 크게 오는 순간은?",
        "options": [
            ("예상하고 계산했던 결과가 실제로 맞아떨어질 때", "guided"),
            ("남들이 놓쳤던 걸 내가 발견해냈을 때", "ew"),
            ("여러 사람·요소를 엮어서 하나로 굴러가게 만들었을 때", "fcs"),
            ("안 움직이던 게 내 손으로 처음 움직였을 때", "embedded"),
        ],
    },
    {
        "q": "취미로 해보고 싶은 건?",
        "options": [
            ("바둑·체스·수학 퍼즐 같은 논리 게임", "guided"),
            ("방탈출·추리 게임", "ew"),
            ("보드게임·전략 시뮬레이션 게임", "fcs"),
            ("DIY·레고·드론 조립", "embedded"),
        ],
    },
    {
        "q": "더 멋있어 보이는 직업은?",
        "options": [
            ("숫자로 세상을 설명하는 과학자/연구원", "guided"),
            ("숨어있는 진실을 찾아내는 분석가/프로파일러", "ew"),
            ("큰 조직이나 도시를 설계하는 건축가/기획자", "fcs"),
            ("내 손으로 만든 걸 돌아가게 하는 엔지니어/메이커", "embedded"),
        ],
    },
    {
        "q": "10년 뒤 내가 이상적으로 되고 싶은 모습은?",
        "options": [
            ("정확한 계산과 판단으로 중요한 결정을 내리는 전문가", "guided"),
            ("남들이 못 보는 패턴과 진실을 찾아내는 전문가", "ew"),
            ("많은 사람·시스템을 엮어서 움직이게 하는 사람", "fcs"),
            ("내가 만든 것이 실제로 세상을 돌아다니는 걸 보는 사람", "embedded"),
        ],
    },
]

# 결과 데이터
# 처음엔 외부 json 파일로 뺐다가 그냥 코드에 박는게 편해서 다시 가져오기
RESULTS = {
    "guided": {
        "emoji": "🎯",
        "title": "유도무기 / 항법 알고리즘 개발자",
        "personality": "수식을 좋아하고, 현상을 모델로 압축해내는 걸 즐기는 스타일. 결과를 숫자로 검증하려는 성향이 강함.",
        "role": "미사일·유도무기 체계의 항법·제어·유도 알고리즘을 설계하고, 시뮬레이션과 실측 데이터를 비교하면서 성능을 끌어올리는 역할.",
        "strengths": [
            "수학·물리 기반 모델링",
            "제어 / 항법 / 유도 알고리즘 설계",
            "MATLAB · Simulink 시뮬레이션",
        ],
        "courses": ["제어공학", "신호 및 시스템", "선형대수학", "확률 및 랜덤신호", "수치해석"],
        "fields": [
            "칼만 필터 / 확장 칼만 필터",
            "유도 항법(INS/GPS) 알고리즘",
            "MATLAB · Simulink 시뮬레이션",
            "최적 제어 · 추정 이론",
        ],
        "careers": {
            "방산": ["LIG넥스원 유도무기연구소", "한화에어로스페이스 유도무기/정밀타격"],
            "일반 SW": ["자율주행 인지/추정 엔지니어", "로봇·드론 항법 알고리즘 엔지니어"],
            "기타": ["위성 항법 연구", "모빌리티 센서 융합 R&D"],
        },
    },
    "ew": {
        "emoji": "📡",
        "title": "전자전 / 신호처리 개발자",
        "personality": "남들이 못 보는 신호에서 패턴을 찾는 걸 좋아하고, '이거 왜 이래?' 를 끝까지 파고드는 탐정 스타일.",
        "role": "레이더·통신 신호를 수집하고 분석해서, 적의 전파를 식별하거나 재밍·기만하는 전자전 시스템 SW를 개발.",
        "strengths": [
            "디지털 신호처리 · 통신 이론",
            "RF 하드웨어 이해 + SDR 활용",
            "신호 기반 역공학 · 보안 마인드",
        ],
        "courses": ["통신이론", "디지털신호처리(DSP)", "네트워크 보안", "RF·안테나공학", "확률 및 랜덤신호"],
        "fields": [
            "레이더 / SDR(GNU Radio)",
            "재밍 · 스푸핑 · 기만",
            "무선 보안 CTF",
            "주파수 스펙트럼 분석",
        ],
        "careers": {
            "방산": ["한화시스템 전자전·레이더", "LIG넥스원 전자전 체계"],
            "일반 SW": ["통신장비·SDR 펌웨어 개발자", "무선 보안 리서처"],
            "기타": ["5G/6G RF 알고리즘 엔지니어", "차량 V2X 통신 연구"],
        },
    },
    "fcs": {
        "emoji": "🖥️",
        "title": "사격통제 · 지휘통제 SW 개발자",
        "personality": "하나의 기능보다 '시스템 전체가 어떻게 이어져 있는가' 에 먼저 눈이 가는 구조 지향형.",
        "role": "센서·통신·화기·디스플레이를 묶어 지휘관이 의사결정할 수 있게 해주는 사격통제·지휘통제(C4I) 소프트웨어를 설계·구현.",
        "strengths": [
            "시스템 아키텍처 설계",
            "네트워크 / 분산 처리",
            "요구분석 · 인터페이스 설계",
        ],
        "courses": ["소프트웨어공학", "시스템프로그래밍", "자료구조", "컴퓨터네트워크", "운영체제"],
        "fields": [
            "C4I / C4ISR 시스템",
            "전술 데이터링크(Link-16 등)",
            "ROS · 분산 시스템",
            "지휘통제용 HMI / UX",
        ],
        "careers": {
            "방산": ["한화시스템 방산SW·지휘통제", "LIG넥스원 사격통제체계"],
            "일반 SW": ["대규모 백엔드·실시간 시스템 개발자", "로봇 통합 SW 아키텍트"],
            "기타": ["교통관제·항공관제 SW", "재난 대응 통합 플랫폼"],
        },
    },
    "embedded": {
        "emoji": "🤖",
        "title": "드론·로봇 임베디드 SW 개발자",
        "personality": "추상적인 이론보다 '내 손으로 움직이게 한다' 에서 성취감을 크게 느끼는 타입.",
        "role": "드론·무인지상차량·로봇의 두뇌가 되는 비행제어기(FCU)·ECU 펌웨어, RTOS 기반 임베디드 SW를 개발·최적화.",
        "strengths": [
            "C / C++ 저수준 프로그래밍",
            "RTOS · 인터럽트 · 메모리 관리",
            "센서·모터 드라이버 / 펌웨어 디버깅",
        ],
        "courses": ["임베디드시스템", "마이크로프로세서", "전자회로", "C언어 프로그래밍", "디지털논리회로"],
        "fields": [
            "RTOS(FreeRTOS 등)",
            "FCU(비행제어기) · ECU 펌웨어",
            "STM32 · 라즈베리파이 · Jetson",
            "센서 드라이버 · 모터 제어",
        ],
        "careers": {
            "방산": ["한화에어로스페이스 무인체계/드론", "LIG넥스원 무인기체계"],
            "일반 SW": ["로보틱스 임베디드 엔지니어", "자율주행 제어기 펌웨어 개발자"],
            "기타": ["IoT·스마트팩토리 엣지 디바이스", "전기차 ECU · BMS 개발"],
        },
    },
}

# 차트에 보여줄 한글 이름
TYPE_LABELS = {
    "guided": "유도무기",
    "ew": "전자전",
    "fcs": "사격통제",
    "embedded": "임베디드",
}



# 비밀번호 해시 / 사용자 파일

def hash_password(pw):
    # SHA-256 으로 단방향 해시
    # encode 안 해서 에러났었음. 문자열을 바이트로 바꿔야 
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def load_users():
    # 처음 실행이면 users.json 이 없으니까 기본 계정으로 
    if not os.path.exists(USERS_PATH):
        initial = {}
        for username in DEFAULT_USERS:
            plain_pw = DEFAULT_USERS[username]
            initial[username] = hash_password(plain_pw)
        with open(USERS_PATH, "w", encoding="utf-8") as f:
            json.dump(initial, f, ensure_ascii=False, indent=2)
        return initial

    with open(USERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)



# 통계 파일 (전체 사용자 결과 카운트)

def load_stats():
    if not os.path.exists(STATS_PATH):
        # 첫 실행이면 0으로 초기화해서 만들기
        empty = {"guided": 0, "ew": 0, "fcs": 0, "embedded": 0}
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump(empty, f, ensure_ascii=False, indent=2)
        return empty
    with open(STATS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def add_stat(result_type):
    # 결과 페이지 갈 때마다 +1
    stats = load_stats()
    stats[result_type] = stats[result_type] + 1
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)



# 캐싱 - 안 바뀌는 데이터는 한 번만 읽고 들고 있게


@st.cache_data
def get_questions():
    return QUESTIONS


@st.cache_data
def get_results():
    return RESULTS


@st.cache_data
def get_background_b64():
    # 배경 이미지가 있으면 base64 로 인코딩
    # 없으면 None 돌려서 fallback 그라데이션이 깔리게
    if not os.path.exists(BG_IMAGE_PATH):
        return None
    with open(BG_IMAGE_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# 전역 CSS
# Streamlit 은 배경 바꾸는 메뉴가 없어서 이렇게 직접 주입해야 ㅠㅠ

def inject_global_css():
    bg_b64 = get_background_b64()

    # 배경 이미지가 있으면 그걸로, 없으면 그라데이션
    if bg_b64 is not None:
        bg_layer = (
            "linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)),"
            "url('data:image/png;base64," + bg_b64 + "')"
        )
        bg_size = "cover"
    else:
        bg_layer = "radial-gradient(circle at 30% 20%, #1a2a1a 0%, #050505 70%)"
        bg_size = "auto"

    # 큰 제목이 두 줄로 밀려서 max-width 늘리고 nowrap 추가
    css = """
    <style>
    .stApp {
        background-image: """ + bg_layer + """;
        background-size: """ + bg_size + """;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }

    .block-container {
        max-width: 920px !important;
        background-color: rgba(10, 14, 10, 0.72);
        border: 1px solid rgba(120, 160, 120, 0.25);
        border-radius: 14px;
        padding: 2.5rem 2.8rem !important;
        margin-top: 2rem;
    }

    .stApp, .stApp p, .stApp label, .stApp span {
        color: #e6ecd6;
    }
    h1, h2, h3 {
        color: #f3f6e6 !important;
        letter-spacing: 0.3px;
    }

    /* 제목 한 줄로 못 박기 */
    .stApp h1 {
        font-size: 2rem !important;
        line-height: 1.25 !important;
        white-space: nowrap !important;
        overflow: hidden;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stCaptionContainer"], .stCaption {
        margin-bottom: 1.4rem !important;
    }

    .stProgress {
        margin-top: 1.2rem !important;
        margin-bottom: 2.2rem !important;
    }

    .stApp h3 {
        margin-top: 0.4rem !important;
        margin-bottom: 1.4rem !important;
        line-height: 1.5 !important;
    }

    /* 라디오 옵션 따닥따닥 안 붙게 띄움 */
    div[role="radiogroup"] {
        gap: 0.7rem !important;
        padding-top: 0.3rem;
    }
    div[role="radiogroup"] > label {
        padding: 0.35rem 0.2rem !important;
        line-height: 1.5 !important;
    }
    .stRadio {
        margin-bottom: 1.5rem !important;
    }

    /* 군용 패치 느낌 버튼 */
    .stButton > button {
        background-color: #2c3a22;
        color: #f0f3da;
        border: 1px solid #6a7d4a;
        border-radius: 6px;
        padding: 0.55rem 1.2rem;
    }
    .stButton > button:hover {
        background-color: #3d5230;
        border-color: #a3b97a;
    }

    .stRadio label, .stTextInput label {
        color: #e6ecd6 !important;
    }

    .stApp p {
        line-height: 1.7;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)



# 세션 상태 초기화
# Streamlit 은 버튼 누를 때마다 코드를 다시 돌려서
# 일반 변수에 저장하면 사라짐. session_state 에 넣어야 살아있음.

def init_session():
    if "page" not in st.session_state:
        st.session_state["page"] = "welcome"
    if "login_user" not in st.session_state:
        st.session_state["login_user"] = None
    if "q_index" not in st.session_state:
        st.session_state["q_index"] = 0
    if "answers" not in st.session_state:
        # 문항 개수만큼 None 으로 채워둠 (B3 - 이전 문항 기능 때문에 리스트로)
        st.session_state["answers"] = [None] * len(QUESTIONS)
    if "final_type" not in st.session_state:
        st.session_state["final_type"] = None


def goto(page_name):
    # 페이지 바꾸고 새로고침
    st.session_state["page"] = page_name
    st.rerun()


def reset_quiz():
    st.session_state["q_index"] = 0
    st.session_state["answers"] = [None] * len(QUESTIONS)
    st.session_state["final_type"] = None



# 페이지 - 처음 화면

def page_welcome():
    st.title("🛡️ 나는 어떤 무기체계 개발자일까?")
    st.caption("만약 내가 무기체계 개발자라면?")

    st.write("")
    st.write(
        "내 손으로 만든 소프트웨어로 나라를 지킬 수 있다면, "
        "그를 바탕으로 한 자긍심은 어마어마합니다. "
        "개발 직무를 희망하지만, 어떤 분야의 개발이 적성에 맞는지 고민하는 학우들을 보며, "
        "같은 길을 걷자고 설득함과 동시에 조금이나마 방향을 잡는데 도움이 되고자 이 앱을 만들었습니다."
    )

    st.markdown("---")
    st.markdown("**제작:** 광운대학교 정보융합학부 2학년 유명현 (학번 2023204088)")
    st.markdown("**과목:** 오픈소스소프트웨어실습 / 박규동 교수님")

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("로그인 / 시작하기", use_container_width=True):
            goto("login")
    with col2:
        if st.button("회원가입", use_container_width=True):
            goto("signup")



# 페이지 - 로그인

def page_login():
    st.title("로그인")
    users = load_users()

    # st.form 안에 넣으면 엔터 한 번에 제출됨
    with st.form("login_form"):
        u = st.text_input("아이디")
        p = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")

    if submitted:
        if u == "" or p == "":
            st.warning("아이디/비밀번호를 입력해주세요.")
        elif u in users and users[u] == hash_password(p):
            # 로그인 성공
            st.session_state["login_user"] = u
            st.success(u + " 님 환영합니다.")
            reset_quiz()
            goto("quiz")
        else:
            st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

    st.markdown("---")
    st.write("아직 계정이 없으신가요?")
    if st.button("회원가입 하러가기"):
        goto("signup")
    if st.button("← 처음 화면으로"):
        goto("welcome")



# 페이지 - 회원가입
# 검증 5종 세트 (빈값/형식/길이/일치/중복)
# 처음엔 함수로 분리했었는데 그냥 여기 다 적는 게 보기 편해서 풀었음

def page_signup():
    st.title("회원가입")
    st.caption("아이디는 영문/숫자만 가능, 비밀번호는 최소 4자 이상")

    users = load_users()

    with st.form("signup_form"):
        new_id = st.text_input("아이디 (영문/숫자)")
        new_pw = st.text_input("비밀번호", type="password")
        new_pw2 = st.text_input("비밀번호 확인", type="password")
        submitted = st.form_submit_button("가입하기")

    if submitted:
        # 1) 빈값 제출 방지
        if new_id == "" or new_pw == "" or new_pw2 == "":
            st.error("모든 항목을 입력해주세요.")
        # 2) 아이디 형식 (영문+숫자만)
        elif not ID_REGEX.match(new_id):
            st.error("아이디는 영문과 숫자만 사용할 수 있어요.")
        # 3) 비밀번호 길이
        elif len(new_pw) < MIN_PW_LEN:
            st.error("비밀번호는 최소 " + str(MIN_PW_LEN) + "자 이상이어야 해요.")
        # 4) 비밀번호 확인
        elif new_pw != new_pw2:
            st.error("비밀번호가 서로 일치하지 않아요.")
        # 5) 아이디 중복
        elif new_id in users:
            st.error("이미 존재하는 아이디예요.")
        else:
            # 다 통과 → 해시해서 저장
            users[new_id] = hash_password(new_pw)
            save_users(users)
            st.success("가입 완료! 이제 로그인 해주세요.")
            goto("login")

    if st.button("← 로그인 화면으로"):
        goto("login")


# 페이지 - 퀴즈
# 처음엔 카운터로 점수만 쌓았는데 '이전 문항' 기능 때문에
# 답을 리스트로 저장하는 구조로 바꿈

def page_quiz():
    questions = get_questions()
    idx = st.session_state["q_index"]
    answers = st.session_state["answers"]

    if st.session_state["login_user"] is not None:
        user = st.session_state["login_user"]
    else:
        user = "guest"

    st.title("퀴즈")
    st.caption(user + " 님 - 총 " + str(len(questions)) + "문항")

    st.write("")

    # 진행률 (n/총)
    progress_value = (idx + 1) / len(questions)
    progress_text = "진행 " + str(idx + 1) + " / " + str(len(questions))
    st.progress(progress_value, text=progress_text)

    # 현재 문항
    q = questions[idx]
    st.subheader("Q" + str(idx + 1) + ". " + q["q"])

    # 보기 텍스트만 뽑아서 라디오에 넣기
    options_text = []
    for opt in q["options"]:
        options_text.append(opt[0])

    # 이전에 골랐던 답이 있으면 그 값을 기본 선택으로
    if answers[idx] is not None:
        default_index = answers[idx]
    else:
        default_index = 0

    chosen = st.radio(
        "보기",
        options=list(range(len(options_text))),
        format_func=lambda i: options_text[i],
        index=default_index,
        key="q_" + str(idx),
    )

    st.write("")

    # 버튼 3개 - 이전 / 처음부터 / 다음(또는 결과)
    col_prev, col_mid, col_next = st.columns([1, 1, 1])

    with col_prev:
        # 1번 문항이면 이전 버튼 비활성화
        prev_disabled = (idx == 0)
        if st.button("← 이전 문항", disabled=prev_disabled, use_container_width=True):
            answers[idx] = chosen
            st.session_state["q_index"] = idx - 1
            st.rerun()

    with col_mid:
        if st.button("처음부터", use_container_width=True):
            reset_quiz()
            st.rerun()

    with col_next:
        is_last = (idx == len(questions) - 1)
        if is_last:
            next_label = "결과 보기 →"
        else:
            next_label = "다음 문항 →"

        if st.button(next_label, use_container_width=True):
            answers[idx] = chosen
            if is_last:
                final = calc_result(answers, questions)
                st.session_state["final_type"] = final
                add_stat(final)
                goto("result")
            else:
                st.session_state["q_index"] = idx + 1
                st.rerun()


def calc_result(answers, questions):
    # 답변 리스트 보고 가장 많이 고른 유형 찾기
    # 처음엔 collections.Counter 쓰려다가 그냥 직접 셈
    score = {"guided": 0, "ew": 0, "fcs": 0, "embedded": 0}
    for i in range(len(answers)):
        if answers[i] is None:
            continue
        type_key = questions[i]["options"][answers[i]][1]
        score[type_key] = score[type_key] + 1

    # 최댓값 유형 찾기 (max() 한 줄로 되긴 하는데 헷갈려서 풀어서)
    final_type = "guided"
    max_count = -1
    for k in score:
        if score[k] > max_count:
            max_count = score[k]
            final_type = k
    return final_type



# 페이지 - 결과
# A1 레이더 / A2 공부과목 / C2 통계 한 페이지에 다 들어감

def page_result():
    final_type = st.session_state["final_type"]
    if final_type is None:
        st.warning("아직 퀴즈를 풀지 않았어요.")
        if st.button("퀴즈 풀러가기"):
            goto("quiz")
        return

    results = get_results()
    info = results[final_type]

    st.title(info["emoji"] + "  " + info["title"])
    st.write("")
    st.markdown("**성향**  ·  " + info["personality"])
    st.markdown("**역할**  ·  " + info["role"])

    # ---- A1 레이더 차트 ----
    st.write("")
    st.subheader("📊 유형별 점수 (Radar)")
    score_dict = score_by_type(st.session_state["answers"], get_questions())
    fig = build_radar(score_dict)
    st.plotly_chart(fig, use_container_width=True)

    # 강점
    st.write("")
    st.subheader("🛠 강점")
    for s in info["strengths"]:
        st.write("- " + s)

    # ---- A2 공부 과목/분야 ----
    st.write("")
    st.subheader("📚 공부해야 할 과목 / 분야")
    col_c, col_f = st.columns(2)
    with col_c:
        st.markdown("**광운대 / 일반 학부 과목**")
        for c in info["courses"]:
            st.write("- " + c)
    with col_f:
        st.markdown("**핵심 공부 분야 / 키워드**")
        for f in info["fields"]:
            st.write("- " + f)

    # 진로
    st.write("")
    st.subheader("🚀 어울리는 진로")
    for category in info["careers"]:
        places = info["careers"][category]
        st.markdown("**" + category + "**")
        for p in places:
            st.write("- " + p)

    st.markdown("---")

    # ---- C2 전체 사용자 통계 ----
    st.subheader("👥 전체 사용자 결과 분포")
    stats = load_stats()
    show_stats_chart(stats, final_type)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("다시 풀어보기", use_container_width=True):
            reset_quiz()
            goto("quiz")
    with col_b:
        if st.button("로그아웃", use_container_width=True):
            st.session_state["login_user"] = None
            reset_quiz()
            goto("welcome")


# 차트 만드는 함수들

def score_by_type(answers, questions):
    # 결과 페이지 레이더 그릴 때 쓸 점수 - 위 calc_result 랑 거의 같음
    # TODO: 나중에 합칠 수 있을 듯
    score = {"guided": 0, "ew": 0, "fcs": 0, "embedded": 0}
    for i in range(len(answers)):
        if answers[i] is None:
            continue
        t = questions[i]["options"][answers[i]][1]
        score[t] = score[t] + 1
    return score


def build_radar(score_dict):
    # plotly Scatterpolar 로 레이더 그리기
    # 처음에 도형이 한쪽 안 닫히고 'ㄴ' 모양으로 떠서 한참 헤맴
    # → 마지막 점을 다시 처음 점으로 한 번 더 넣어줘야 닫힌다고 함
    keys = ["guided", "ew", "fcs", "embedded"]
    labels = []
    values = []
    for k in keys:
        labels.append(TYPE_LABELS[k])
        values.append(score_dict[k])

    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        name="내 점수",
        line=dict(color="#a3b97a"),
        fillcolor="rgba(163, 185, 122, 0.45)",
    ))

    # 축 범위 - 0표인 유형이 있을수도 있어서 max+1
    if max(values) > 0:
        max_v = max(values)
    else:
        max_v = 1

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, max_v + 1], color="#e6ecd6"),
            angularaxis=dict(color="#e6ecd6"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e6ecd6"),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
    )
    return fig


def show_stats_chart(stats, highlight):
    # C2 - 전체 사용자 결과 막대 그래프
    # 내 결과 막대만 색 다르게 칠해서 강조
    keys = ["guided", "ew", "fcs", "embedded"]
    labels = []
    values = []
    colors = []
    for k in keys:
        labels.append(TYPE_LABELS[k])
        values.append(stats[k])
        if k == highlight:
            colors.append("#d6a86a")
        else:
            colors.append("#6a7d4a")

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        text=values, textposition="outside",
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e6ecd6"),
        yaxis=dict(title="응답 수", gridcolor="rgba(255,255,255,0.1)"),
        xaxis=dict(title=""),
        margin=dict(l=20, r=20, t=20, b=20),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)
    total = sum(values)
    st.caption("누적 응답 " + str(total) + "건 - 내 결과는 강조색으로 표시")



# 메인 - 페이지 전환
# 처음엔 PAGES dict 로 dispatch 하는 패턴 썼는데
# 너무 헷갈려서 그냥 if/elif 로 풀어버림

def main():
    init_session()
    inject_global_css()

    page = st.session_state["page"]
    if page == "welcome":
        page_welcome()
    elif page == "login":
        page_login()
    elif page == "signup":
        page_signup()
    elif page == "quiz":
        page_quiz()
    elif page == "result":
        page_result()
    else:
        # 혹시 모를 fallback
        page_welcome()


if __name__ == "__main__":
    main()
