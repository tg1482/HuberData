import json
import torch
import time, os
import logging
import whisper
import numpy as np
import pandas as pd
from youtubesearchpython import *
import yt_dlp
import requests
from db_connection import connect_to_db


# Whisper model
class WhisperModel:
    def __init__(self):
        if torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
        print(f"Using device: {device}")
        self.model = whisper.load_model("medium", device=device)

    def transcribe(self, audio):
        return self.model.transcribe(audio)


# Get Video info
def get_video_info(video_id):
    json_file = open(f"data/raw/{video_id}.info.json")
    json_data = json.load(json_file)
    video_id = json_data["id"]
    video_id = "dgzJ_DMo4rg"
    video_data = {
        "id": video_id,
        "title": json_data["title"],
        "description": json_data["description"],
        "upload_date": json_data["upload_date"],
        "view_count": json_data["view_count"],
        "duration": json_data["duration"],
        "img_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
    }
    return video_data


# Download video
def download_video(video_data):
    youtube_id = video_data["id"]
    print(f"Downloading video: {youtube_id}")

    # Construct video URL and thumbnail image URL
    ep_link = f"https://www.youtube.com/watch?v={youtube_id}"

    audio_dir = "data/audio"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    # Write audio
    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "outtmpl": f"{audio_dir}/{youtube_id}.m4a",
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([ep_link])

    if error_code == 0:
        print(f"Download successful: {youtube_id}")
    else:
        print(f"Download failed: {youtube_id}")


# Get video transcript
def transcribe_video(video_id):
    print(f"Transcribing video: {video_id}")
    whisper_model = WhisperModel()

    # Paths for the audio and transcription files
    audio_file_path = f"data/audio/{video_id}.m4a"
    audio_transcription_dir = "data/transcript"

    if not os.path.exists(audio_transcription_dir):
        os.makedirs(audio_transcription_dir)

    out_file_path = f"{audio_transcription_dir}/{video_id}.txt"

    print(f"Processing file: {audio_file_path}")
    start_time = time.time()

    # Transcribe audio file
    result = whisper_model.transcribe(audio_file_path)

    transcription = []

    # Write transcription to file
    with open(out_file_path, "w") as f:
        for seg in result["segments"]:
            ts = np.round(seg["start"], 1)
            line = f"{video_id}&t={ts}s\t{ts}\t{seg['text']}\n"
            f.write(line)
            transcription.append(line)

    end_time = time.time()
    time_diff = end_time - start_time
    print(f"Time taken: {time_diff:.2f} seconds")

    return transcription


# Add video info to database
def add_video_info_to_db(video_data):
    # Connect to the database
    db = connect_to_db()

    # Create a cursor object
    cursor = db.cursor()

    # SQL query to insert video info into the videoDimension table
    add_video_info_query = (
        "INSERT INTO VideoDimension (youtubeId, title, description, uploadedAt) "
        "VALUES (%s, %s, %s, %s)"
    )

    # Video data to be inserted
    video_info_data = (
        video_data["id"],
        video_data["title"],
        video_data["description"],
        video_data["upload_date"],
    )

    # Execute the query and commit the transaction
    cursor.execute(add_video_info_query, video_info_data)
    db.commit()

    # Close the cursor and connection
    cursor.close()
    db.close()


# Add video transcript to database
def add_transcription_to_db(youtube_id, transcription):
    # Connect to the database
    db = connect_to_db()

    # Create a cursor object
    cursor = db.cursor()

    # SQL query to update the transcription of the video in the videoDimension table
    add_transcription_query = "UPDATE VideoDimension SET transcription = %s, transcribedAt = NOW() WHERE youtubeId = %s"

    # Execute the query and commit the transaction
    cursor.execute(add_transcription_query, (transcription, youtube_id))
    db.commit()

    # Close the cursor and connection
    cursor.close()
    db.close()


# Initiate workflow for video
def initiate_workflow_for_video(youtube_id):
    logging.info(f"Initiating workflow for video: {youtube_id}")
    video_data = get_video_info(youtube_id)

    logging.info(f"Adding video info to database: {youtube_id} | {video_data['title']}")
    add_video_info_to_db(video_data)

    logging.info(f"Downloading video: {youtube_id} | {video_data['title']}")
    download_video(video_data)

    youtube_id = "dgzJ_DMo4rg"
    logging.info(f"Transcribing video: {youtube_id} | {video_data['title']}")
    transcription = transcribe_video(youtube_id)

    logging.info(
        f"Writing transcription to database: {youtube_id} | {video_data['title']}"
    )
    add_transcription_to_db(youtube_id, transcription)

    logging.info(f"Workflow complete for video: {youtube_id} | {video_data['title']}")
