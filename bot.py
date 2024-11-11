import discord
from discord.ext import commands
import youtube_dl
import json

# config.json 파일에서 설정을 불러오는 함수
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Intents 설정
intents = discord.Intents.default()
intents.voice_states = True

# 설정 불러오기
config = load_config()

# 봇의 프리픽스 및 intents 설정
bot = commands.Bot(command_prefix='!', intents=intents)

# youtube_dl 설정
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'type': 'audio/ffmpeg',
        'options': {'-vn': None},
    }],
}

# 봇이 준비되었을 때의 이벤트
@bot.event
async def on_ready():
    print(f'{bot.user.name}로 로그인되었습니다.')
    # 프로필 상태 메시지 설정
    await bot.change_presence(activity=discord.Game(name="개발"))

@bot.command()
async def status(ctx):
    """봇의 설정 상태를 표시합니다."""
    status_message = (
        f"**봇 설정 상태**\n"
        f"디스코드 봇 토큰: {'설정됨' if config['TOKEN'] else '설정되지 않음'}\n"
        f"유튜브 API 키: {'설정됨' if config['YOUTUBE_API_KEY'] else '설정되지 않음'}\n"
        f"채널 ID: {'설정됨' if config['CHANNEL_ID'] else '설정되지 않음'}"
    )
    await ctx.send(status_message)

# 음악 재생 명령어
@bot.command()
async def join(ctx):
    """음성 채널에 봇을 초대합니다."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"{channel.name}에 연결되었습니다.")
    else:
        await ctx.send("먼저 음성 채널에 들어가세요.")

@bot.command()
async def leave(ctx):
    """봇을 음성 채널에서 나가게 합니다."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("음성 채널에서 나갔습니다.")
    else:
        await ctx.send("봇이 음성 채널에 없습니다.")

@bot.command()
async def play(ctx, url):
    """유튜브 링크를 입력하여 음악을 재생합니다."""
    if not ctx.voice_client:
        await ctx.send("먼저 음성 채널에 들어가세요.")
        return

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url = info['formats'][0]['url']
        ctx.voice_client.stop()
        ctx.voice_client.play(discord.FFmpegPCMAudio(url))

    await ctx.send(f"재생 중: {info['title']}")

@bot.command()
async def stop(ctx):
    """음악 재생을 중지합니다."""
    ctx.voice_client.stop()
    await ctx.send("재생이 중지되었습니다.")

# 봇 실행
bot.run(config['TOKEN'])
