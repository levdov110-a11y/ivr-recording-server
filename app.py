import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response

# שימוש במפתח שהגדרת ב-Render
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/chat', methods=['GET', 'POST'])
def gemini_chat():
    file_path = request.args.get('AAA')
    api_did = request.args.get('ApiDID')
    
    try:
        url = f"https://www.call2all.co.il/ym/api/DownloadFile?path=ivr/{api_did}/{file_path}"
        audio_response = requests.get(url, timeout=15)
        
        # כאן קורה הקסם - שליחה לג'ימיני
        response = model.generate_content([
            "ענה בעברית קצרה מאוד על השאלה שבהקלטה.",
            {'mime_type': 'audio/wav', 'data': audio_response.content}
        ])
        
        answer = response.text.replace('*', '').replace('#', '').replace('\n', ' ').strip()
        print(f"--- SUCCESS! GEMINI ANSWER: {answer} ---") # זה יופיע בלוג אם זה עובד
        return Response(f"say={answer}&next=hangup", mimetype='text/plain; charset=utf-8')
            
    except Exception as e:
        # הדפסה בולטת מאוד של השגיאה ללוג
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"THE ERROR IS: {str(e)}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return Response(f"say=תקלה בעיבוד שגיאה {str(e)[:20]}&next=hangup", mimetype='text/plain; charset=utf-8')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
