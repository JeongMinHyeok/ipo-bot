# 🌩️ Oracle Cloud 배포 가이드

## 1. Oracle Cloud 계정 및 VM 생성

### 계정 생성
1. https://www.oracle.com/cloud/free/ 접속
2. "Start for free" 클릭
3. 계정 정보 입력 (신용카드 필요, 청구 안 됨)

### VM 인스턴스 생성
1. Oracle Cloud 콘솔 → Compute → Instances
2. Create Instance:
   - **Name**: ipo-discord-bot
   - **Image**: Ubuntu 22.04
   - **Shape**: VM.Standard.A1.Flex (ARM, 무료)
     - OCPU: 2-4
     - Memory: 12-24GB
   - **SSH Keys**: Generate 클릭 → 키 다운로드
3. Create 클릭

## 2. SSH 접속

### Windows
```powershell
ssh -i C:\path\to\ssh-key-*.key ubuntu@<PUBLIC_IP>
```

### Mac/Linux
```bash
chmod 400 ~/Downloads/ssh-key-*.key
ssh -i ~/Downloads/ssh-key-*.key ubuntu@<PUBLIC_IP>
```

**PUBLIC_IP**: Oracle Cloud 콘솔의 Instance Details에서 확인

## 3. 서버 초기 설정

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Python 및 필수 패키지 설치
sudo apt install -y python3 python3-pip git

# Git 설정
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## 4. 봇 코드 배포

```bash
# 저장소 클론
cd ~
git clone https://github.com/JeongMinHyeok/ipo-bot.git
cd ipo-bot

# 의존성 설치
pip3 install -r requirements.txt
```

## 5. 환경 변수 설정

```bash
# .env 파일 생성
nano .env
```

다음 내용 입력:
```env
DISCORD_TOKEN=your_discord_bot_token_here
CHANNEL_ID=your_channel_id_here
```

저장: `Ctrl+O` → `Enter` → `Ctrl+X`

## 6. systemd 서비스 생성 (자동 시작)

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/ipo-bot.service
```

다음 내용 입력:
```ini
[Unit]
Description=IPO Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ipo-bot
ExecStart=/usr/bin/python3 /home/ubuntu/ipo-bot/discord_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

저장: `Ctrl+O` → `Enter` → `Ctrl+X`

## 7. 서비스 시작

```bash
# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable ipo-bot
sudo systemctl start ipo-bot

# 상태 확인
sudo systemctl status ipo-bot

# 로그 확인
sudo journalctl -u ipo-bot -f
```

## 8. 유용한 명령어

### 봇 관리
```bash
# 봇 시작
sudo systemctl start ipo-bot

# 봇 중지
sudo systemctl stop ipo-bot

# 봇 재시작
sudo systemctl restart ipo-bot

# 봇 상태 확인
sudo systemctl status ipo-bot

# 실시간 로그 보기
sudo journalctl -u ipo-bot -f

# 최근 100줄 로그
sudo journalctl -u ipo-bot -n 100
```

### 코드 업데이트
```bash
cd ~/ipo-bot
git pull
sudo systemctl restart ipo-bot
```

### 서버 재부팅 시
봇이 자동으로 시작됩니다! (systemd 덕분)

## 9. 문제 해결

### 봇이 시작 안 될 때
```bash
# 로그 확인
sudo journalctl -u ipo-bot -n 50

# 수동 실행 테스트
cd ~/ipo-bot
python3 discord_bot.py
```

### Python 패키지 에러
```bash
cd ~/ipo-bot
pip3 install -r requirements.txt --upgrade
sudo systemctl restart ipo-bot
```

### 환경 변수 확인
```bash
cat ~/ipo-bot/.env
```

## 10. 보안 팁

1. ✅ `.env` 파일 권한 설정:
   ```bash
   chmod 600 ~/ipo-bot/.env
   ```

2. ✅ 정기적으로 시스템 업데이트:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. ✅ 사용하지 않는 포트 닫기 (Oracle Cloud 방화벽에서)

## 11. 비용

- ✅ **완전 무료**
- ✅ Ampere (ARM) 인스턴스는 영구 무료
- ✅ 아웃바운드 트래픽 10TB/월 무료

## 문제 발생 시

1. 로그 확인: `sudo journalctl -u ipo-bot -f`
2. 봇 재시작: `sudo systemctl restart ipo-bot`
3. GitHub 이슈 등록
