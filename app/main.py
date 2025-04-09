import os

import ollama

from core.logger import log
from frames import VideoData, VideoFramesManager
from prompts.video_frames_analysis import video_frame_prompt
from prompts.video_frames_summary import get_summary_prompt

# LLM_MODEL = "llava:7b"
LLM_MODEL = "llama3.2-vision:11b"


def analyze_video_frames(
    video_path: str,
    prompt: str,
    interval_in_seconds: int | float | None,
    max_frames: int,
    remove_images: bool = False,
):
    """
    Analyzes video frames using vision model.
    """

    # Extract key frames
    frames_directory = "_temp/video_frames"
    video = VideoData(video_path=video_path)
    directory_name = video.name.replace(".", "_")
    video_frames_dir = f"{frames_directory}/{directory_name}"
    frames_manager = VideoFramesManager(
        video,
        interval_in_seconds=interval_in_seconds,
        max_frames=max_frames,
        video_frames_dir=video_frames_dir,
    )
    # os.makedirs(video_frames_dir)
    image_paths = frames_manager.get_video_frames()
    log.debug(f"\nimage_paths: \n{image_paths}")

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


def main(
    video_path: str,
    interval_in_seconds: int | float | None,
    max_frames: int,
) -> None:
    """
    The main function of video frames analysis.
    """

    # Verify video exists
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
        video_path,
        video_frame_prompt,
        interval_in_seconds=interval_in_seconds,
        max_frames=max_frames,
        remove_images=False,
    )

    log.info(f"\nVideo analysis results: \n{analysis_result}")

    summary = summarize_video_frames(analysis_result)
    log.info(f"Summary: \n{summary}")


if __name__ == "__main__":
    main(
        "_temp/video.mp4",
        interval_in_seconds=None,
        max_frames=2,
    )
