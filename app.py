import os
import google.generativeai as genai
from flask import Flask, request, Response

genai.configure(api_key="AIzaSyCTsATxKCBR2EelzU8qzQZ9aOIT6QXLM8U")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

# מילון לשמירת היסטוריית השיחות לפי מספר טלפון או CallId
chat_sessions = {}

@app.route('/', methods=['GET', 'POST'])
def gemini_ivr():
    call_id = request.args.get('ApiCallId', 'default')

    # 1. כניסה לשלוחה - הצגת הודעת פתיחה
    if request.method == 'GET':
        text = "say=שלום, אני ג'ימיני. נא לומר את שאלתך לאחר הצליל ובסיום להקיש סולמית.&re_api=type=record&record_ok=no&record_ok_no_ask=yes&record_post_file_name=file"
        return Response(text, mimetype='text/plain')

    # 2. עיבוד ההקלטה עם זיכרון
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                # אתחול צ'אט חדש אם זה משתמש חדש בשיחה הנוכחית
                if call_id not in chat_sessions:
                    chat_sessions[call_id] = model.start_chat(history=[])
                
                chat = chat_sessions[call_id]
                audio_data = file.read()
                
                # שליחה לג'ימיני בתוך ה-session של הצ'אט
                response = chat.send_message([
                    "ענה בעברית קצרה מאוד. אם זו שאלה המשכית, התייחס למה שנאמר קודם בשיחה.",
                    {'mime_type': 'audio/wav', 'data': audio_data}
                ])
                
                answer = response.text.replace('*', '').replace('#', '').strip()
                
                # אנחנו משתמשים ב-&next= כדי להחזיר אותו להקלטה נוספת באותה שלוחה (אופציונלי)
                # אם אתה רוצה שהוא ינתק אחרי תשובה אחת, תשאיר next=hangup
                return Response(f"say={answer}&next=.", mimetype='text/plain')
                
            except Exception as e:
                return Response("say=מצטער, חלה שגיאה בעיבוד.&next=hangup", mimetype='text/plain')
        
    return Response("say=לא התקבל קובץ.&next=hangup", mimetype='text/plain')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
