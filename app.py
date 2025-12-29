import os
import google.generativeai as genai
from flask import Flask, request, make_response

genai.configure(api_key="AIzaSyCTsATxKCBR2EelzU8qzQZ9aOIT6QXLM8U")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST', 'PUT'])
def gemini_ivr():
    # טיפול בניתוק
    if request.args.get('hangup') == 'yes':
        return make_response("ok", 200, {'Content-Type': 'text/plain'})

    # שלב הכניסה - GET
    if request.method == 'GET':
        # פקודה אחת פשוטה שמשלבת הודעה והקלטה
        res_text = "say=נא לומר שאלה ובסיום סולמית&type=record&record_post_file_name=file"
        return make_response(res_text, 200, {'Content-Type': 'text/plain'})

    # שלב קבלת הקובץ - POST
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                audio_data = file.read()
                response = model.generate_content([
                    "ענה בעברית קצרה מאוד. ללא סימנים מיוחדים.",
                    {'mime_type': 'audio/wav', 'data': audio_data}
                ])
                answer = response.text.replace('*', '').replace('#', '').strip()
                res_text = f"say={answer}&next=hangup"
                return make_response(res_text, 200, {'Content-Type': 'text/plain'})
            except Exception:
                return make_response("say=תקלה בעיבוד&next=hangup", 200, {'Content-Type': 'text/plain'})
    
    return make_response("ok", 200, {'Content-Type': 'text/plain'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
