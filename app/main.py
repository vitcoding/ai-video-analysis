import os

import ollama

from core.logger import log
from frames import get_video_frames
from prompts.video_frames_analysis import video_frame_prompt
from prompts.video_frames_summary import get_summary_prompt

# LLM_MODEL = "llava:7b"
LLM_MODEL = "llama3.2-vision:11b"


def analyze_video_frames(
    video_path: str, prompt: str, remove_images: bool = False
):
    """
    Analyzes video frames using vision model.
    """

    # Extract key frames
    image_paths = get_video_frames(
        video_path, interval_in_seconds=3, max_frames=3
    )

    responses = []

    for i, image_path in enumerate(image_paths):
        log.info(f"\n\nProcessing frame {i+1}/{len(image_paths)}...")

        try:
            response = ollama.generate(
                model=LLM_MODEL,
                prompt=prompt,
                images=[image_path],
                stream=False,
            )
            log.debug(f"model response: {response}")

            responses.append(response["response"])

        finally:
            # Remove temporary file
            if remove_images and os.path.exists(image_path):
                os.remove(image_path)

    # Combine all responses
    full_response = "\n".join(
        [
            f"Frame {i+1} analysis:\n{resp}\n"
            for i, resp in enumerate(responses)
        ]
    )

    return full_response


def summarize_video_frames(frames_analysis_result: str) -> str:
    """
    Summarizes video_frames analysis.
    """

    log.info(f"\n\nSummarizing the video frames data...")

    prompt = get_summary_prompt(frames_analysis_result)
    summary_response = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt,
        stream=False,
    )

    log.debug(f"summary_response: \n{summary_response}")
    return summary_response["response"]


def main():
    """
    The main function of video frames analysis.
    """

    # Verify video exists
    video_path = "_temp/video.mp4"
    if not os.path.exists(video_path):
        log.error(f"Error: Video '{video_path}' not found in root directory!")
        return

    # Verify model is available
    try:
        ollama_show = ollama.show(LLM_MODEL)
        # log.debug(f"ollama_show: {ollama_show}")
    except:
        log.info(f"Downloading '{LLM_MODEL}' model...")
        ollama.pull(LLM_MODEL)

    log.info(f"Analyzing video {video_path}...")
    analysis_result = analyze_video_frames(
        video_path, video_frame_prompt, remove_images=False
    )

    log.info(f"\nVideo analysis results: \n{analysis_result}")

    summary = summarize_video_frames(analysis_result)
    log.info(f"Summary: \n{summary}")


if __name__ == "__main__":
    main()
