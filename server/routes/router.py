from fastapi import Request, APIRouter
from TTS.api import TTS
import torch
import whisper
from whisper.utils import get_writer
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import re
from typing import List
import time
import os
from moviepy import VideoFileClip, AudioFileClip, ColorClip, TextClip, ImageClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from datetime import datetime

client = genai.Client(api_key="YOUR_API_KEY_HERE")  # Replace with your actual API key

router = APIRouter()

def generate_script_from_topic(topic):
    script_prompt = f"""
    Write a short, simple, and visually descriptive script (story) based on the topic: "{topic}".
    
    The script should:
    - Be suitable for a short 30-second voiceover using text-to-speech (TTS)
    - Use clear, short sentences (exactly 8 words per sentence or less than 8 words. but not more than 8 words not a single word more(not even a character))
    - Be easy to visualize, with each sentence describing a specific scene or moment
    - Show progression over time, like a simple story or timeline
    - Avoid abstract imagery (no metaphors or symbols—only real-world visuals)
    - Avoid complex vocabulary, long dialogue, or technical jargon
    - Be written in a calm, neutral narrator voice
    - Use simple language and short sentences
    
    Output just the script as plain text, without numbering, timestamps, or any extra formatting.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=script_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
        ),
    )
    return response.text.strip()

def generate_audio_from_script(projectName, script):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False).to(device)
    output_folder = f"./videos/{projectName}"
    os.makedirs(output_folder, exist_ok=True)
    tts.tts_to_file(
        text=script,
        file_path=os.path.join(output_folder, "output1.wav"),
    )
    return f"{output_folder}/output1.wav"

def generate_subtitles_from_audio(projectName, audio_path):
    model = whisper.load_model("base.en")
    result = model.transcribe(
        audio_path,
        language="en",
        word_timestamps=True,
        task="transcribe"
    )
    writer = get_writer("srt", f"./videos/{projectName}")
    writer(
        result, audio_path, {
            "max_line_count": 1,
            "max_words_per_line": 8,
        }
    )
    return f"./videos/{projectName}/output1.srt"

def parse_srt_file(srt_path: str) -> List[dict]:
    """Parses an .srt file and returns a list of subtitle entries with timestamps and text."""
    print(f"Parsing SRT file: {srt_path}")
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"SRT file not found: {srt_path}")
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    pattern = re.compile(r'(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3})\s-->\s(\d{2}:\d{2}:\d{2},\d{3})\s+([\s\S]*?)(?=\n\d+\n|\Z)')
    matches = pattern.findall(content)

    subtitles = []
    for match in matches:
        index, start, end, text = match
        text = text.strip().replace('\n', ' ')
        subtitles.append({
            "index": int(index),
            "start": start,
            "end": end,
            "text": text
        })
    return subtitles

def generate_image_prompts_from_srt(srt_path: str, topic: str) -> List[str]:
    """Generates image prompts using Gemini API from an SRT file."""
    subtitles = parse_srt_file(srt_path)

    script_blocks = "\n".join(
        f"{entry['index']}\n{entry['start']} --> {entry['end']}\n{entry['text']}\n"
        for entry in subtitles
    )

    main_prompt = f"""
    I have a short script with subtitles and timestamps from a video. and topic of video is "{topic}".
    I want to generate detailed and creative (sometimes 3d rendered or which is best for particular scene) 
    image prompts for each subtitle line (in most of the cases but skip prompt for continuation of the previous 
    scene like and, or, etc. so it won't feed it to AI as this will be dynamic) 
    to use in AI-based image generation (gemini-2.0-flash-preview-image-generation).
    And also if a particular subtitle line is not perfect to use it for image generation prompt or it is
    continuation of the previous scene then do not skip it, just go through the whole script and then 
    generate a prompt for that subtitle line related to it's continuation of the previous scene which best fit to it. 
    only skip prompt for a subtitle line if it's duration is less than 1.0 seconds.
    
    The goal is to create a visual scene that matches the mood, setting, and action described.
    For each subtitle section, give me a vivid, visually rich image prompt. 
    Focus on cinematic details like lighting, time of day, setting, atmosphere, emotions, and characters. 

    Give me prompts in the given format:
    **Subtitle 1:**
    **Text:**
    **Prompt:**
    
    Script with timestamps:
    {script_blocks}
    """

    # response = model.generate_content(main_prompt)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=main_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
        ),
    )
    return response.text.strip().split('\n')

def extract_only_prompts(image_prompts: list) -> list:
    """Extracts only the actual prompt text from Gemini's response list."""
    extracted_prompts = []
    for line in image_prompts:
        line = line.strip()
        if line.startswith("**Prompt:**"):
            prompt_text = line.replace("**Prompt:**", "").strip()
            extracted_prompts.append(prompt_text)
    return extracted_prompts

def generate_images_from_prompts(clean_prompts: list, projectName: str):
    images = []
    for i, prompt in enumerate(clean_prompts, 1):
        # print(f"Prompt {i}: {prompt}")
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
              response_modalities=['TEXT', 'IMAGE']
            )
        )
        time.sleep(1)
        for part in response.candidates[0].content.parts:
            if part.text is not None:
              print(part.text)
            elif part.inline_data is not None:
              # image_data = base64.b64decode(part.inline_data.data)
              # image = Image.open(BytesIO(image_data))   
              image = Image.open(BytesIO((part.inline_data.data)))
              image.save(f"./videos/{projectName}/image{i}.png")
              images.append(f"./videos/{projectName}/image{i}.png")
              # image.show()
        print(f"Image is generated for Prompt: {i}")
        time.sleep(1)
    return images

