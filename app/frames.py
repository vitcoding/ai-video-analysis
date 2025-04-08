import os
import shutil
from pathlib import Path

import cv2
from PIL import Image

from core.logger import log


def extract_key_frames(
    video_path: str, interval_in_seconds: int, max_frames: int
) -> list[tuple[Image.Image, int]]:
    """
    Extracts frames from video.
    """

    # clean temp frames directory
    temp_frames_directory_path = Path("./_temp/video_frames")
    for item in temp_frames_directory_path.glob("*"):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video {video_path}")

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_length = total_frames / original_fps

    log.debug(
        f"Video data: \noriginal_fps: {original_fps}"
        f"\ntotal_frames: {total_frames}"
        f"\nvideo_length: {video_length:.1f} s"
    )

    DELTA = 0.03
    delta_length = DELTA * video_length
    delta_frames = int(DELTA * total_frames)
    # analytical video length
    length = video_length - 2 * delta_length
    frames_from_interval = length // interval_in_seconds

    log.debug(
        f"Key frames number: \nmax_frames: {max_frames}"
        f"\nframes_from_interval: {frames_from_interval}"
    )

    total_frames_delta = total_frames - 2 * delta_frames
    frames_number = min(frames_from_interval, max_frames - 1)
    frame_interval = (
        int(total_frames_delta / frames_number)
        if frames_number > 0
        else int(total_frames_delta / frames_from_interval)
    )

    frames = []
    frame_count = int(delta_frames)

    while frame_count < total_frames_delta:
        ret, frame = cap.read()

        if frame_count < delta_frames:
            frame_count += 1
            continue

        if not ret:
            break

        if (frame_count - delta_frames) % frame_interval == 0:
            # Convert BGR (OpenCV) to RGB (Pillow)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append((Image.fromarray(frame_rgb), frame_count))

        frame_count += 1

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frames.append((Image.fromarray(frame_rgb), frame_count))

    cap.release()
    return frames


def get_video_frames(
    video_path: str,
    interval_in_seconds: int = 5,
    max_frames: int = 5,
    video_frames_dir: str = "_temp/video_frames",
) -> list[str]:
    """
    Gets video frames and saves them.
    """

    log.info(f"Getting frames from the video...")

    # Extract key frames
    key_frames = extract_key_frames(
        video_path, interval_in_seconds, max_frames
    )

    image_paths = []

    counter = 1
    for frame, i in key_frames:

        # Save a frame image
        if not os.path.exists(video_frames_dir):
            os.makedirs(video_frames_dir)
        temp_image_path = f"{video_frames_dir}/temp_frame_{i}.jpg"
        frame.save(temp_image_path)
        image_paths.append(temp_image_path)

        counter += 1

    log.debug(f"image_paths: \n{image_paths}")
    return image_paths


if __name__ == "__main__":
    video_path = "_temp/video.mp4"
    get_video_frames(video_path)
