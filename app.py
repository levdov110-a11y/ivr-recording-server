import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response

# הגדרת המודל עם הנחיות מערכת קבועות
genai.configure(api_key="AIzaSyCTsATxKCBR2EelzU8qzQZ9aOIT6QXLM8U")
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="אתה עוזר קולי חכם במערכת טלפונית. המשתמש מקליט שאלה, ואתה צריך לענות עליה בצורה קצרה, ברורה ועניינית. ענה תמיד בעברית. אל תשתמש בסימנים כמו כוכביות או סולמיות, רק בטקסט חלק שניתן להקריא."
)

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is Up and Running!"

@app.route('/chat', methods=['GET', 'POST'])
def gemini_chat():
    # קבלת נתיב הקובץ מימות המשיח (הפרמטר AAA)
    file_path = request.args.get('AAA')
    api_did = request.args.get('ApiDID')
    
    if file_path and api_did:
        try:
            # כתובת להורדת הקובץ (ללא טוקן אם המערכת פתוחה, או הוסף טוקן אם יש)
            download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?path=ivr/{api_did}/{file_path}"
            
            audio_response = requests.get(download_url)
            if audio_response.status_code == 200:
                audio_data = audio_response.content
                
                # שליחה לג'ימיני עם הנחיה ספציפית להקלטה הזו
                prompt = "הקשב להקלטה המצורפת וענה על השאלה של המשתמש בקצרה."
                response = model.generate_content([
                    prompt,
                    {'mime_type': 'audio/wav', 'data': audio_data}
                ])
                
                answer = response.text.replace('*', '').replace('#', '').strip()
                return Response(f"say={answer}&next=hangup", mimetype='text/plain')
            else:
                return Response("say=שגיאה במשיכת קובץ השמע&next=hangup", mimetype='text/plain')
        
        except Exception as e:
            return Response("say=תקלה בעיבוד הנתונים&next=hangup", mimetype='text/plain')

    return Response("say=לא התקבלה הקלטה תקינה&next=hangup", mimetype='text/plain')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
