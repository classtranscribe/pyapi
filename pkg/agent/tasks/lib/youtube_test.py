
import os
os.environ['DATA_DIRECTORY']='.'

import youtube

def quick_test():
    yt=youtube.YoutubeProvider()
    pl=yt.get_youtube_playlist('PLBgxzZMu3GpPb35BDIU5eeopR4MhBOZw_')
    print(pl)
    #[{'channelId': 'UC4JRDwrS2QC4XNZnSex0Udw', 'playlistId': 'PLBgxzZMu3GpPb35BDIU5eeopR4MhBOZw_', 'title': 'STAT 385 /// Welcome', 'description': 'Course: https://stat385.org/', 'publishedAt': '2021/08/24', 'videoUrl': 'https://youtube.com/watch?v=DqHMh8nqCPw', 'videoId': 'DqHMh8nqCPw', 'createdAt': '2021/08/24'}]
    onevid = yt.download_youtube_video('https://youtube.com/watch?v=DqHMh8nqCPw') # 24 seconds typical
    print(onevid)