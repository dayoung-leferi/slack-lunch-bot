import os
import json
from slack_sdk import WebClient
from datetime import datetime

# 환경 변수에서 토큰과 채널 ID 가져오기
SLACK_TOKEN = os.environ['SLACK_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']

client = WebClient(token=SLACK_TOKEN)

def start_lottery():
    """10:30 실행 - 추첨 시작 메시지"""
    result = client.chat_postMessage(
        channel=CHANNEL_ID,
        text="🍽️ 오늘의 점심 당번 추첨을 시작합니다!\n불참하실 분은 11시까지 ❌ 이모지를 달아주세요."
    )
    
    # 메시지 ID를 파일로 저장 (11시에 사용)
    with open('/tmp/message_ts.txt', 'w') as f:
        f.write(result['ts'])
    
    print(f"추첨 시작! 메시지 ID: {result['ts']}")

if __name__ == "__main__":
    start_lottery()
