import os
import shutil
from pathlib import Path

import cv2
from PIL import Image

from core.logger import log


def get_frame_interval(
    interval_in_seconds: int | float | None,
    max_frames: int,
    original_fps: int,
    video_length: float,
    total_frames: int,
    delta: float = 0.03,
) -> tuple[int, int, int]:
    """Gets a frame interval."""

    delta_length = delta * video_length
    delta_frames = int(delta * total_frames)
    # analytical video length
    length = video_length - 2 * delta_length
    total_frames_delta = total_frames - 2 * delta_frames

    if (interval_in_seconds is None) and max_frames > 1:
        frame_interval = int(total_frames_delta / (max_frames - 1))
        log.debug(f"frame_interval (max_frames): {frame_interval}")
        return frame_interval, delta_frames, total_frames_delta

    if interval_in_seconds is None:
        frame_interval = total_frames_delta
        log.debug(f"frame_interval (total_frames_delta): {frame_interval}")
        return frame_interval, delta_frames, total_frames_delta

    frame_interval = int(interval_in_seconds * original_fps)
    log.debug(f"frame_interval (interval_in_seconds): {frame_interval}")
    return frame_interval, delta_frames, total_frames_delta


def extract_key_frames(
    video_path: str,
    interval_in_seconds: int,
    max_frames: int,
    video_frames_dir: str,
) -> list[tuple[Image.Image, int]]:
    """
    Extracts frames from video.
    """

    # clean temp frames directory
    frames_directory_path = Path(video_frames_dir)
    for item in frames_directory_path.glob("*"):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video {video_path}")

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_length = total_frames / original_fps  # in seconds

    log.debug(
        f"Video data: \noriginal_fps: {original_fps}"
        f"\ntotal_frames: {total_frames}"
        f"\nvideo_length: {video_length:.1f} s"
    )

    frame_interval, delta_frames, total_frames_delta = get_frame_interval(
        interval_in_seconds,
        max_frames,
        original_fps,
        video_length,
        total_frames,
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
    interval_in_seconds: int | None,
    max_frames: int,
    video_frames_dir: str,
) -> list[str]:
    """
    Gets video frames and saves them.
    """

    log.info(f"Getting frames from the video...")

    # Extract key frames
    key_frames = extract_key_frames(
        video_path, interval_in_seconds, max_frames, video_frames_dir
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
    get_video_frames(
        video_path,
        # interval_in_seconds=None,
        interval_in_seconds=50,
        max_frames=5,
        video_frames_dir="_temp/video_frames/test",
    )
