import os
import google.generativeai as genai
from flask import Flask, request, make_response

genai.configure(api_key="AIzaSyCTsATxKCBR2EelzU8qzQZ9aOIT6QXLM8U")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def gemini_ivr():
    # אם ימות המשיח שולחים הודעת ניתוק, אנחנו מאשרים ומסיימים
    if request.args.get('hangup') == 'yes':
        return "ok"

    if request.method == 'GET':
        # פקודה לימות המשיח: הקלטה ושליחה לשרת ב-POST
        response_text = "say=נא לומר את השאלה לאחר הצליל ובסיום להקיש סולמית.&re_api=type=record&record_ok=no&record_ok_no_ask=yes&record_post_file_name=file"
        res = make_response(response_text)
        res.headers["Content-Type"] = "text/plain; charset=utf-8"
        return res

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                audio_data = file.read()
                # פנייה לג'ימיני
                response = model.generate_content([
                    "ענה בעברית קצרה מאוד על השאלה שבהקלטה. ללא סימנים מיוחדים.",
                    {'mime_type': 'audio/wav', 'data': audio_data}
                ])
                answer = response.text.replace('*', '').replace('#', '')
                res = make_response(f"say={answer}&next=hangup")
            except Exception:
                res = make_response("say=חלה שגיאה בעיבוד השאלה.&next=hangup")
        else:
            res = make_response("say=לא התקבל קובץ קולי.&next=hangup")
            
        res.headers["Content-Type"] = "text/plain; charset=utf-8"
        return res

    return "ok"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