def srt_time_to_seconds(t: str) -> float:
    dt = datetime.strptime(t, "%H:%M:%S,%f")
    total_seconds = dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1_000_000
    return total_seconds

def generate_img_clips(subtitles_raw, images):
    # Generate image clips with accurate durations
    clips = []
    x = 0
    for i, subtitle in enumerate(subtitles_raw):
        start = srt_time_to_seconds(subtitle["start"])
        end = srt_time_to_seconds(subtitle["end"])
        duration = end - start
        
        # print(f"out of if:{x}")
        prev_start = srt_time_to_seconds(subtitles_raw[i-1]["start"])
        prev_end = srt_time_to_seconds(subtitles_raw[i-1]["end"])
        prev_duration = prev_end - prev_start
        if prev_end != start and x > 0:
            # print(f"Processing subtitle {i+1} in 1st if: {subtitle['text']} (start: {start}, end: {end}, duration: {duration})")
            pause_duration = start - prev_end
            img_clip = ImageClip(images[x-1]).with_duration(prev_duration + pause_duration)
            clips[-1] = img_clip
        if duration > 1.0:
            # print(f"Processing subtitle {i+1} in 2nd if: {subtitle['text']} (start: {start}, end: {end}, duration: {duration})")
            img_clip = ImageClip(images[x]).with_duration(duration)
            clips.append(img_clip)
            x = x + 1
        else:
            # print(f"Processing subtitle {i+1} in 1st else: {subtitle['text']} (start: {start}, end: {end}, duration: {duration})")
            # print(f"in else:{x}")
            # print(subtitles_raw[i-1])
            prev_start = srt_time_to_seconds(subtitles_raw[i-1]["start"])
            prev_end = srt_time_to_seconds(subtitles_raw[i-1]["end"])
            prev_duration = prev_end - prev_start
            if prev_end != start and x > 0:
                # print(f"Processing subtitle {i+1} in 3rd if: {subtitle['text']} (start: {start}, end: {end}, duration: {duration})")
                pause_duration = start - prev_end
                img_clip = ImageClip(images[x-1]).with_duration(prev_duration + pause_duration + duration)
                clips[-1] = img_clip
            else:
                # print(f"Processing subtitle {i+1} in 2nd else: {subtitle['text']} (start: {start}, end: {end}, duration: {duration})")
                img_clip = ImageClip(images[x-1]).with_duration(prev_duration + duration)
                clips[-1] = img_clip
    print(f"clips: {len(clips)}")
    return clips

def generate_video_from_clips(clips, audio_path, projectName):
    audio = AudioFileClip(audio_path)

    # Your factory must specify font as first arg to TextClip
    def generator(txt):
        return TextClip(
            text=txt,
            font=r"C:\Windows\Fonts\Arial\ariblk.ttf",
            font_size=24,
            color="white",
            method="caption",
             size=(1280, 200),
        )

    subtitles = SubtitlesClip(f"./videos/{projectName}/output1.srt", make_textclip=generator)
    subtitles = subtitles.with_duration(audio.duration)

    video = concatenate_videoclips(clips, method="compose")

    final = CompositeVideoClip([video, subtitles.with_position(("center", "bottom"))]).with_audio(audio)
    final.write_videofile(f"./videos/{projectName}/final_video1.mp4", fps=30)

@router.get("/")
def read_item(request: Request):
    return {"msg": "Welcome to Text To Video API"}

@router.post("/generate-script")
async def generate_script(request: Request):
    data = await request.json()
    topic = data.get("topic")
    print(f"Generating script for topic: {topic}")
    script = generate_script_from_topic(topic)
    script = script.replace("\n", " ")
    return {"script": script, "topic": topic}

@router.post("/generate-video")
async def generate_video(request: Request):
    data = await request.json()
    topic = data.get("topic")
    script = data.get("script")
    projectName = data.get("projectName")
    print(f"Generating audio for project: {projectName}")
    audio_path = generate_audio_from_script(projectName, script)
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    print(f"Audio generated at: {audio_path}")
    print(f"Generating subtitles for audio_path: {audio_path}")
    srt_path = generate_subtitles_from_audio(projectName, audio_path)
    print(f"Subtitles generated at: {srt_path}")
    print(f"Generating image prompts from subtitles: {srt_path}")
    image_prompts = generate_image_prompts_from_srt(srt_path, topic)
    print("Image prompts generated:")
    clean_prompts = extract_only_prompts(image_prompts)
    print("generating Images from prompts...")
    images = generate_images_from_prompts(clean_prompts, projectName)
    subtitles_raw = parse_srt_file(srt_path)
    # images = [f"./videos/{projectName}/image{x}.png" for x in range(1, 16)]
    clips = generate_img_clips(subtitles_raw, images)
    print("Generating video from clips...")
    generate_video_from_clips(clips, audio_path, projectName)
    print(f"Video generated for project: {projectName}")
    return {"video_path": f"/videos/{projectName}/final_video1.mp4"}