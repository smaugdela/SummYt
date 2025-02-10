from pathlib import Path
from mistralai import Mistral
from youtube_transcript_api import YouTubeTranscriptApi
import argparse
import os
from icecream import ic


LANG_OPTIONS = ('en', 'fr', 'de', 'es', 'it', 'nl', 'pt', 'ru', 'ja', 'ko', 'zh-CN', 'zh-TW', 'ar', 'el')
LANG_MAPPING = {
    "en": "English",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "nl": "Dutch",
    "pt": "Portuguese",
    "pl": "Polish",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "ar": "Arabic",
    "el": "Greek",
}


# # extract video ID with regex
# def extract_video_id(youtube_url):
#     import re

#     video_id_regex = r'(?:v=|/)([0-9A-Za-z_-]{11}).*'
#     match = re.search(video_id_regex, youtube_url)

#     if match:
#         return match.group(1)
#     else:
#         return None


# @retry(stop=stop_after_delay(10))
def get_video_info(youtube_url):

    try:
        from pytubefix import YouTube
        yt = YouTube(youtube_url)

        # Get available captions among the supported languages
        available_captions = yt.captions
        # Find the language code inside each caption description
        available_captions_language_codes = [str(caption.code).split(".")[-1] for caption in available_captions]

        info = {
            "title": yt.title,
            "id": yt.video_id,
            "captions": available_captions_language_codes,
            "thumbnail_url": yt.thumbnail_url
        }
    except RuntimeError:
        raise RuntimeError("Could not extract video information. Please check the video is available and not age-restricted.")

    return info


# The program takes the URL of a youtube video as parameter using argparse
def main(youtube_url: str, lang: str, output_directory: str = "."):

    video_info = get_video_info(youtube_url)
    ic(video_info)

    # Check if the language is supported
    if lang not in LANG_OPTIONS:
        raise ValueError(f"Language \'{LANG_MAPPING[lang]}\' is not supported. Please choose among: {LANG_MAPPING}")
    if lang not in video_info["captions"]:
        # lang is the first of LANG_OPTIONS that is available
        old_lang = lang
        lang = next((x for x in LANG_OPTIONS if x in video_info["captions"]), None)
        print(f"WARNING: Language \'{LANG_MAPPING[old_lang]}\' is not available for this video and will be performed in \'{LANG_MAPPING[lang]}\'. Please choose among: {video_info['captions']}")

    # get transcript
    transcript = YouTubeTranscriptApi.get_transcript(video_info["id"], languages=(lang,))

    # extract transcript
    text_list = [transcript[i]['text'] for i in range(len(transcript))]
    transcript_text = '\n'.join(text_list)

    # Get thumbnail
    thumbnail_url = video_info["thumbnail_url"]

    # Setup Mistral API
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-small-latest"

    client = Mistral(api_key=api_key)

    prompt = f"""
    Please summarize the following video transcript in a concise manner.
    Organize the information into chapters and subchapters if applicable.
    Return the summary as a markdown-formatted text.
    Always create at least an abstract at the begining and a conclusion at the end of your summary.
    Do not mention that you are summarizing the transcript of a video.
    Focus on extracting the most important details and key points.
    Keep the summary as brief as possible while retaining essential information and keywords. You can quote the transcript if relevant.
    Finally, make sure the summary is in the following language: {LANG_MAPPING[lang]}.
    -----
    Transcript:
    \"{transcript_text}\"
    """
    ic(prompt)

    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    # Save the summary to a markdown file
    summary = chat_response.choices[0].message.content

    header = f"# \"{video_info['title']}\"\n\n"
    header += f"![Thumbnail]({thumbnail_url})\n\n"
    summary = header + summary

    filename = Path(output_directory) / (video_info["title"].replace(" ", "_").lower() + ".md")
    with open(filename, "w") as f:
        f.write(summary)
    print(f"Summary saved to {filename}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Summarize a YouTube video transcript')
    parser.add_argument('youtube_url', type=str, help='URL of the YouTube video')
    parser.add_argument('--lang', type=str, default='en', help=f'Wanted language of the summary (although it might not be available), among: {LANG_OPTIONS}')
    parser.add_argument('--output_directory', type=str, default='.', help='Output directory for the summary file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    if args.debug:
        ic.enable()
    else:
        ic.disable()

    youtube_url = args.youtube_url
    lang = args.lang
    output_directory = args.output_directory

    main(youtube_url, lang, output_directory)
