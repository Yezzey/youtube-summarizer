from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import requests

app = Flask(__name__, template_folder='templates', static_folder='static')

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

def summarize_text(text):
    headers = { "Content-Type": "application/json" }
    response = requests.post(HF_API_URL, headers=headers, json={"inputs": text})
    if response.status_code == 200:
        return response.json()[0]["summary_text"]
    else:
        return "Error: Unable to summarize."

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    yt_url = request.form.get("yt_url")
    video_id = extract_video_id(yt_url)
    if not video_id:
        return render_template("index.html", error="Invalid YouTube URL.")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([seg["text"] for seg in transcript])
        if len(full_text.split()) > 3000:
            return render_template("index.html", error="Video is too long to summarize (max 3000 words).")
        summary = summarize_text(full_text)
        return render_template("index.html", summary=summary)
    except (TranscriptsDisabled, NoTranscriptFound):
        return render_template("index.html", error="This video has no transcript available.")
    except Exception as e:
        return render_template("index.html", error="An unexpected error occurred.")

if __name__ == "__main__":
    app.run(debug=True)
