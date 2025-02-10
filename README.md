# SummYt

SummYt is a command-line tool that downloads a video's transcript from YouTube and summarizes it using Mistral AI. It supports multiple languages and saves the summary as a Markdown file.

## Installation

1. Clone or download this repository.  
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (Make sure you have Python 3.7+ installed.)

3. Set the environment variable:
   ```bash
   export MISTRAL_API_KEY=YOUR_MISTRAL_API_KEY
   ```

## Usage

Run the script with:
```bash
python SummYt.py <youtube_url> [--lang LANG_CODE] [--output_directory PATH] [--debug]
```

- **youtube_url**: The YouTube link you want to summarize.  
- **--lang**: Target language for the summary (defaults to `en`).  
- **--output_directory**: Output directory for the resulting Markdown file (defaults to `.`).  
- **--debug**: Enables debug output with icecream.

Example:
```bash
python SummYt.py https://www.youtube.com/watch?v=abcd1234 --lang fr --output_directory summaries
```

## Supported Languages

SummYt checks captions for availability and falls back if the requested language is not available. Common options include:
```
en, fr, de, es, it, nl, pt, ru, ja, ko, zh-CN, zh-TW, ar, el
```

## How It Works

1. Extracts metadata about the YouTube video and checks for supported subtitle languages.  
2. Retrieves the transcript with `youtube_transcript_api`.  
3. Sends the transcript text to Mistral AI to generate a concise summary in the specified language.  
4. Saves the summary as a Markdown file with a title and thumbnail.

## License

This project is provided as-is. Refer to individual dependencies for their licenses.