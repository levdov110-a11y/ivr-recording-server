import os
import google.generativeai as genai
from flask import Flask, request

# הגדרת Gemini עם המפתח שלך
genai.configure(api_key="AIzaSyCTsATxKCBR2EelzU8qzQZ9aOIT6QXLM8U")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def gemini_ivr():
    # כשהמחייג נכנס לשלוחה
    if request.method == 'GET':
        return (
            "say=נא לומר את השאלה לאחר הצליל ובסיום להקיש סולמית."
            "&re_api=type=record"
            "&record_ok=no"
            "&record_ok_no_ask=yes"
            "&record_post_file_name=file"
        )

    # קבלת הקלטה ועיבוד ע"י ג'ימיני (חינמי - ללא יחידות תמלול)
    if request.method == 'POST':
        if 'file' in request.files:
            audio_data = request.files['file'].read()
            prompt = "הקשב להקלטה וענה עליה בעברית קצרה מאוד וללא סימנים מיוחדים."
            response = model.generate_content([
                prompt,
                {'mime_type': 'audio/wav', 'data': audio_data}
            ])
            clean_text = response.text.replace('*', '').replace('#', '')
            return f"say={clean_text}&next=hangup"
            
    return "hangup"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
