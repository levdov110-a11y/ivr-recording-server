
import os
import google.generativeai as genai
from flask import Flask, request, Response

genai.configure(api_key="AIzaSyCTsATxKCBR2EelzU8qzQZ9aOIT6QXLM8U")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def gemini_ivr():
    # אם המערכת מודיעה על ניתוק, אל תחזיר פקודות 'say'
    if request.args.get('hangup') == 'yes':
        return Response("ok", mimetype='text/plain')

    if request.method == 'GET':
        # הפקודה לימות המשיח - שים לב לשינוי קטן ב-re_api
        text = "say=נא לומר את השאלה לאחר הצליל ובסיום להקיש סולמית.&re_api=yes&type=record&record_post_file_name=file"
        return Response(text, mimetype='text/plain')

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                audio_data = file.read()
                response = model.generate_content([
                    "ענה בעברית קצרה מאוד על השאלה שבהקלטה.",
                    {'mime_type': 'audio/wav', 'data': audio_data}
                ])
                answer = response.text.replace('*', '').replace('#', '').strip()
                return Response(f"say={answer}&next=hangup", mimetype='text/plain')
            except Exception:
                return Response("say=שגיאה בעיבוד&next=hangup", mimetype='text/plain')
    
    return Response("ok", mimetype='text/plain')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
