import os, random, json, requests
from instagrapi import Client
from moviepy.editor import VideoFileClip, AudioFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# --- CONFIGURATION FROM SECRETS ---
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
INSTA_USER = os.getenv("INSTA_USERNAME")
INSTA_PASS = os.getenv("INSTA_PASSWORD")

def get_video():
    print("🎥 Fetching video from Pexels...")
    query = random.choice(["luxury car", "luxury watch", "modern mansion", "aesthetic travel"])
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait"
    res = requests.get(url, headers={"Authorization": PEXELS_KEY}).json()
    video_url = random.choice(res['videos'])['video_files'][0]['link']
    with open("raw.mp4", "wb") as f: f.write(requests.get(video_url).content)
    return "raw.mp4"

def mix_audio(video_path):
    print("🎵 Mixing background music...")
    music_files = [f for f in os.listdir("music") if f.endswith(".mp3")]
    if not music_files: return video_path
    
    video = VideoFileClip(video_path)
    audio = AudioFileClip(os.path.join("music", random.choice(music_files))).set_duration(video.duration)
    video.set_audio(audio).write_videofile("final.mp4", codec="libx264", audio_codec="aac")
    return "final.mp4"

def post_insta(file_path, text):
    print("📸 Posting to Instagram...")
    cl = Client()
    cl.set_settings(json.loads(os.getenv("INSTA_SESSION_JSON")))
    cl.login(INSTA_USER, INSTA_PASS)
    cl.clip_upload(file_path, caption=text)

def post_youtube(file_path, text):
    print("📺 Posting to YouTube Shorts...")
    creds = Credentials.from_authorized_user_info(json.loads(os.getenv("YT_TOKEN_JSON")))
    yt = build('youtube', 'v3', credentials=creds)
    body = {
        'snippet': {'title': text, 'description': '#Shorts #Luxury #KroldIT', 'categoryId': '22'},
        'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
    }
    yt.videos().insert(part='snippet,status', body=body, media_body=MediaFileUpload(file_path)).execute()

if __name__ == "__main__":
    caption = "Success is a mindset. ✨ #Luxury #Motivation #AI"
    video = get_video()
    final = mix_audio(video)
    
    try: post_insta(final, caption)
    except Exception as e: print(f"Insta Error: {e}")
    
    try: post_youtube(final, caption)
    except Exception as e: print(f"YouTube Error: {e}")
