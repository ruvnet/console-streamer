import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
import subprocess
import threading
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

def get_authenticated_service():
    """
    Authenticate and build the YouTube service using Replit secrets for authentication.

    Returns:
    A YouTube service object authenticated with the credentials obtained from Replit secrets.
    """
    client_id = os.environ['GOOGLE_CLIENT_ID']
    client_secret = os.environ['GOOGLE_CLIENT_SECRET']
    refresh_token = os.environ['GOOGLE_REFRESH_TOKEN']
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
            }
        },
        scopes=SCOPES,
    )
    credentials = Credentials.from_authorized_user_info(info=flow.run_local_server()['tokens'])

    # Use the refresh token to refresh the credentials if they expire
    credentials.set_refresh_token(refresh_token)

    # Build the YouTube service with the authenticated credentials
    return build('youtube', 'v3', credentials=credentials)

def create_live_event(youtube, title, description, start_time, end_time):
    """
    Create a new live broadcast event on YouTube.

    Args:
    youtube: A YouTube service object.
    title: A string containing the title of the live broadcast.
    description: A string containing the description of the live broadcast.
    start_time: A string containing the start time of the live broadcast in ISO 8601 format.
    end_time: A string containing the end time of the live broadcast in ISO 8601 format.

    Returns:
    A tuple containing the ID of the new live broadcast event and the ID of the associated live chat.
    """
    event = youtube.liveBroadcasts().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title=title,
                description=description,
                scheduledStartTime=start_time,
                scheduledEndTime=end_time
            ),
            status=dict(
                privacyStatus="unlisted"
            )
        )
    ).execute()

    return event["id"], event["snippet"]["liveChatId"]

def stream_console_output_to_youtube(youtube, stream_id):
    """
    Stream console output to a YouTube live broadcast using ffmpeg.

    Args:
    youtube: A YouTube service object.
    stream_id: A string containing the ID of the YouTube live broadcast stream.
    """
    # Set the appropriate paths for your system
    FFMPEG_BIN = "ffmpeg"

    # Parameters for the video stream
    width, height = 640, 480
    fps = 30
  
    def generate_frames():
        font = ImageFont.truetype("arial.ttf", 20)
        text_color = (255, 255, 255)
        draw = ImageDraw.Draw(Image.new('RGB', (width, height)))

        while True:
            frame = Image.new('RGB', (width, height), (0, 0, 0))
            
            # Capture console output
            console_output = "Your console output here"
            y = 30
            for line in console_output.split('\n'):
                draw.text((10, y), line, font=font, fill=text_color)
                y += 30

            yield frame
            time.sleep(1 / fps)

    frame_generator = generate_frames()
    command = [FFMPEG_BIN,
               '-y', '-loglevel', 'error',
               '-f', 'rawvideo',
               '-pixel_format', 'rgb24',
               '-video_size', f'{width}x{height}',
               '-framerate', str(fps),
               '-i', '-',
               '-c:v', 'libx264',
               '-preset', 'ultrafast',
               '-tune', 'zerolatency',
               '-b:v', '2500k',
               '-maxrate', '2500k',
               '-bufsize', '5000k',
               '-pix_fmt', 'yuv420p',
               '-g', str(fps),
               '-c:a', 'aac',
               '-b:a', '128k',
               '-ar', '44100',
               '-ac', '2',
               '-f', 'flv',
               f"rtmp://a.rtmp.youtube.com/live2/{stream_id}"]

    proc = subprocess.Popen(command, stdin=subprocess.PIPE)

    while True:
        frame = next(frame_generator)
        proc.stdin.write(frame.tobytes())

if __name__ == "__main__":
    # Authenticate the YouTube service
    youtube = get_authenticated_service()

    # Create a new live event and get the event ID and live chat ID
    event_id, live_chat_id = create_live_event(youtube, "Console Output Live Stream", "Live streaming console output", "2023-03-26T00:00:00Z", "2023-03-26T01:00:00Z")

    # Print the live event ID and live chat ID
    print(f"Live Event ID: {event_id}, Live Chat ID: {live_chat_id}")

    # Get the stream ID from your live event
    stream_id = youtube.liveBroadcasts().list(
        part="cdn",
        id=event_id
    ).execute()["items"][0]["cdn"]["ingestionInfo"]["streamName"]

    # Stream console output to YouTube
    stream_console_output_to_youtube(youtube, stream_id)