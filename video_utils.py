import os

def get_background_video(niche):
    bg_map = {
        "tech": "assets/bg_tech_loop.mp4",
        "ai": "assets/bg_ai_loop.mp4",
        "finance": "assets/bg_finance_loop.mp4",
        "science": "assets/bg_science_loop.mp4",
        "cybersecurity": "assets/bg_cyber_loop.mp4",
    }
    bg_path = bg_map.get(niche.lower())
    if bg_path and os.path.exists(bg_path):
        return bg_path
    return None
