import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response

# 1. הגדרת המפתח בצורה מאובטחת
# וודא שהגדרת ב-Render משתנה בשם GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 2. הגדרת המודל והנחיות המערכת
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="אתה עוזר קולי חכם. ענה על השאלה שבהקלטה בעברית קצרה מאוד, ללא סימנים מיוחדים."
)

app = Flask(__name__)

@app.route('/')
def home():
    return "AI Server is Live!"

@app.route('/chat', methods=['GET', 'POST'])
def gemini_chat():
    file_path = request.args.get('AAA')
    api_did = request.args.get('ApiDID')
    
    # בדיקה ראשונית אם הנתונים הגיעו מימות המשיח
    if not file_path or not api_did:
        return Response("say=לא התקבל נתיב לקובץ&next=hangup", mimetype='text/plain; charset=utf-8')

    try:
        # 3. ניסיון הורדת הקובץ
        download_url = f"https://www.call2all.co.il/ym/api/DownloadFile?path=ivr/{api_did}/{file_path}"
        print(f"DEBUG: Downloading from: {download_url}")
        
        audio_response = requests.get(download_url, timeout=10)
        
        if audio_response.status_code != 200:
            # אם ההורדה נכשלה, נחזיר הודעה לימות המשיח
            return Response(f"say=שגיאה בהורדת הקובץ קוד {audio_response.status_code}&next=hangup", mimetype='text/plain; charset=utf-8')

        audio_data = audio_response.content
        print("DEBUG: File downloaded successfully")

        # 4. שליחה לבינה מלאכותית
        response = model.generate_content(
            [
                "הקשב להקלטה וענה על השאלה בקצרה.",
                {'mime_type': 'audio/wav', 'data': audio_data}
            ]
        )
        
        # ניקוי התשובה מתווים שמשבשים את ימות המשיח
        answer = response.text.replace('*', '').replace('#', '').replace('\n', ' ').strip()
        
        if not answer:
            answer = "לא התקבלה תשובה מהבינה המלאכותית"

        print(f"DEBUG: Gemini Success! Answer: {answer}")
        return Response(f"say={answer}&next=hangup", mimetype='text/plain; charset=utf-8')

    except Exception as e:
        # 5. מנגנון הדיווח על שגיאות לתוך הטלפון
        error_msg = str(e).replace('"', '').replace("'", "")
        print(f"CRITICAL ERROR: {error_msg}")
        
        # נחזיר לימות המשיח את תחילת השגיאה כדי שתבין מה קרה (למשל: API KEY חסום)
        return Response(f"say=תקלה במערכת. פרטי השגיאה הם {error_msg[:40]}&next=hangup", mimetype='text/plain; charset=utf-8')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
