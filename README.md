# 📊 공모주 정보 Discord 봇

공모주 정보를 자동으로 Discord 채널에 알려주는 봇입니다.

## ✨ 주요 기능

- 🕐 매일 오전 9시 자동 알림
- 📅 특정 날짜의 공모주 정보 조회
- 🔍 종목명으로 공모주 검색
- 📈 청약/상장 정보 구분 표시

## 🚀 시작하기

### 1. Discord Bot 생성

1. [Discord Developer Portal](https://discord.com/developers/applications) 접속
2. "New Application" 클릭하여 애플리케이션 생성
3. 왼쪽 메뉴에서 "Bot" 클릭 → "Add Bot" 클릭
4. "Reset Token" 클릭하여 토큰 복사 (나중에 사용)
5. "Privileged Gateway Intents" 섹션:
   - ✅ **MESSAGE CONTENT INTENT** 활성화

### 2. 봇을 서버에 초대

1. 왼쪽 메뉴 "OAuth2" → "URL Generator" 클릭
2. **SCOPES** 선택:
   - ✅ `bot`
   - ✅ `applications.commands`
3. **BOT PERMISSIONS** 선택:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
4. 생성된 URL을 복사하여 브라우저에서 열고 서버에 초대

### 3. 채널 ID 확인

1. Discord 설정 → 고급 → **개발자 모드** 활성화
2. 메시지를 받을 채널 우클릭 → **ID 복사**

### 4. 환경 설정

`.env.example` 파일을 `.env`로 복사하고 설정:

```bash
cp .env.example .env
```

`.env` 파일 편집:

```env
DISCORD_TOKEN=여기에_봇_토큰_입력
CHANNEL_ID=여기에_채널_ID_입력
```

### 5. 로컬에서 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 봇 실행
python discord_bot.py
```

## 📦 Render.com 배포

### 1. GitHub에 푸시

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/ipo-bot.git
git push -u origin main
```

### 2. Render 설정

1. [Render.com](https://render.com) 접속 및 가입
2. "New +" → "Web Service" 클릭
3. GitHub 저장소 연결
4. 설정:
   - **Name**: ipo-bot (원하는 이름)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python discord_bot.py`
   - **Plan**: Free

### 3. 환경 변수 설정

Render 대시보드에서 "Environment" 탭:

```
DISCORD_TOKEN = your_token_here
CHANNEL_ID = your_channel_id_here
```

### 4. 배포

"Create Web Service" 클릭하면 자동 배포됩니다.

## 🤖 봇 사용법

### 슬래시 커맨드

- `/공모주` - 오늘의 공모주 정보
- `/공모주 내일` - 내일의 공모주 정보
- `/공모주 2025-10-28` - 특정 날짜의 공모주 정보
- `/검색 명인제약` - 종목명으로 검색
- `/도움말` - 사용법 표시

### 레거시 커맨드 (옵션)

- `!공모주` - 오늘의 공모주 정보
- `!공모주 내일` - 내일의 공모주 정보
- `!공모주 2025-10-28` - 특정 날짜의 공모주 정보

### 자동 알림

매일 오전 9시(KST)에 자동으로 공모주 정보가 전송됩니다.

## 📁 프로젝트 구조

```
ipo_bot/
├── discord_bot.py          # Discord 봇 메인 파일
├── ipo_crawler.py          # 데이터 수집 모듈
├── requirements.txt        # 의존성 패키지
├── .env                    # 환경 변수 (git에 포함 안 됨)
├── .env.example           # 환경 변수 예시
├── .gitignore             # Git 제외 파일
└── README.md              # 이 파일
```

## 🛠️ 기술 스택

- Python 3.9+
- discord.py - Discord 봇 라이브러리
- requests - HTTP 요청
- python-dotenv - 환경 변수 관리
- pytz - 시간대 처리

## ⚠️ 주의사항

- Discord 봇 토큰은 절대 공개하지 마세요
- `.env` 파일은 Git에 커밋하지 마세요
- Render 무료 티어는 15분 비활성시 sleep 됩니다
