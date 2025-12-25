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
FOLDER_ID = "16xkYWn6J3oFm5GSGytr2go18QMHjVgpo"

# --- 1. VIRAL CONTENT GENERATOR (50+ Set) ---
def get_viral_content():
    captions = [
        "Success is a mindset, not a destination. ✨", "The grind is silent, the success is loud. 🦁",
        "Luxury is the reward for your hard work. 💰", "Your future self is counting on you. 💎",
        "Dream big, work harder. 🏆", "Level up in private. Let them wonder. 🌪️",
        "Work until your bank account looks like a phone number. 📞", "Silence is the best status symbol. 🤫",
        "I didn't come this far to only come this far. 🏎️", "Invest in your dreams. Grind now, shine later. 🥂",
        "Classy is when you have a lot to say but stay silent. 🎩", "Your only limit is your mind. ⛓️",
        "Don't stay in bed unless you're making money. 🛌", "Life is short. Make every second count. ⌚",
        "The best revenge is massive success. 🔥", "Don't stop until you're proud. 👑",
        "Focus on the goal, not the obstacles. 🎯", "Consistency is what transforms average into excellence. 🛠️",
        "Wealth is a state of mind. 🏦", "Be so good they can't ignore you. 🌟",
        "Discipline will take you where motivation can't. 🚀", "Small steps lead to big results. 📈",
        "Style is a reflection of your attitude. 👔", "Chasing dreams, catching excellence. 🌌",
        "Quality over quantity, always. 💎", "Live life on your own terms. 🗺️",
        "A goal without a plan is just a wish. 🌠", "Everything you want is on the other side of fear. 🦁",
        "Master your mindset, master your life. 🧠", "Stay humble, stay focused, stay blessed. 🙏",
        "The secret of getting ahead is getting started. 🚦", "Your energy is your currency. Spend it wisely. ⚡",
        "Hustle until your haters ask if you're hiring. 💼", "Winners focus on winning, losers focus on winners. 🏆",
        "Great things never come from comfort zones. 🛋️", "Success belongs to those who prepare for it. 📝",
        "Building an empire in silence. 🏗️", "Manifesting a life full of luxury. ✨",
        "Stay hungry, stay foolish. 🍎", "If you want to be successful, be consistent. 🔄",
        "Don't tell people your dreams, show them. 🎬", "Be the person you've always wanted to meet. 💎",
        "Hard work beats talent when talent doesn't work hard. ⚡", "I’m not lucky, I’m hardworking. 🍀",
        "Success is my only option. 🎯", "Vision without action is just a dream. 👁️",
        "Make your life a masterpiece. 🖼️", "The journey is the reward. 🛤️",
        "Choose your path and walk it with pride. 👞", "Turn your obstacles into opportunities. 🛠️"
    ]
    hashtags_pool = [
        "#Luxury", "#Wealth", "#Success", "#Motivation", "#Mindset", "#Entrepreneur", "#Goals", "#Billionaire",
        "#RichLife", "#Millionaire", "#FinancialFreedom", "#LuxuryLifestyle", "#Aesthetic", "#Shorts", "#Reels",
        "#Viral", "#Trending", "#Explore", "#HighLife", "#Elite", "#Ambition", "#DreamBig", "#Wealthy",
        "#MoneyMindset", "#RichVibes", "#ClassicStyle", "#Vibe", "#SuccessMindset", "#Hustle", "#DailyMotivation",
        "#VisualAesthetic", "#Modern", "#Dubai", "#Monaco", "#ExpensiveTaste", "#HighSociety", "#Classy",
        "#LuxuryTravel", "#LuxuryCars", "#Supercars", "#Architecture", "#ModernVilla", "#BusinessOwner",
        "#AestheticPost", "#Power", "#GrowthMindset", "#SelfImprovement", "#Income", "#Asset", "#PassiveIncome"
    ]
    selected_caption = random.choice(captions)
    tag_string = " ".join(random.sample(hashtags_pool, 15))
    return f"{selected_caption}\n.\n.\n.\n{tag_string}", selected_caption

