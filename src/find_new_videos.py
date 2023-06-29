import os
import json
from youtubesearchpython import *
from db_connection import connect_to_db
import logging
from new_video_workflow import initiate_workflow_for_video

# find all file names in data/raw and extract their IDs
# connect to planetscale Db and query videoDimension table for all video IDs
# compare the two lists and find the difference
# for all new IDs, call new_video_workflow.py with the ID as an argument

if __name__ == "__main__":
    logging.basicConfig(
        # filename="logs/find_new_videos.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s - %(message)s",
    )
    logging.info("Running find_new_videos.py")

    # get all video IDs from data/raw
    raw_video_ids = []
    for file in os.listdir("data/raw"):
        if file.endswith(".json"):
            json_file = open(f"data/raw/{file}")
            json_data = json.load(json_file)
            raw_video_ids.append(json_data["id"])

    # get all video IDs from planetscale
    db = connect_to_db()
    query = "SELECT youtubeId FROM VideoDimension"
    cursor = db.cursor()
    cursor.execute(query)
    ps_video_ids = cursor.fetchall()

    # compare the two lists and find the difference
    new_video_ids = []
    for video_id in raw_video_ids:
        if video_id not in ps_video_ids:
            new_video_ids.append(video_id)

    logging.info(f"Found {len(new_video_ids)} new videos")

    # for all new IDs, call new_video_workflow.py with the ID as an argument
    # for video_id in new_video_ids:
    logging.info(f"Processing new video: {video_id}")
    initiate_workflow_for_video(video_id)
