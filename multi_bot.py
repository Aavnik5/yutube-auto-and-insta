import os, random, json, requests
from instagrapi import Client

# --- MOVIEPY VERSION FIX ---
try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# --- CONFIGURATION ---
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
INSTA_USER = os.getenv("INSTA_USERNAME")
INSTA_PASS = os.getenv("INSTA_PASSWORD")

# --- 1. DYNAMIC VIRAL CONTENT (Clean) ---
def get_viral_content():
    captions = [
        "Success is a mindset, not a destination. ✨",
        "The grind is silent, the success is loud. 🦁",
        "Luxury is the reward for your hard work. 💰",
        "Don't stay in bed unless you're making money. 🚀",
        "Your future self is counting on you. 💎",
        "Dream big, work harder. 🏆",
        "Work until your bank account looks like a phone number. 📞",
        "Level up in private. Let them wonder. 🌪️"
    ]
    hashtags = "#Luxury #Wealth #Success #Motivation #Trending #Shorts #Reels"
    selected = random.choice(captions)
    return f"{selected}\n.\n.\n{hashtags}", selected

# --- 2. DRIVE MUSIC DOWNLOADER ---
def download_music():
    print("📥 Downloading random music from Google Drive...")
    # ⚠️ Apni File IDs yahan daalein
    drive_ids = ["16xkYWn6J3oFm5GSGytr2go18QMHjVgpo"] 
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

# --- 3. PEXELS VIDEO FETCH (Filtered for 30s+) ---
def get_video():
    print("🎥 Fetching luxury video (Target: 30s+)...")
    queries = ["luxury cars", "modern architecture", "expensive lifestyle", "aesthetic city"]
    query = random.choice(queries)
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=20&orientation=portrait"
    
    res = requests.get(url, headers=headers).json()
    # Sirf wahi videos dekho jo 25-30 seconds se lambi hain
    valid_videos = [v for v in res['videos'] if v['duration'] >= 28]
    
    if not valid_videos:
        video_data = random.choice(res['videos']) # Fallback
    else:
        video_data = random.choice(valid_videos)
        
    video_url = video_data['video_files'][0]['link']
    with open("raw_video.mp4", "wb") as f:
        f.write(requests.get(video_url).content)
    return "raw_video.mp4"

# --- 4. VIDEO & AUDIO MIXING (The Fix) ---
def create_final_video(video_path, audio_path):
    print("🎬 Clipping to 30s and Syncing Audio...")
    try:
        # Video load karo aur uski original (silent) audio hatao
        video = VideoFileClip(video_path).without_audio()
        
        # Duration check aur 30 sec par cut
        target_duration = 30
        if video.duration > target_duration:
            video = video.subclip(0, target_duration)
        else:
            target_duration = video.duration

        # Audio mix karo
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path).set_duration(target_duration)
            video = video.set_audio(audio)
        
        output = "final_output.mp4"
        # Audio aur Video sync fix ke liye parameters
        video.write_videofile(output, codec="libx264", audio_codec="aac", fps=24, logger=None)
        return output
    except Exception as e:
        print(f"❌ Mixing Error: {e}")
        return video_path

# --- 5. PLATFORM POSTING ---
def post_insta(file_path, caption):
    print("📸 Uploading Reel...")
    cl = Client()
    cl.set_settings(json.loads(os.getenv("INSTA_SESSION_JSON")))
    cl.login(os.getenv("INSTA_USERNAME"), os.getenv("INSTA_PASSWORD"))
    cl.clip_upload(file_path, caption=caption)

def post_youtube(file_path, title):
    print("📺 Uploading YouTube Short...")
    creds = Credentials.from_authorized_user_info(json.loads(os.getenv("YT_TOKEN_JSON")))
    yt = build('youtube', 'v3', credentials=creds)
    body = {
        'snippet': {'title': title, 'description': f'{title} #Shorts #Luxury', 'categoryId': '22'},
        'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
    }
    yt.videos().insert(part='snippet,status', body=body, media_body=MediaFileUpload(file_path)).execute()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        insta_cap, yt_title = get_viral_content()
        v_path = get_video()
        a_path = download_music()
        final_file = create_final_video(v_path, a_path)
        
        # Independent Platform Runs
        try:
            post_insta(final_file, insta_cap)
            print("✅ Insta Done!")
        except Exception as e: print(f"❌ Insta Error: {e}")

        try:
            post_youtube(final_file, yt_title)
            print("✅ YouTube Done!")
        except Exception as e: print(f"❌ YouTube Error: {e}")

    except Exception as main_e:
        print(f"💀 Critical Bot Error: {main_e}")
