# app.py
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

app = Flask(__name__)

def extract_video_id(url_or_id):
    """Extract video ID from YouTube URL or return ID if already provided"""
    if 'youtube.com' in url_or_id or 'youtu.be' in url_or_id:
        # Extract video ID from various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
    else:
        # Assume it's already a video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
            return url_or_id
    
    return None

@app.route('/')
def home():
    return jsonify({
        "message": "YouTube Transcript API Service",
        "endpoints": {
            "get_transcript": "/transcript/<video_id_or_url>",
            "get_transcript_languages": "/languages/<video_id_or_url>"
        },
        "example": "/transcript/dQw4w9WgXcQ"
    })

@app.route('/transcript/<path:video_identifier>')
def get_transcript(video_identifier):
    try:
        video_id = extract_video_id(video_identifier)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL or video ID"}), 400
        
        # Get query parameters
        languages = request.args.getlist('lang')
        if not languages:
            languages = ['de', 'en']  # Default languages
        
        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        
        # Format as text if requested
        format_type = request.args.get('format', 'json')
        if format_type == 'text':
            formatter = TextFormatter()
            text = formatter.format_transcript(transcript)
            return jsonify({"video_id": video_id, "transcript": text})
        
        return jsonify({"video_id": video_id, "transcript": transcript})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/languages/<path:video_identifier>')
def get_transcript_languages(video_identifier):
    try:
        video_id = extract_video_id(video_identifier)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL or video ID"}), 400
        
        languages = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = []
        
        for transcript in languages:
            available_languages.append({
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable
            })
        
        return jsonify({
            "video_id": video_id,
            "available_languages": available_languages
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
