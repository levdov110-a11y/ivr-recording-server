import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response

genai.configure(api_key="AIzaSyCTsATxKCBR2EelzU8qzQZ9aOIT6QXLM8U")
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="אתה עוזר קולי חכם. ענה על השאלה שבהקלטה בעברית קצרה, ללא סימנים מיוחדים."
)

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is Up!"

@app.route('/chat', methods=['GET', 'POST'])
def gemini_chat():
    file_path = request.args.get('AAA')
    
    if file_path:
        try:
            # אנחנו משתמשים בקישור הורדה ישיר. 
            # אם יש לך טוקן למערכת, תוסיף אותו אחרי ה-token=
            download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?token=&path=ivr/{file_path}"
            
            audio_response = requests.get(download_url)
            
            if audio_response.status_code == 200:
                audio_data = audio_response.content
                
                response = model.generate_content([
                    "הקשב להקלטה וענה על השאלה בקצרה.",
                    {'mime_type': 'audio/wav', 'data': audio_data}
                ])
                
                answer = response.text.replace('*', '').replace('#', '').strip()
                return Response(f"say={answer}&next=hangup", mimetype='text/plain')
            else:
                # אם השרת לא הצליח להוריד את הקובץ
                return Response(f"say=שגיאה במשיכת הקובץ קוד {audio_response.status_code}&next=hangup", mimetype='text/plain')
        
        except Exception as e:
            return Response("say=תקלה בעיבוד&next=hangup", mimetype='text/plain')

    return Response("say=ממתין להקלטה&next=hangup", mimetype='text/plain')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
