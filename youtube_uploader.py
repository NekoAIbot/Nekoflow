# youtube_uploader.py
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the required YouTube scopes for uploading videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    creds = None
    # This file must be downloaded from the Google Cloud Console.
    CLIENT_SECRETS_FILE = "client_secret.json"
    TOKEN_PICKLE = "token.pickle"
    
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as token:
            creds = pickle.load(token)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        creds = flow.run_console()
        with open(TOKEN_PICKLE, "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, tags, categoryId="27"):
    """
    Uploads a video to YouTube.
    
    Args:
        file_path (str): Path to the video file.
        title (str): The video title.
        description (str): A description for the video.
        tags (list): A list of tags.
        categoryId (str): YouTube category ID (default "27" for Education; change by niche).
    
    Returns:
        The uploaded video’s YouTube ID.
    """
    youtube = get_authenticated_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": categoryId
        },
        "status": {
            "privacyStatus": "public",  # Change this if you want private or unlisted.
            "selfDeclaredMadeForKids": False,
        }
    }
    
    try:
        print("Uploading video...")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=file_path
        )
        response = request.execute()
        print(f"Video uploaded successfully. Video ID: {response['id']}")
        return response["id"]
    except HttpError as e:
        print(f"An HTTP error occurred: {e.resp.status}\n{e.content}")
        return None

if __name__ == "__main__":
    # Example usage:
    video_file = "generated_videos/tech/example_video.mp4"
    # Replace with your own metadata generation logic as needed.
    title = "Example Tech Video Title"
    description = "This video explains the latest update in tech."
    tags = ["tech", "update", "innovation"]
    
    upload_video(video_file, title, description, tags)
