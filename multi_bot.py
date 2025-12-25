import os, random, json, requests
from instagrapi import Client
from moviepy.editor import VideoFileClip, AudioFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# --- CONFIGURATION (GitHub Secrets se aayega) ---
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
INSTA_USER = os.getenv("INSTA_USERNAME")
INSTA_PASS = os.getenv("INSTA_PASSWORD")

# --- 1. GOOGLE DRIVE MUSIC DOWNLOADER ---
def download_music():
    print("📥 Downloading random music from Google Drive...")
    # ⚠️ YAHAN APNI DRIVE FILE IDs DAALEIN (Jo aapne folder se nikali hain)
    drive_ids = [
        "16xkYWn6J3oFm5GSGytr2go18QMHjVgpo", # Example ID, replace with actual File IDs
        "ADD_YOUR_SECOND_FILE_ID_HERE"
    ]
    file_id = random.choice(drive_ids)
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    
    os.makedirs("music", exist_ok=True)
    music_path = "music/bg_audio.mp3"
    
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(music_path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192): f.write(chunk)
        return music_path
    return None

# --- 2. PEXELS VIDEO FETCH ---
def get_video():
    print("🎥 Fetching luxury video from Pexels...")
    queries = ["luxury cars", "modern villa", "aesthetic travel", "rolex watch"]
    query = random.choice(queries)
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    
    res = requests.get(url, headers=headers).json()
    video_data = random.choice(res['videos'])
    video_url = video_data['video_files'][0]['link']
    
    with open("raw_video.mp4", "wb") as f:
        f.write(requests.get(video_url).content)
    return "raw_video.mp4"

# --- 3. VIDEO & AUDIO MIXING ---
def create_final_video(video_path, audio_path):
    print("🎬 Mixing video and audio...")
    try:
        video = VideoFileClip(video_path)
        # Agar music mil gaya toh mix karein, varna raw video use karein
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path).set_duration(video.duration)
            video = video.set_audio(audio)
        
        output = "final_output.mp4"
        video.write_videofile(output, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
        return output
    except Exception as e:
        print(f"❌ Mixing Error: {e}")
        return video_path

# --- 4. PLATFORM POSTING ---
def post_insta(file_path, caption):
    print("📸 Uploading to Instagram Reels...")
    cl = Client()
    cl.set_settings(json.loads(os.getenv("INSTA_SESSION_JSON")))
    cl.login(INSTA_USER, INSTA_PASS)
    cl.clip_upload(file_path, caption=caption)

def post_youtube(file_path, title):
    print("📺 Uploading to YouTube Shorts...")
    creds_info = json.loads(os.getenv("YT_TOKEN_JSON"))
    creds = Credentials.from_authorized_user_info(creds_info)
    yt = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {'title': title, 'description': '#Shorts #Luxury #KroldIT', 'categoryId': '22'},
        'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
    }
    yt.videos().insert(part='snippet,status', body=body, media_body=MediaFileUpload(file_path)).execute()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        title = "Luxury is a lifestyle. ✨ #Luxury #Goals #Success"
        v_path = get_video()
        a_path = download_music()
        final_file = create_final_video(v_path, a_path)
        
        # Dono jagah post karein
        post_insta(final_file, title)
        post_youtube(final_file, title)
        print("🚀 Mission Accomplished! Video posted everywhere.")
    except Exception as main_e:
        print(f"💀 Critical Bot Error: {main_e}")
