from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from yt_dlp import YoutubeDL
import re
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt

class YoutubeReader:
    def __init__(self):
        self.transcript_extracted = False
      
    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def fetch_transcript(self, video_url: str) -> str:
        pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        match = re.search(pattern, video_url)
        if match is None:
            self.logger.error("Invalid YouTube URL. Please enter a valid YouTube video URL.")
            return None
        
        video_id = match.group(6)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)

        opts = dict()
        with YoutubeDL(opts) as yt:
            info = yt.extract_info(video_url, download=False)
        information = {
                "title": info.get("title", ""),
                "transcript": formatted_transcript,
                "description": info.get("description", ""),
                "thumbnail":  info.get("thumbnails", [])[-1]["url"],
                }
                    
        return json.dumps(information, indent=2) 

# Example usage:
if __name__ == "__main__":
    tool = YoutubeReader()
    vide_url = input("Enter youtube video link: ")
    transcript = tool.fetch_transcript(vide_url)
    print(transcript)