"""THREAD Canonical Timeline & Deterministic Time Synchronization Engine.

Enforces integer microsecond time resolution (timestamp_us) at FRAME_RATE = 24 FPS.
Guarantees cross-modal synchronization (visual frame, audio state, subtitle state) with zero float accumulation.
"""

import math
from typing import Dict, List, Optional, Tuple, Any

FRAME_RATE = 24
MICROSECONDS_PER_SECOND = 1_000_000
FRAME_DURATION_US = MICROSECONDS_PER_SECOND // FRAME_RATE  # 41,666 us per frame


def frame_to_timestamp_us(frame_index: int, frame_rate: int = FRAME_RATE) -> int:
    """Convert 0-based frame index to exact integer microsecond timestamp.
    
    Deterministic Rule: round(frame_index * 1_000_000 / frame_rate)
    """
    if frame_index < 0:
        raise ValueError(f"Invalid negative frame index: {frame_index}")
    return round(frame_index * MICROSECONDS_PER_SECOND / frame_rate)


def timestamp_us_to_frame(timestamp_us: int, frame_rate: int = FRAME_RATE) -> int:
    """Convert integer microsecond timestamp to 0-based frame index.
    
    Deterministic Rule: round(timestamp_us * frame_rate / 1_000_000)
    """
    if timestamp_us < 0:
        raise ValueError(f"Invalid negative timestamp_us: {timestamp_us}")
    return round(timestamp_us * frame_rate / MICROSECONDS_PER_SECOND)


class SubtitleCue:
    """Represents a validated subtitle cue aligned to the canonical timeline."""

    def __init__(
        self,
        cue_id: str,
        start_us: int,
        end_us: int,
        text: str,
        speaker: Optional[str] = None,
        shot_id: Optional[str] = None,
        narrative_event_id: Optional[str] = None,
    ):
        if start_us >= end_us:
            raise ValueError(f"Invalid subtitle cue duration: start_us ({start_us}) >= end_us ({end_us})")

        self.cue_id = cue_id
        self.start_us = start_us
        self.end_us = end_us
        self.text = text
        self.speaker = speaker
        self.shot_id = shot_id
        self.narrative_event_id = narrative_event_id

    @property
    def start_frame(self) -> int:
        return timestamp_us_to_frame(self.start_us)

    @property
    def end_frame(self) -> int:
        return timestamp_us_to_frame(self.end_us)

    def is_active_at_frame(self, frame_index: int) -> bool:
        ts = frame_to_timestamp_us(frame_index)
        return self.start_us <= ts < self.end_us


class AudioEvent:
    """Represents a validated audio playback event aligned to the canonical timeline."""

    def __init__(
        self,
        audio_id: str,
        start_us: int,
        end_us: int,
        source: str,
        volume: float = 1.0,
        fade_in_us: int = 0,
        fade_out_us: int = 0,
        shot_id: Optional[str] = None,
        narrative_event_id: Optional[str] = None,
    ):
        if start_us >= end_us:
            raise ValueError(f"Invalid audio event duration: start_us ({start_us}) >= end_us ({end_us})")

        self.audio_id = audio_id
        self.start_us = start_us
        self.end_us = end_us
        self.source = source
        self.volume = max(0.0, min(1.0, volume))
        self.fade_in_us = fade_in_us
        self.fade_out_us = fade_out_us
        self.shot_id = shot_id
        self.narrative_event_id = narrative_event_id

    @property
    def start_frame(self) -> int:
        return timestamp_us_to_frame(self.start_us)

    @property
    def end_frame(self) -> int:
        return timestamp_us_to_frame(self.end_us)

    def is_active_at_frame(self, frame_index: int) -> bool:
        ts = frame_to_timestamp_us(frame_index)
        return self.start_us <= ts < self.end_us


class CanonicalTimeline:
    """Unified master timeline that manages deterministic visual, audio, and subtitle states."""

    def __init__(self, duration_us: int = 60_000_000, frame_rate: int = FRAME_RATE):
        self.duration_us = duration_us
        self.frame_rate = frame_rate
        self.total_frames = timestamp_us_to_frame(duration_us, frame_rate)

        self.subtitles: List[SubtitleCue] = []
        self.audio_events: List[AudioEvent] = []
        self.shots: Dict[str, Tuple[int, int]] = {}  # shot_id -> (start_us, end_us)

    def add_subtitle_cue(self, cue: SubtitleCue):
        self.subtitles.append(cue)
        self.subtitles.sort(key=lambda c: c.start_us)

    def add_audio_event(self, event: AudioEvent):
        self.audio_events.append(event)
        self.audio_events.sort(key=lambda e: e.start_us)

    def register_shot(self, shot_id: str, start_us: int, end_us: int):
        self.shots[shot_id] = (start_us, end_us)

    def get_frame_state(self, frame_index: int) -> Dict[str, Any]:
        """Returns the exact, deterministic cross-modal state for a given frame_index."""
        if frame_index < 0 or frame_index >= self.total_frames:
            raise IndexError(f"Frame index {frame_index} out of bounds [0, {self.total_frames - 1}]")

        ts_us = frame_to_timestamp_us(frame_index, self.frame_rate)

        # Resolve Active Shot
        active_shot_id = None
        shot_local_frame = 0
        shot_local_time_us = 0
        for s_id, (s_start, s_end) in self.shots.items():
            if s_start <= ts_us < s_end:
                active_shot_id = s_id
                shot_local_time_us = ts_us - s_start
                shot_local_frame = timestamp_us_to_frame(shot_local_time_us, self.frame_rate)
                break

        # Resolve Active Subtitles
        active_subtitles = [c.text for c in self.subtitles if c.is_active_at_frame(frame_index)]

        # Resolve Active Audio
        active_audio = [e.audio_id for e in self.audio_events if e.is_active_at_frame(frame_index)]

        return {
            "frame_index": frame_index,
            "timestamp_us": ts_us,
            "time_seconds": ts_us / MICROSECONDS_PER_SECOND,
            "shot_id": active_shot_id,
            "shot_local_frame": shot_local_frame,
            "shot_local_time_us": shot_local_time_us,
            "subtitles": active_subtitles,
            "audio_events": active_audio,
        }
