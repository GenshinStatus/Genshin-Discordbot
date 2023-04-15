import datetime
import re
import googleapiclient.discovery
import google.auth
import os


# ①Google APIの準備をする
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = os.getenv('CALENDAR_ID')
JSON_PATH = os.getenv('CALENDAR_JSON_PATH')

# Googleの認証情報をファイルから読み込む
gapi_creds = google.auth.load_credentials_from_file(
    JSON_PATH, SCOPES)[0]
# APIと対話するためのResourceオブジェクトを構築する
service = googleapiclient.discovery.build(
    'calendar', 'v3', credentials=gapi_creds)


def get():
    """
    カレンダーを取得してdictで返します。
    {"stert":date,"end":date,"name":name}
    で返します。
    """
    # ②Googleカレンダーからイベントを取得する
    # 現在時刻を世界協定時刻（UTC）のISOフォーマットで取得する
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    # 直近3件のイベントを取得する
    event_list = service.events().list(
        calendarId=CALENDAR_ID, timeMin=now,
        maxResults=20, singleEvents=True,
        orderBy='startTime').execute()

    # ③イベントの開始時刻、終了時刻、概要を取得する
    events = event_list.get('items', [])
    formatted_events = [(event['start'].get('dateTime', event['start'].get('date')),  # start time or day
                        event['end'].get('dateTime', event['end'].get(
                            'date')),  # end time or day
                        event['summary'], event['description']) for event in events]

    # ④出力テキストを生成する
    response = list()
    # データの正規化をする
    for event in formatted_events:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', event[0]):
            start_date = datetime.datetime.strptime(event[1], '%Y-%m-%d')
            response.append({"start": start_date, "end": "allday",
                            "name": event[2], "description": event[3]})
        # For all day events
        else:
            start_time = datetime.datetime.strptime(
                event[0], '%Y-%m-%dT%H:%M:%S+09:00')
            end_time = datetime.datetime.strptime(
                event[1], '%Y-%m-%dT%H:%M:%S+09:00')
            response.append({"start": start_time, "end": end_time,
                            "name": event[2], "description": event[3]})
    return response


def set(name: str, description: str, start_month: int, start_day: int, end_month: int, end_day: int):
    """
    カレンダーに書き込んでイベント名を返します。
    """
    # ②予定を書き込む
    # 書き込む予定情報を用意する
    body = {
        # 予定のタイトル
        'summary': name,
        'description': description,
        # 予定の開始時刻
        'start': {
            'dateTime': datetime.datetime(2022, start_month, start_day, 00, 00).isoformat(),
            'timeZone': 'Japan'
        },
        # 予定の終了時刻
        'end': {
            'dateTime': datetime.datetime(2022, end_month, end_day, 00, 00).isoformat(),
            'timeZone': 'Japan'
        },
    }
    # 用意した予定を登録する
    event = service.events().insert(calendarId=CALENDAR_ID, body=body).execute()
    return name
