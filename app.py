import os
import google.generativeai as genai
from flask import Flask, request, make_response

genai.configure(api_key="AIzaSyCTsATxKCBR2EelzU8qzQZ9aOIT6QXLM8U")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def gemini_ivr():
    # שלב א: כניסה לשלוחה (GET)
    if request.method == 'GET':
        # הפקודה שמורה לימות המשיח להקליט ולשלוח לשרת
        response_text = "say=נא לומר את השאלה לאחר הצליל ובסיום להקיש סולמית.&re_api=type=record&record_ok=no&record_ok_no_ask=yes&record_post_file_name=file"
        res = make_response(response_text)
        res.headers["Content-Type"] = "text/plain; charset=utf-8"
        return res

    # שלב ב: קבלת ההקלטה (POST)
    if request.method == 'POST':
        if 'file' in request.files:
            try:
                audio_data = request.files['file'].read()
                # שליחה לג'ימיני
                gen_response = model.generate_content([
                    "ענה בקצרה מאוד בעברית על השאלה שבהקלטה. ללא סימנים מיוחדים.",
                    {'mime_type': 'audio/wav', 'data': audio_data}
                ])
                answer = gen_response.text.replace('*', '').replace('#', '')
                res = make_response(f"say={answer}&next=hangup")
            except Exception:
                res = make_response("say=חלה שגיאה בעיבוד.&next=hangup")
        else:
            res = make_response("say=לא התקבל קובץ.&next=hangup")
            
        res.headers["Content-Type"] = "text/plain; charset=utf-8"
        return res

    return "hangup"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
