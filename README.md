# HuberData

Repo to collect, transform, and upload Huberman video data so that it can be used by huberx.com

### Steps followed

- Everyday at 1 am a cron job will trigger src/daily_video_search.sh

  - This will download new video meta data to data/raw
  - Trigger python script to check if new video added that doesn't exist in Db
  - If new video added, run new video adding workflow
    - From raw data --> add meta data to MySQL Db
    - From video data --> Transcribe full video --> upload transcription to MYSQL and Pinecone
    - From transcription --> add FAQs, summary, detailed summary --> Upload to MYSQL
    - Notify on discord when complete

- videoDimension will have the following columns
  - id
  - youtubeId
  - title
  - description
  - uploadedAt
  - transcription
  - transcribedAt
  - summary
  - summaryAt
  - detailedSummary
  - detailedSummaryAt
