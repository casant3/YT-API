from googleapiclient.discovery import build
from api_key import api_key
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#add your own api key
channel_ids = [#'UCX6OQ3DkcsbYNE6H8uQQuVA', #MrBeast
              'UCDogdKl7t7NHzQ95aEwkdMw', #Sidemen
              'UCBJycsmduvYEL83R_U4JriQ', #Marques Brownlee
              'UCq6VFHwMzcMXbuKyG7SQYIg', #penguinz0
              'UCWyDCS2xtZgab_MUlhmpQZA', #YourRAGE
              'UCqpyFHhE13LsrG5qDknJcFQ' #AfroSenju
              ]

youtube = build('youtube', 'v3', developerKey=api_key)

#function to get channel stats
def get_channel_stats(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids))
    response = request.execute()
    
    for item in response['items']:
        data = dict(Channel_name=item['snippet']['title'],
                    Subscribers=item['statistics']['subscriberCount'],
                    Views=item['statistics']['viewCount'],
                    Total_videos=item['statistics']['videoCount'],
                    Playlist_id=item['contentDetails']['relatedPlaylists']['uploads'])
        all_data.append(data)
    
    return all_data


channel_statistics = get_channel_stats(youtube, channel_ids)

channel_data = pd.DataFrame(channel_statistics)

print(channel_data)

channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])

print(channel_data.dtypes)

#ax = sns.barplot(x='Channel_name', y='Views', data=channel_data)
# plt.show()

#function to get video id
playlist_id = channel_data.loc[channel_data['Channel_name']=='Sidemen', 'Playlist_id'].values[0]
def get_video_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    video_ids = []
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken = next_page_token)
            response = request.execute()

            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            next_page_token = response.get('nextPageToken')
            
    return video_ids
    
video_ids = get_video_ids(youtube, playlist_id)

# print(video_ids)

#function to get video details
def get_video_details(youtube, video_ids):
    all_video_stats = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,statistics",
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute()

        for video in response['items']:
            video_stats = dict(Title = video['snippet']['title'],
                               Published_date = video['snippet']['publishedAt'],
                               Views = video['statistics']['viewCount'],
                               #Likes = video['statistics']['likeCount'],
                               Comments = video['statistics']['commentCount'])
            all_video_stats.append(video_stats)
            
    return all_video_stats

video_details = get_video_details(youtube, video_ids)

video_data = pd.DataFrame(video_details)

video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Comments'] = pd.to_numeric(video_data['Comments'])

print(video_data)

top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)
print(top10_videos)

#ax1 = sns.barplot(x='Views', y='Title', data=top10_videos)
# plt.show()

video_data['Month'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%b')
print(video_data)

videos_per_month = video_data.groupby('Month', as_index=False).size()
print(videos_per_month)

sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

videos_per_month.index = pd.CategoricalIndex(videos_per_month['Month'], categories = sort_order, ordered = True)
videos_per_month = videos_per_month.sort_index()

ax2 = sns.barplot(x='Month', y='size', data = videos_per_month)
plt.show()