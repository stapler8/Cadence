# import youtube_dl as ytdl
import yt_dlp as ytdl
import discord

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist",
    "compat-options": "filename"
}


class Video:
    """Class containing information about a particular video."""

    def __init__(self, info, requested_by):
        """Plays audio from (or searches for) a URL."""
        if "webpage_url" in info:
            self.video_url = info["webpage_url"]
        else:
            self.video_url = "https://www.youtube.com/watch?v=" + info["id"]
        self.title = info["title"]
        self.uploader = info["uploader"] if "uploader" in info else ""
        self.requested_by = requested_by

    def get_embed(self):
        """Makes an embed out of this Video's information."""
        embed = discord.Embed(
            title=self.title, description=self.uploader, url=self.video_url)
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.avatar)
        return embed

class Video_Full:
    """Class containing information about a particular video."""

    def __init__(self, url_or_search, requested_by):
        """Plays audio from (or searches for) a URL."""
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            video = self._get_info(url_or_search)
            video_format = video["formats"][0]
            # self.stream_url = video_format["url"]
            self.stream_url = video["url"]
            self.video_url = video["webpage_url"]
            self.title = video["title"]
            self.uploader = video["uploader"] if "uploader" in video else ""
            self.thumbnail = video[
                "thumbnail"] if "thumbnail" in video else None
            self.requested_by = requested_by

    def _get_info(self, video_url):
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            if len(video_url) == 11:
                info = ydl.extract_info("https://www.youtube.com/watch?v=" + video_url, download=False)
            else:
                info = ydl.extract_info(video_url, download=False)

            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"])  # get info for first video
            else:
                video = info
            return video

    def get_embed(self):
        """Makes an embed out of this Video's information."""
        embed = discord.Embed(
            title=self.title, description=self.uploader, url=self.video_url)
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.avatar)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed

class Playlist:
    """Class to handle both playlist and video links."""

    def __init__(self, url_or_search, requested_by):
        """Plays audio from (or searches for) a URL."""
        self.playlist, info = self._get_info(url_or_search, requested_by)
#        video_format = video["formats"][0]
#        self.stream_url = video_format["url"]
        self.playlist_url = info["webpage_url"]
        self.title = info["title"] if "title" in info else ""
        self.uploader = info["uploader"] if "uploader" in info else ""
        self.requested_by = requested_by

    def _get_info(self, video_url, requested_by):
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if "_type" in info and info["_type"] == "playlist":
                videos = [Video(e, requested_by) for e in info["entries"]]
            else:
                videos = [Video(info, requested_by)]
            return videos, info

    def get_embed(self):
        """Makes an embed out of this Video's information."""
        embed = discord.Embed(
            title=self.title, description=self.uploader, url=self.playlist_url)
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.avatar)
        return embed
