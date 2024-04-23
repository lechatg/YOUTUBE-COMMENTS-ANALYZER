from googleapiclient.discovery import build
import os
import pandas as pd

# Initialize the YouTube API Client:
# Here, we’re using the build function from googleapiclient.discovery to initialize 
# the YouTube API client with the provided API key.
api_service_name = "youtube"
api_version = "v3"

# To access variable from environment we first need to set it there (for example with export command in CLI)
DEVELOPER_KEY = os.environ.get("YT_API_DEVELOPER_KEY_1")

# Set how many comments is allowed to parse per video (consider that 10,000 comments is 1% of free YouTube daily quota) 
MAX_NUMBER_OF_COMMENTS_TO_PARSE = 2000

youtube = build(api_service_name, api_version, developerKey = DEVELOPER_KEY)

# Parse yt comments (up to MAX_NUMBER...), store them dataframe and return df
def youtube_parse_comments(link):
    url = link
    video_id = url.split('v=')[1]
  
    # Set Up the API Request:
    request = youtube.commentThreads().list(
            # maximum maxResults is 100, so it is most cheap option in terms of API quota cost
            maxResults=100,
            # I only need comments (first in threads), if you also need replies - then part="snippet,replies"
            part="snippet",
            videoId=video_id,
            textFormat="plainText"
        )

    list_of_comment_dicts = []

    # Iterate Through Paginated Results: The YouTube API returns paginated results. 
    # The while loop ensures we fetch all pages of comments:
    count = 0
    while request:
        
        try:
            response = request.execute()

            for item in response['items']:
                    # Extracting comments
                    comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                    number_of_likes = item['snippet']['topLevelComment']['snippet']['likeCount']
                    number_of_replies = item['snippet']['totalReplyCount']
                    time_when_posted = item['snippet']['topLevelComment']['snippet']['publishedAt']

                    new_comment_dict = {'comment_text': comment,'author_name': author, 'likes': number_of_likes, 
                                        'replies': number_of_replies, 'published_at': time_when_posted}
                    list_of_comment_dicts.append(new_comment_dict)

            count = count + 100
            if count < MAX_NUMBER_OF_COMMENTS_TO_PARSE:
                pass
            else:
                break
                    
            # Get next page of comments
            # Put nextPageToken into request's pageToken. 
            # If this is last page - value will be none and response = request.execute() will fail with error: 'nextPageToken' so loop will break.
            request = youtube.commentThreads().list(
                maxResults=100,
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                pageToken = response['nextPageToken']
                )        

        except Exception as e:
            print(f'error: {str(e)}')
            break

    print(f'\nNumber of parsed comments: {len(list_of_comment_dicts)}')

    # create dataframe
    df = pd.DataFrame(list_of_comment_dicts)

    # Optionally save parsed comments in csv
    # df.to_csv(f"parsed_csv_files/{video_id}_user_comments.csv", index=False, header=True, encoding='utf-8')
    
    return df

# Check if video exists, and return its name
def youtube_parse_name(link):
    url = link
    video_id = url.split('v=')[1]

    # Set Up the API Request:
    request_for_video_name = youtube.videos().list(maxResults=10, part= ["snippet"], id=video_id)
    
    try:
        response = request_for_video_name.execute()
        
    except Exception as e:
        print(str(e))
        return False

    number_of_found_videos = response['pageInfo']['totalResults']

    if number_of_found_videos == 1:
        video_title = response['items'][0]['snippet']['title']
        return video_title

    if number_of_found_videos == 0:
        return False