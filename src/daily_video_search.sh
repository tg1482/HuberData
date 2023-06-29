# File to download all videos from a channel

youtube-dl --ignore-errors --write-info-json -o "../data/raw/%(id)s.%(ext)s" --skip-download --no-overwrites --max-downloads 5 "https://www.youtube.com/channel/UC2D2CMWXMOVWx7giW1n3LIg"
echo "Done"

# run python script in src/find_new_videos.py
python find_new_videos.py