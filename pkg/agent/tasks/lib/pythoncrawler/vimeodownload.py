from vimeo_downloader import Vimeo

def download_vimeo_video(vimeo_url, embedded_on, directory, name):
    if (vimeo_url != "https://player.vimeo.com/video/"):
        v = Vimeo(vimeo_url, embedded_on)

        # >> [Stream(240p), Stream(360p), Stream(540p), Stream(720p), Stream(1080p)]
        s = v.streams
        selected_stream = s[2]  # 540P

        selected_stream.download(download_directory = directory, filename = name)