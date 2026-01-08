import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response

# משיכת המפתח מהגדרות השרת ב-Render
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# כאן פתרנו את השגיאה: מגדירים רק את שם המודל ללא תוספות
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/chat', methods=['GET', 'POST'])
def gemini_chat():
    file_path = request.args.get('AAA')
    api_did = request.args.get('ApiDID')
    
    if not file_path or not api_did:
        return Response("say=נתונים חסרים&next=hangup", mimetype='text/plain; charset=utf-8')

    try:
        # הורדת הקובץ מימות המשיח
        url = f"https://www.call2all.co.il/ym/api/DownloadFile?path=ivr/{api_did}/{file_path}"
        audio_response = requests.get(url, timeout=15)
        
        if audio_response.status_code == 200:
            # שליחה לג'ימיני - הספרייה כבר יודעת לאיזו כתובת ללכת
            response = model.generate_content([
                "הקשב להקלטה וענה עליה בעברית קצרה מאוד.",
                {'mime_type': 'audio/wav', 'data': audio_response.content}
            ])
            
            answer = response.text.replace('*', '').replace('#', '').strip()
            return Response(f"say={answer}&next=hangup", mimetype='text/plain; charset=utf-8')
        
        return Response(f"say=שגיאה בהורדת קובץ קוד {audio_response.status_code}&next=hangup", mimetype='text/plain; charset=utf-8')
            
    except Exception as e:
        # כאן נראה בלוגים אם יש שגיאה חדשה
        print(f"ERROR: {str(e)}")
        return Response(f"say=תקלה בעיבוד שגיאה {str(e)[:20]}&next=hangup", mimetype='text/plain; charset=utf-8')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