# --- 2. DRIVE MUSIC AUTO-SCANNER ---
def download_random_music():
    print("📥 Scanning Google Drive folder for music...")
    try:
        creds_info = json.loads(os.getenv("YT_TOKEN_JSON"))
        creds = Credentials.from_authorized_user_info(creds_info)
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(q=f"'{FOLDER_ID}' in parents and mimeType='audio/mpeg'", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items: return None
        selected_file = random.choice(items)
        file_id = selected_file['id']
        url = f'https://drive.google.com/uc?export=download&id={file_id}'
        os.makedirs("music", exist_ok=True)
        path = "music/bg_audio.mp3"
        res = requests.get(url, stream=True)
        with open(path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192): f.write(chunk)
        return path
    except Exception as e: return None

# --- 3. PEXELS VIDEO FETCH (High Quality Filter) ---
def get_video():
    print("🎥 Fetching HIGH QUALITY luxury video from Pexels...")
    queries = ["luxury cars 4k", "modern architecture hd", "expensive lifestyle aesthetic", "luxury villa portrait"]
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={random.choice(queries)}&per_page=15&orientation=portrait"
    res = requests.get(url, headers=headers).json()
    
    # 25s+ videos ko filter karein
    valid_videos = [v for v in res['videos'] if v['duration'] >= 25]
    video_data = random.choice(valid_videos if valid_videos else res['videos'])
    
    # Sabse badi resolution wali file dhoondna (4K/HD)
    best_file = max(video_data['video_files'], key=lambda x: x['width'])
    print(f"💎 Selected Resolution: {best_file['width']}x{best_file['height']}")
    
    with open("raw_video.mp4", "wb") as f:
        f.write(requests.get(best_file['link']).content)
    return "raw_video.mp4"

# --- 4. MIXING & CLIPPING (Pro Encoding Settings) ---
def create_final_video(video_path, audio_path):
    print("🎬 Mixing with Professional Encoding (30s)...")
    try:
        video = VideoFileClip(video_path).without_audio()
        if video.duration > 30: video = video.subclip(0, 30)
        target_dur = video.duration
        
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path).set_duration(target_dur)
            video = video.set_audio(audio)
            
        output = "final_output.mp4"
        # 🚀 HIGH QUALITY ENCODING
        video.write_videofile(
            output, 
            codec="libx264", 
            audio_codec="aac", 
            fps=30, 
            bitrate="10000k", 
            preset="slow",
            ffmpeg_params=["-crf", "18"],
            logger=None
        )
        return output
    except Exception as e: return video_path

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        insta_cap, yt_title = get_viral_content()
        v_raw = get_video()
        a_raw = download_random_music()
        final_video = create_final_video(v_raw, a_raw)
        
        # Instagram
        try:
            cl = Client()
            cl.set_settings(json.loads(os.getenv("INSTA_SESSION_JSON")))
            cl.login(os.getenv("INSTA_USERNAME"), os.getenv("INSTA_PASSWORD"))
            cl.clip_upload(final_video, caption=insta_cap)
            print("✅ Instagram Success!")
        except Exception as e: print(f"❌ Insta Fail: {e}")

        # YouTube
        try:
            creds = Credentials.from_authorized_user_info(json.loads(os.getenv("YT_TOKEN_JSON")))
            yt = build('youtube', 'v3', credentials=creds)
            body = {'snippet': {'title': yt_title, 'description': f'{yt_title} #Shorts #Luxury', 'categoryId': '22'},
                    'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}}
            yt.videos().insert(part='snippet,status', body=body, media_body=MediaFileUpload(final_video)).execute()
            print("✅ YouTube Success!")
        except Exception as e: print(f"❌ YouTube Fail: {e}")

    except Exception as e: print(f"💀 Fatal Error: {e}")
