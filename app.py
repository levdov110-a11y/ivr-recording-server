import os
import google.generativeai as genai
from flask import Flask, request, Response

# הגדרת מפתח ה-API של ג'ימיני
genai.configure(api_key="AIzaSyCTsATxKCBR2EelzU8qzQZ9aOIT6QXLM8U")
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)

# דף הבית - כדי שתוכל לראות בדפדפן שהשרת עובד
@app.route('/')
def home():
    return "The Server is LIVE! Waiting for audio from Yemot Hamashiah..."

# הנתיב שימות המשיח פונים אליו (צריך להופיע ב-api_link)
@app.route('/chat', methods=['GET', 'POST'])
def gemini_chat():
    # בשיטה שלך, ימות המשיח שולחים את הקובץ ב-POST תחת השם 'file'
    file = request.files.get('file')
    
    if file:
        try:
            audio_data = file.read()
            # שליחת קובץ השמע לבינה המלאכותית
            response = model.generate_content([
                "ענה בעברית קצרה מאוד על השאלה שבהקלטה. ללא כוכביות או סימנים מיוחדים.",
                {'mime_type': 'audio/wav', 'data': audio_data}
            ])
            
            # ניקוי התשובה מסימנים שעלולים לשבש את ההקראה
            answer = response.text.replace('*', '').replace('#', '').strip()
            
            # החזרת הפקודה לימות המשיח
            return Response(f"say={answer}&next=hangup", mimetype='text/plain')
            
        except Exception as e:
            print(f"Error: {e}")
            return Response("say=תקלה בעיבוד התשובה&next=hangup", mimetype='text/plain')
    
    # במקרה שמישהו נכנס ללינק בלי לשלוח קובץ
    return Response("say=לא התקבלה הקלטה&next=hangup", mimetype='text/plain')

if __name__ == "__main__":
    # הרצת השרת על הפורט ש-Render נותן
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
