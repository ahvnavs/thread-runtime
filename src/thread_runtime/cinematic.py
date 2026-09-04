"""Cinematic Scene Specification, Timeline Scheduler, and Validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from thread_runtime.errors import CinematicValidationError

VALID_CAMERA_FRAMINGS = {
    "extreme_wide",
    "wide",
    "medium",
    "close",
    "extreme_close",
}

VALID_CAMERA_MOVEMENTS = {
    "static",
    "pan",
    "tilt",
    "push_in",
    "pull_out",
    "tracking",
}

VALID_ACTION_TYPES = {
    "enter",
    "exit",
    "walk",
    "run",
    "stand",
    "sit",
    "look",
    "turn",
    "raise",
    "lower",
    "embrace",
    "fall",
    "speak",
}

VALID_CUE_TYPES = {
    "dialogue",
    "voice",
    "music",
    "sound_effect",
    "ambience",
}

VALID_TRANSITION_TYPES = {
    "cut",
    "fade",
    "dissolve",
    "match_cut",
}


@dataclass(frozen=True)
class Camera:
    """Cinematic camera attributes including framing, subject, and movement."""

    framing: str
    movement: str = "static"
    subject: Optional[str] = None


@dataclass(frozen=True)
class CharacterAction:
    """Authored character physical or speech action within a shot."""

    character_id: str
    action: str
    start_time_ms: int = 0
    duration_ms: Optional[int] = None
    target: Optional[str] = None


@dataclass(frozen=True)
class AudioCue:
    """Cinematic audio or dialogue cue specification."""

    cue_type: str
    asset_id: str
    start_time_ms: int = 0
    duration_ms: Optional[int] = None
    speaker_id: Optional[str] = None
    text: Optional[str] = None
    volume: float = 1.0


@dataclass(frozen=True)
class Transition:
    """Transition specification connecting shots or scenes (including match cuts)."""

    type: str
    duration_ms: int = 0
    target_scene: Optional[str] = None
    target_shot: Optional[str] = None


@dataclass(frozen=True)
class Shot:
    """Individual cinematic camera shot with timing, actions, cues, and transitions."""

    id: str
    duration_ms: int
    camera: Camera
    actions: List[CharacterAction] = field(default_factory=list)
    cues: List[AudioCue] = field(default_factory=list)
    transition: Optional[Transition] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class CinematicScene:
    """Sequenced list of cinematic shots forming a cinematic scene."""

    id: str
    title: str
    duration_ms: int
    shots: List[Shot]
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class CinematicEvent:
    """Data-only event emitted by the CinematicTimeline runtime."""

    event_type: str
    timestamp_ms: int
    details: Dict[str, Any]


def validate_cinematic_scene(data: Dict[str, Any]) -> CinematicScene:
    """Validate raw dictionary data against the Cinematic Scene specification."""
    if not isinstance(data, dict):
        raise CinematicValidationError("Cinematic scene data must be a JSON object.")

    scene_id = data.get("id")
    if not scene_id or not isinstance(scene_id, str) or not scene_id.strip():
        raise CinematicValidationError("Cinematic scene requires a non-empty 'id' string.")
    scene_id = scene_id.strip()

    scene_title = data.get("title", scene_id)
    if not isinstance(scene_title, str):
        raise CinematicValidationError(f"Cinematic scene '{scene_id}' title must be a string.")

    shots_raw = data.get("shots")
    if not shots_raw or not isinstance(shots_raw, list) or not shots_raw:
        raise CinematicValidationError(f"Cinematic scene '{scene_id}' requires a non-empty 'shots' list.")

    parsed_shots: List[Shot] = []
    seen_shot_ids: Set[str] = set()
    calculated_duration_ms = 0

    for idx, shot_raw in enumerate(shots_raw):
        if not isinstance(shot_raw, dict):
            raise CinematicValidationError(f"Shot #{idx + 1} in scene '{scene_id}' must be an object.")

        shot_id = shot_raw.get("id")
        if not shot_id or not isinstance(shot_id, str) or not shot_id.strip():
            raise CinematicValidationError(f"Shot #{idx + 1} in scene '{scene_id}' requires a non-empty 'id'.")
        shot_id = shot_id.strip()

        if shot_id in seen_shot_ids:
            raise CinematicValidationError(f"Duplicate shot ID '{shot_id}' in scene '{scene_id}'.")
        seen_shot_ids.add(shot_id)

        duration_ms = shot_raw.get("duration_ms")
        if duration_ms is None or not isinstance(duration_ms, int) or duration_ms <= 0:
            raise CinematicValidationError(
                f"Shot '{shot_id}' in scene '{scene_id}' requires a positive integer 'duration_ms'."
            )

        # Camera Validation
        cam_raw = shot_raw.get("camera")
        if not cam_raw or not isinstance(cam_raw, dict):
            raise CinematicValidationError(f"Shot '{shot_id}' in scene '{scene_id}' requires a 'camera' object.")

        framing = cam_raw.get("framing")
        if not framing or framing not in VALID_CAMERA_FRAMINGS:
            raise CinematicValidationError(
                f"Invalid camera framing '{framing}' in shot '{shot_id}'. Valid: {sorted(VALID_CAMERA_FRAMINGS)}"
            )

        movement = cam_raw.get("movement", "static")
        if movement not in VALID_CAMERA_MOVEMENTS:
            raise CinematicValidationError(
                f"Invalid camera movement '{movement}' in shot '{shot_id}'. Valid: {sorted(VALID_CAMERA_MOVEMENTS)}"
            )

        camera = Camera(
            framing=framing,
            movement=movement,
            subject=cam_raw.get("subject"),
        )

        # Character Actions Validation
        actions_raw = shot_raw.get("actions", [])
        if not isinstance(actions_raw, list):
            raise CinematicValidationError(f"Shot '{shot_id}' actions must be a list.")

        parsed_actions: List[CharacterAction] = []
        for act_idx, act_raw in enumerate(actions_raw):
            if not isinstance(act_raw, dict):
                raise CinematicValidationError(f"Action #{act_idx + 1} in shot '{shot_id}' must be an object.")
            char_id = act_raw.get("character_id")
            if not char_id or not isinstance(char_id, str):
                raise CinematicValidationError(f"Action #{act_idx + 1} in shot '{shot_id}' requires 'character_id'.")
            action_name = act_raw.get("action")
            if not action_name or action_name not in VALID_ACTION_TYPES:
                raise CinematicValidationError(
                    f"Invalid action '{action_name}' in shot '{shot_id}'. Valid: {sorted(VALID_ACTION_TYPES)}"
                )
            parsed_actions.append(
                CharacterAction(
                    character_id=char_id,
                    action=action_name,
                    start_time_ms=int(act_raw.get("start_time_ms", 0)),
                    duration_ms=act_raw.get("duration_ms"),
                    target=act_raw.get("target"),
                )
            )

        # Audio Cues Validation
        cues_raw = shot_raw.get("cues", [])
        if not isinstance(cues_raw, list):
            raise CinematicValidationError(f"Shot '{shot_id}' cues must be a list.")

        parsed_cues: List[AudioCue] = []
        for cue_idx, cue_raw in enumerate(cues_raw):
            if not isinstance(cue_raw, dict):
                raise CinematicValidationError(f"Audio cue #{cue_idx + 1} in shot '{shot_id}' must be an object.")
            ctype = cue_raw.get("cue_type")
            if not ctype or ctype not in VALID_CUE_TYPES:
                raise CinematicValidationError(
                    f"Invalid cue_type '{ctype}' in shot '{shot_id}'. Valid: {sorted(VALID_CUE_TYPES)}"
                )
            asset_id = cue_raw.get("asset_id")
            if not asset_id or not isinstance(asset_id, str):
                raise CinematicValidationError(f"Audio cue in shot '{shot_id}' requires 'asset_id'.")

            parsed_cues.append(
                AudioCue(
                    cue_type=ctype,
                    asset_id=asset_id,
                    start_time_ms=int(cue_raw.get("start_time_ms", 0)),
                    duration_ms=cue_raw.get("duration_ms"),
                    speaker_id=cue_raw.get("speaker_id"),
                    text=cue_raw.get("text"),
                    volume=float(cue_raw.get("volume", 1.0)),
                )
            )

        # Transition Validation
        parsed_trans: Transition | None = None
        trans_raw = shot_raw.get("transition")
        if trans_raw is not None:
            if not isinstance(trans_raw, dict):
                raise CinematicValidationError(f"Transition in shot '{shot_id}' must be an object.")
            ttype = trans_raw.get("type")
            if not ttype or ttype not in VALID_TRANSITION_TYPES:
                raise CinematicValidationError(
                    f"Invalid transition type '{ttype}' in shot '{shot_id}'. Valid: {sorted(VALID_TRANSITION_TYPES)}"
                )
            parsed_trans = Transition(
                type=ttype,
                duration_ms=int(trans_raw.get("duration_ms", 0)),
                target_scene=trans_raw.get("target_scene"),
                target_shot=trans_raw.get("target_shot"),
            )

        parsed_shots.append(
            Shot(
                id=shot_id,
                duration_ms=duration_ms,
                camera=camera,
                actions=parsed_actions,
                cues=parsed_cues,
                transition=parsed_trans,
                metadata=shot_raw.get("metadata"),
            )
        )
        calculated_duration_ms += duration_ms

    declared_duration = data.get("duration_ms", calculated_duration_ms)

    return CinematicScene(
        id=scene_id,
        title=scene_title.strip(),
        duration_ms=declared_duration,
        shots=parsed_shots,
        metadata=data.get("metadata"),
    )


class CinematicTimeline:
    """Deterministic millisecond-based cinematic timeline scheduler and event generator."""

    def __init__(self, scene: CinematicScene):
        self.scene = scene
        self.elapsed_scene_ms: int = 0
        self.current_shot_index: int = 0
        self.elapsed_shot_ms: int = 0
        self.is_complete: bool = False
        self.is_started: bool = False
        self.events: List[CinematicEvent] = []

        self._emitted_shot_starts: Set[int] = set()
        self._emitted_action_starts: Set[Tuple[int, int]] = set()
        self._emitted_cue_starts: Set[Tuple[int, int]] = set()

    @property
    def current_shot(self) -> Shot | None:
        if 0 <= self.current_shot_index < len(self.scene.shots):
            return self.scene.shots[self.current_shot_index]
        return None

    @property
    def remaining_shot_ms(self) -> int:
        shot = self.current_shot
        if not shot:
            return 0
        return max(0, shot.duration_ms - self.elapsed_shot_ms)

    def start(self) -> List[CinematicEvent]:
        """Initialize the timeline and emit initial scene and shot events."""
        if self.is_started:
            return []

        self.is_started = True
        event = CinematicEvent(
            event_type="scene_started",
            timestamp_ms=0,
            details={"scene_id": self.scene.id, "title": self.scene.title},
        )
        self.events.append(event)
        new_events = [event]

        if self.current_shot:
            shot_events = self._emit_shot_start(self.current_shot_index)
            new_events.extend(shot_events)

        return new_events

    def _emit_shot_start(self, shot_idx: int) -> List[CinematicEvent]:
        if shot_idx in self._emitted_shot_starts:
            return []

        self._emitted_shot_starts.add(shot_idx)
        shot = self.scene.shots[shot_idx]

        evt = CinematicEvent(
            event_type="shot_started",
            timestamp_ms=self.elapsed_scene_ms,
            details={
                "shot_id": shot.id,
                "scene_id": self.scene.id,
                "duration_ms": shot.duration_ms,
                "framing": shot.camera.framing,
                "movement": shot.camera.movement,
                "subject": shot.camera.subject,
            },
        )
        self.events.append(evt)
        events = [evt]

        # Check immediate actions/cues starting at offset 0
        sub_evts = self._check_sub_shot_events()
        events.extend(sub_evts)
        return events

    def _check_sub_shot_events(self) -> List[CinematicEvent]:
        shot = self.current_shot
        if not shot:
            return []

        new_evts: List[CinematicEvent] = []

        # Check Character Actions
        for act_idx, act in enumerate(shot.actions):
            key = (self.current_shot_index, act_idx)
            if key not in self._emitted_action_starts:
                if self.elapsed_shot_ms >= act.start_time_ms:
                    self._emitted_action_starts.add(key)
                    evt = CinematicEvent(
                        event_type="action_started",
                        timestamp_ms=self.elapsed_scene_ms,
                        details={
                            "shot_id": shot.id,
                            "character_id": act.character_id,
                            "action": act.action,
                            "target": act.target,
                        },
                    )
                    self.events.append(evt)
                    new_evts.append(evt)

        # Check Audio Cues
        for cue_idx, cue in enumerate(shot.cues):
            key = (self.current_shot_index, cue_idx)
            if key not in self._emitted_cue_starts:
                if self.elapsed_shot_ms >= cue.start_time_ms:
                    self._emitted_cue_starts.add(key)
                    evt_name = "dialogue_started" if cue.cue_type == "dialogue" else "audio_started"
                    evt = CinematicEvent(
                        event_type=evt_name,
                        timestamp_ms=self.elapsed_scene_ms,
                        details={
                            "shot_id": shot.id,
                            "cue_type": cue.cue_type,
                            "asset_id": cue.asset_id,
                            "speaker_id": cue.speaker_id,
                            "text": cue.text,
                        },
                    )
                    self.events.append(evt)
                    new_evts.append(evt)

        return new_evts

    def advance(self, delta_ms: int) -> List[CinematicEvent]:
        """Advance the timeline by delta_ms milliseconds and return newly triggered events."""
        if not self.is_started:
            start_events = self.start()
        else:
            start_events = []

        if self.is_complete or delta_ms <= 0:
            return start_events

        new_events: List[CinematicEvent] = list(start_events)
        self.elapsed_scene_ms += delta_ms
        self.elapsed_shot_ms += delta_ms

        while self.current_shot and self.elapsed_shot_ms >= self.current_shot.duration_ms:
            shot = self.current_shot
            overflow_ms = self.elapsed_shot_ms - shot.duration_ms

            # Emit shot_completed
            shot_comp = CinematicEvent(
                event_type="shot_completed",
                timestamp_ms=self.elapsed_scene_ms - overflow_ms,
                details={"shot_id": shot.id, "scene_id": self.scene.id},
            )
            self.events.append(shot_comp)
            new_events.append(shot_comp)

            # Emit transition if present
            if shot.transition:
                trans_evt = CinematicEvent(
                    event_type="transition_started",
                    timestamp_ms=self.elapsed_scene_ms - overflow_ms,
                    details={
                        "shot_id": shot.id,
                        "type": shot.transition.type,
                        "duration_ms": shot.transition.duration_ms,
                        "target_scene": shot.transition.target_scene,
                        "target_shot": shot.transition.target_shot,
                    },
                )
                self.events.append(trans_evt)
                new_events.append(trans_evt)

            self.current_shot_index += 1
            if self.current_shot_index >= len(self.scene.shots):
                self.is_complete = True
                self.elapsed_shot_ms = 0
                scene_comp = CinematicEvent(
                    event_type="scene_completed",
                    timestamp_ms=self.elapsed_scene_ms,
                    details={"scene_id": self.scene.id},
                )
                self.events.append(scene_comp)
                new_events.append(scene_comp)
                break
            else:
                self.elapsed_shot_ms = overflow_ms
                shot_events = self._emit_shot_start(self.current_shot_index)
                new_events.extend(shot_events)

        if not self.is_complete and self.current_shot:
            sub_events = self._check_sub_shot_events()
            new_events.extend(sub_events)

        return new_events

    def reset(self) -> None:
        """Reset timeline state back to 0ms."""
        self.elapsed_scene_ms = 0
        self.current_shot_index = 0
        self.elapsed_shot_ms = 0
        self.is_complete = False
        self.is_started = False
        self.events.clear()
        self._emitted_shot_starts.clear()
        self._emitted_action_starts.clear()
        self._emitted_cue_starts.clear()
