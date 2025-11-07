import os
import json
import random
from slack_sdk import WebClient
from datetime import datetime

SLACK_TOKEN = os.environ['SLACK_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']

client = WebClient(token=SLACK_TOKEN)

def get_week_number():
    """현재 주 번호"""
    return datetime.now().strftime("%Y_W%U")

def load_winners():
    """이번 주 당첨자 로드"""
    try:
        with open('/tmp/winners.json', 'r') as f:
            return json.load(f)
    except:
        return {"week": get_week_number(), "winners": []}

def save_winner(user_id):
    """당첨자 저장"""
    data = load_winners()
    current_week = get_week_number()
    
    if data["week"] != current_week:
        data = {"week": current_week, "winners": []}
    
    data["winners"].append(user_id)
    
    with open('/tmp/winners.json', 'w') as f:
        json.dump(data, f)

def draw_lottery():
    """11:00 실행 - 자동 추첨"""
    
    # 10:30 메시지 ID 읽기
    try:
        with open('/tmp/message_ts.txt', 'r') as f:
            message_ts = f.read().strip()
    except:
        print("오늘 메시지를 찾을 수 없습니다")
        return
    
    # 1. 이모지 반응한 사용자 가져오기
    excluded_users = set()
    try:
        reactions = client.reactions_get(
            channel=CHANNEL_ID,
            timestamp=message_ts
        )
        
        if 'reactions' in reactions['message']:
            for reaction in reactions['message']['reactions']:
                if reaction['name'] in ['x', 'no_entry_sign', 'hand']:  # ❌, 🚫, ✋ 등
                    excluded_users.update(reaction['users'])
    except:
        pass
    
    # 2. 채널 멤버 가져오기
    members = client.conversations_members(channel=CHANNEL_ID)['members']
    
    # 3. 봇 제외 (봇은 U로 시작하지 않음)
    members = [m for m in members if m.startswith('U')]
    
    # 4. 이번 주 당첨자 가져오기
    winners_data = load_winners()
    weekly_winners = winners_data['winners'] if winners_data['week'] == get_week_number() else []
    
    # 5. 제외 대상 합치기
    excluded_users.update(weekly_winners)
    
    # 6. 추첨 가능한 사람 필터링
    eligible = [m for m in members if m not in excluded_users]
    
    if eligible:
        winner = random.choice(eligible)
        save_winner(winner)
        
        # 7. 결과 발표
        client.chat_postMessage(
            channel=CHANNEL_ID,
            thread_ts=message_ts,
            text=f"🎉 오늘의 점심 당번: <@{winner}>님!\n맛있는 메뉴 추천 부탁드려요~ 🍜"
        )
        print(f"당첨자: {winner}")
    else:
        client.chat_postMessage(
            channel=CHANNEL_ID,
            thread_ts=message_ts,
            text="😅 오늘은 선택 가능한 사람이 없네요! (모두 당첨되었거나 불참)"
        )
        print("추첨 가능한 사람이 없음")

if __name__ == "__main__":
    draw_lottery()
```

"Commit new file" 클릭

3. **requirements.txt 생성**
   - "Add file" → "Create new file"
   - 파일명: `requirements.txt`
```
slack-sdk==3.23.0
