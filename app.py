from flask import Flask, request, send_file
from flask_cors import CORS
import openai
import os
from moviepy.editor import *
import requests

# ضع هنا مفتاح OpenAI الخاص بك
openai.api_key = "PUT_YOUR_OPENAI_KEY"

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    idea = data["idea"]

    # 1️⃣ توليد القصة
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "اكتب قصة قصيرة مناسبة لمشهد فيديو"},
            {"role": "user", "content": idea}
        ]
    )

    story = response.choices[0].message.content

    # 2️⃣ توليد صورة
    image = openai.Image.create(prompt=story, n=1, size="1024x1024")
    img_url = image["data"][0]["url"]

    os.makedirs("media", exist_ok=True)
    img_data = requests.get(img_url).content
    with open("media/image.png", "wb") as f:
        f.write(img_data)

    # 3️⃣ توليد صوت
    audio = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=story
    )

    with open("media/voice.mp3", "wb") as f:
        f.write(audio.read())

    # 4️⃣ دمج الفيديو
    clip = ImageClip("media/image.png").set_duration(8)
    audio_clip = AudioFileClip("media/voice.mp3")
    clip = clip.set_audio(audio_clip)

    video_path = "media/final.mp4"
    clip.write_videofile(video_path, fps=24)

    return send_file(video_path, as_attachment=True)

if __name__ == "__main__":
    app.run()
