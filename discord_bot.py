"""
공모주 정보 Discord 봇

매일 오전 9시에 공모주 정보를 자동으로 전송하고,
사용자 커맨드를 통해 공모주 정보를 조회할 수 있습니다.
"""

import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz
from ipo_crawler import FinutsIPOCrawler
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 설정
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))
TIMEZONE = pytz.timezone('Asia/Seoul')

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.presences = False  # 불필요한 Intent 비활성화
intents.typing = False
intents.members = False
bot = commands.Bot(command_prefix='!', intents=intents)

# 크롤러 인스턴스
crawler = FinutsIPOCrawler()


@bot.event
async def on_ready():
    """봇이 준비되었을 때 실행"""
    print(f'✅ {bot.user} 봇이 시작되었습니다!')
    print(f'📌 채널 ID: {CHANNEL_ID}')
    
    # 슬래시 커맨드 동기화
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)}개의 슬래시 커맨드가 동기화되었습니다.')
    except Exception as e:
        print(f'❌ 슬래시 커맨드 동기화 실패: {e}')
    
    # 자동 알림 시작
    if not daily_ipo_notification.is_running():
        daily_ipo_notification.start()
        print('✅ 자동 알림 스케줄러가 시작되었습니다.')


@tasks.loop(hours=24)
async def daily_ipo_notification():
    """매일 오전 9시에 공모주 정보 전송"""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f'❌ 채널을 찾을 수 없습니다: {CHANNEL_ID}')
        return
    
    # 오늘 날짜
    today = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    
    # 공모주 정보 가져오기
    message = crawler.get_ipo_message(today)
    
    # 메시지 전송
    embed = discord.Embed(
        title="📊 오늘의 공모주 정보",
        description=message,
        color=discord.Color.blue(),
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_footer(text="피너츠 공모주 알리미")
    
    await channel.send(embed=embed)
    print(f'✅ {today} 공모주 정보 전송 완료')


@daily_ipo_notification.before_loop
async def before_daily_notification():
    """스케줄러 시작 전 대기 - 매일 오전 9시까지 대기"""
    await bot.wait_until_ready()
    
    now = datetime.now(TIMEZONE)
    target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # 이미 9시가 지났으면 다음날 9시로 설정
    if now >= target_time:
        target_time += timedelta(days=1)
    
    wait_seconds = (target_time - now).total_seconds()
    print(f'⏰ {wait_seconds / 3600:.1f}시간 후 자동 알림이 시작됩니다.')
    await discord.utils.sleep_until(target_time)


# ========== 슬래시 커맨드 ==========

@bot.tree.command(name="공모주", description="특정 날짜의 공모주 정보를 조회합니다")
async def ipo_info(interaction: discord.Interaction, 날짜: str = None):
    """
    공모주 정보 조회
    
    Args:
        날짜: YYYY-MM-DD 형식 또는 '오늘', '내일' (기본값: 오늘)
    """
    await interaction.response.defer()
    
    # 날짜 처리
    if 날짜 is None or 날짜 == '오늘':
        target_date = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    elif 날짜 == '내일':
        target_date = (datetime.now(TIMEZONE) + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        target_date = 날짜
    
    # 공모주 정보 가져오기
    message = crawler.get_ipo_message(target_date)
    
    # 응답 전송
    embed = discord.Embed(
        title="📊 공모주 정보",
        description=message,
        color=discord.Color.green(),
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_footer(text="피너츠 공모주 알리미")
    
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="검색", description="종목명으로 공모주를 검색합니다")
async def search_ipo(interaction: discord.Interaction, 종목명: str):
    """
    종목명으로 공모주 검색
    
    Args:
        종목명: 검색할 공모주 종목명
    """
    await interaction.response.defer()
    
    # 모든 데이터 가져오기
    all_data = crawler.fetch_all_ipo_data()
    
    if not all_data:
        await interaction.followup.send("❌ 데이터를 가져올 수 없습니다.")
        return
    
    # 종목명으로 검색
    results = [item for item in all_data if 종목명 in item.get('ENT_NM', '')]
    
    if not results:
        await interaction.followup.send(f"❌ '{종목명}'에 대한 검색 결과가 없습니다.")
        return
    
    # 최대 5개까지만 표시
    results = results[:5]
    
    message = ""
    for idx, ipo in enumerate(results, 1):
        ent_nm = ipo.get('ENT_NM', 'N/A')
        bgng_ymd = ipo.get('BGNG_YMD', 'N/A')
        end_ymd = ipo.get('END_YMD', 'N/A')
        ipo_date = ipo.get('IPO_DATE', 'N/A')
        pss_prc = ipo.get('PSS_PRC', '')
        
        if pss_prc and pss_prc != '':
            pss_prc_formatted = f"{int(pss_prc):,}원"
        else:
            pss_prc_formatted = "미정"
        
        message += f"\n**{idx}. {ent_nm}**\n"
        message += f"공모가: {pss_prc_formatted}\n"
        message += f"청약기간: {bgng_ymd} ~ {end_ymd}\n"
        message += f"상장일: {ipo_date}\n"
    
    embed = discord.Embed(
        title=f"🔍 '{종목명}' 검색 결과",
        description=message,
        color=discord.Color.purple(),
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_footer(text="피너츠 공모주 알리미")
    
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="도움말", description="봇 사용법을 확인합니다")
async def help_command(interaction: discord.Interaction):
    """봇 사용법"""
    help_text = """
**📌 사용 가능한 커맨드**

`/공모주` - 오늘의 공모주 정보
`/공모주 내일` - 내일의 공모주 정보
`/공모주 2025-10-28` - 특정 날짜의 공모주 정보

`/검색 명인제약` - 종목명으로 검색

`/도움말` - 이 도움말 표시

**⏰ 자동 알림**
매일 오전 9시에 공모주 정보가 자동으로 전송됩니다.
    """
    
    embed = discord.Embed(
        title="📖 공모주 알리미 봇 사용법",
        description=help_text,
        color=discord.Color.gold(),
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_footer(text="피너츠 공모주 알리미")
    
    await interaction.followup.send(embed=embed, ephemeral=True)


# ========== 레거시 명령어 (! 접두사) ==========

@bot.command(name='공모주')
async def ipo_legacy(ctx, 날짜: str = None):
    """레거시 명령어: !공모주"""
    if 날짜 is None or 날짜 == '오늘':
        target_date = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    elif 날짜 == '내일':
        target_date = (datetime.now(TIMEZONE) + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        target_date = 날짜
    
    message = crawler.get_ipo_message(target_date)
    
    embed = discord.Embed(
        title="📊 공모주 정보",
        description=message,
        color=discord.Color.green(),
        timestamp=datetime.now(TIMEZONE)
    )
    embed.set_footer(text="피너츠 공모주 알리미")
    
    await ctx.send(embed=embed)


# ========== 에러 핸들링 ==========

@bot.event
async def on_command_error(ctx, error):
    """명령어 에러 처리"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ 알 수 없는 명령어입니다. `/도움말`을 입력해보세요.")
    else:
        print(f'❌ 에러 발생: {error}')
        await ctx.send(f"❌ 오류가 발생했습니다: {error}")


# ========== 봇 실행 ==========

def main():
    """봇 실행"""
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN이 설정되지 않았습니다.")
        print("❌ .env 파일을 확인해주세요.")
        return
    
    if CHANNEL_ID == 0:
        print("⚠️  CHANNEL_ID가 설정되지 않았습니다.")
        print("⚠️  자동 알림이 작동하지 않습니다.")
    
    # 재시도 로직
    max_retries = 5
    retry_delay = 10  # 초
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 봇 시작 시도 중... ({attempt + 1}/{max_retries})")
            bot.run(DISCORD_TOKEN)
            break  # 성공하면 루프 탈출
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 봇 실행 실패 (시도 {attempt + 1}/{max_retries}): {error_msg}")
            
            # Rate limit 에러인 경우
            if "429" in error_msg or "rate limit" in error_msg.lower():
                if attempt < max_retries - 1:
                    import time
                    wait_time = retry_delay * (attempt + 1)  # 지수 백오프
                    print(f"⏳ {wait_time}초 후 재시도합니다...")
                    time.sleep(wait_time)
                else:
                    print("❌ 최대 재시도 횟수를 초과했습니다.")
                    print("💡 Render 서비스를 재시작하거나 몇 분 후 다시 시도해주세요.")
            else:
                # 다른 에러는 즉시 종료
                break


if __name__ == "__main__":
    main()
