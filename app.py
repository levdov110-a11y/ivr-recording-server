import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response

# משיכת המפתח בצורה מאובטחת מהגדרות השרת (Environment Variable)
# כך גוגל לא תחסום לך את המפתח שוב
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# הגדרה מפורשת של המודל לגרסה היציבה
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="אתה עוזר קולי חכם. ענה על השאלה שבהקלטה בעברית קצרה מאוד, ללא סימנים מיוחדים."
)

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is Up!"

@app.route('/chat', methods=['GET', 'POST'])
def gemini_chat():
    file_path = request.args.get('AAA')
    api_did = request.args.get('ApiDID')
    
    if file_path and api_did:
        try:
            download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?path=ivr/{api_did}/{file_path}"
            print(f"DEBUG: Downloading from: {download_url}")
            
            audio_response = requests.get(download_url)
            
            if audio_response.status_code == 200:
                print("DEBUG: File downloaded successfully")
                audio_data = audio_response.content
                
                # שימוש ב-generate_content עם הגדרה ספציפית
                response = model.generate_content(
                    [
                        "הקשב להקלטה וענה על השאלה בקצרה.",
                        {'mime_type': 'audio/wav', 'data': audio_data}
                    ]
                )
                
                answer = response.text.replace('*', '').replace('#', '').strip()
                print(f"DEBUG: Gemini Success! Answer: {answer}")
                return Response(f"say={answer}&next=hangup", mimetype='text/plain; charset=utf-8')
            else:
                print(f"DEBUG: Download failed: {audio_response.status_code}")
                return Response("say=שגיאה בהורדת הקובץ&next=hangup", mimetype='text/plain; charset=utf-8')
        
        except Exception as e:
            print(f"DEBUG: Detailed Error: {str(e)}")
            return Response("say=תקלה בעיבוד הבינה המלאכותית&next=hangup", mimetype='text/plain; charset=utf-8')

    return Response("say=ממתין להקלטה&next=hangup", mimetype='text/plain; charset=utf-8')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
