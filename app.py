import os
import requests
import google.generativeai as genai
from flask import Flask, request, Response

# תיקון קריטי: הגדרת המפתח כך שיעבוד גם אם קראת לו GEMINI וגם אם GOOGLE
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction="ענה בעברית קצרה מאוד וללא סימנים מיוחדים."
    )
else:
    model = None

app = Flask(__name__)

@app.route('/chat', methods=['GET', 'POST'])
def gemini_chat():
    # קבלת הפרמטרים מימות המשיח
    file_path = request.args.get('AAA')
    api_did = request.args.get('ApiDID')
    
    if not api_key:
        return Response("say=שגיאה הגדרת מפתח חסרה בשרת&next=hangup", mimetype='text/plain; charset=utf-8')

    if file_path and api_did:
        try:
            # הורדת הקובץ
            url = f"https://www.call2all.co.il/ym/api/DownloadFile?path=ivr/{api_did}/{file_path}"
            audio_response = requests.get(url, timeout=10)
            
            if audio_response.status_code != 200:
                return Response("say=שגיאה בהורדת ההקלטה&next=hangup", mimetype='text/plain; charset=utf-8')

            # שליחה לג'ימיני
            response = model.generate_content([
                "מה נאמר בהקלטה? ענה בקצרה.",
                {'mime_type': 'audio/wav', 'data': audio_response.content}
            ])
            
            # ניקוי התשובה מתווים שימות המשיח לא אוהבים
            answer = response.text.replace('*', '').replace('#', '').strip()
            
            # אם קיבלנו תשובה ריקה
            if not answer:
                answer = "לא הצלחתי להבין את ההקלטה"
                
            return Response(f"say={answer}&next=hangup", mimetype='text/plain; charset=utf-8')

        except Exception as e:
            # במקרה של שגיאה - מחזירים לימות המשיח טקסט של השגיאה במקום קריסה
            error_text = str(e)[:30].replace("'", "")
            return Response(f"say=תקלה בעיבוד. שגיאה {error_text}&next=hangup", mimetype='text/plain; charset=utf-8')

    return Response("say=לא התקבלו נתונים&next=hangup", mimetype='text/plain; charset=utf-8')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
