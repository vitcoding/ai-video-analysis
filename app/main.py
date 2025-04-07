import os

import cv2
import ollama
from PIL import Image

from prompts.video_frames_analysis import video_frame_prompt


def extract_key_frames(video_path, max_frames=5, target_fps=0.05):
    """
    Extracts key frames from video with reduced frame rate.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video {video_path}")

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(original_fps / target_fps) if target_fps > 0 else 1
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames = []
    frame_count = 0

    while len(frames) < max_frames and frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            # Convert BGR (OpenCV) to RGB (Pillow)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame_rgb))

        frame_count += 1

    cap.release()
    return frames


def analyze_video_frames(video_path, prompt):
    """
    Analyzes video frames using LLM vision model.
    """
    # Extract key frames
    key_frames = extract_key_frames(video_path)

    responses = []

    for i, frame in enumerate(key_frames):
        print(f"Processing frame {i+1}/{len(key_frames)}...")

        # Save temporary image
        temp_image_path = f"temp_frame_{i}.jpg"
        frame.save(temp_image_path)

        try:
            # Send to LLaVA via Ollama
            response = ollama.generate(
                model="llama3.2-vision:11b",
                # model="llava:7b",
                prompt=prompt,
                images=[temp_image_path],
                stream=False,
            )
            print(response)

            responses.append(response["response"])

        finally:
            # Remove temporary file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    # Combine all responses
    full_response = "\n".join(
        [
            f"Frame {i+1} analysis:\n{resp}\n"
            for i, resp in enumerate(responses)
        ]
    )

    return full_response


def main():
    """
    The main function of video frames analysis.
    """

    # Verify video exists
    video_path = "_temp/video.mp4"
    if not os.path.exists(video_path):
        print(f"Error: Video {video_path} not found in root directory!")
        return

    # # Verify model is available
    # try:
    #     ollama.show("llava:7b")
    # except:
    #     print("Downloading llava:7b model...")
    #     ollama.pull("llava:7b")

    print(f"Analyzing video {video_path}...")
    analysis_result = analyze_video_frames(video_path, video_frame_prompt)

    print("\nVideo analysis results:")
    print(analysis_result)


if __name__ == "__main__":
    main()
