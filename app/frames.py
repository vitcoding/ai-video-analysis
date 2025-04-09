import os
import shutil
from pathlib import Path

import cv2
from PIL import Image
from pydantic import BaseModel

from core.logger import log

CLEAN_FRAMES_DIRECTORY = True


class VideoData(BaseModel):
    video_path: str

    @property
    def name(self):
        return self.video_path.split("/")[-1]


class VideoFramesManager:
    def __init__(
        self,
        video: VideoData,
        interval_in_seconds: int | float | None,
        max_frames: int,
        video_frames_dir: str,
        delta: float = 0.03,
    ) -> None:
        self.video = video
        self.interval_in_seconds = interval_in_seconds
        self.max_frames = max_frames
        self.video_frames_dir = video_frames_dir
        self.delta = delta

    def _get_frame_interval(self) -> int:
        """Gets a frame interval."""

        self.delta_length = self.delta * self.video_length
        self.delta_frames = int(self.delta * self.total_frames)
        # analytical video length
        self.analytical_length = self.video_length - 2 * self.delta_length
        self.start_frame = int(self.total_frames * self.delta)
        self.analytical_frames = self.total_frames - 2 * self.delta_frames

        if (self.interval_in_seconds is None) and self.max_frames > 1:
            frame_interval = int(
                self.analytical_frames / (self.max_frames - 1)
            )
            log.debug(f"frame_interval (max_frames): {frame_interval}")
            return frame_interval

        if self.interval_in_seconds is None:
            frame_interval = self.analytical_frames
            log.debug(f"frame_interval (total_frames_delta): {frame_interval}")
            return frame_interval

        frame_interval = int(self.interval_in_seconds * self.original_fps)
        log.debug(f"frame_interval (interval_in_seconds): {frame_interval}")
        return frame_interval

    def clean_frames_directory(self):
        frames_directory_path = Path(self.video_frames_dir)
        for item in frames_directory_path.glob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    def _extract_key_frames(
        self, clean_frames_dir: bool = CLEAN_FRAMES_DIRECTORY
    ) -> list[tuple[Image.Image, int]]:
        """
        Extracts frames from video.
        """

        if clean_frames_dir:
            # clean frames directory
            self.clean_frames_directory()

        cap = cv2.VideoCapture(self.video.video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video {self.video.video_path}")

        self.original_fps = cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_length = self.total_frames / self.original_fps  # in seconds
        log.debug(
            f"Video data: \noriginal_fps: {self.original_fps}"
            f"\ntotal_frames: {self.total_frames}"
            f"\nvideo_length: {self.video_length:.1f} s"
        )
        self.frame_interval = self._get_frame_interval()

        frames = []
        frame_count = 1

        while frame_count < (self.analytical_frames + self.delta_frames):
            ret, frame = cap.read()

            if frame_count < self.delta_frames:
                frame_count += 1
                continue

            if not ret:
                break

            if (frame_count - self.delta_frames) % self.frame_interval == 0:
                # Convert BGR (OpenCV) to RGB (Pillow)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append((Image.fromarray(frame_rgb), frame_count))

            frame_count += 1

        if self.interval_in_seconds is not None or self.max_frames < 3:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append((Image.fromarray(frame_rgb), frame_count))

        cap.release()
        return frames

    def get_video_frames(self) -> list[str]:
        """
        Gets video frames and saves them.
        """

        log.info(f"Getting frames from the video...")

        # Extract key frames
        key_frames = self._extract_key_frames()

        image_paths = []

        counter = 1
        for frame, i in key_frames:

            # Save a frame image
            if not os.path.exists(self.video_frames_dir):
                os.makedirs(self.video_frames_dir)
            temp_image_path = f"{self.video_frames_dir}/temp_frame_{i}.jpg"
            frame.save(temp_image_path)
            image_paths.append(temp_image_path)

            counter += 1

        log.debug(f"image_paths: \n{image_paths}")
        return image_paths


if __name__ == "__main__":
    video_path = "_temp/video.mp4"
    video = VideoData(video_path=video_path)
    frames_manager = VideoFramesManager(
        video,
        # interval_in_seconds=50,
        interval_in_seconds=None,
        max_frames=2,
        video_frames_dir="_temp/video_frames/test",
    )
    frames_manager.get_video_frames()
