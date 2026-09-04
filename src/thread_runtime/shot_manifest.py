"""THREAD Shot Manifest Loader & Layer Compositing Model."""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from thread_runtime.errors import MissingAssetError, ShotManifestError


class ShotLayer:
    """Represents a single authored PNG layer within a shot."""

    def __init__(self, layer_id: str, file_name: str, z_index: int, parallax: float, file_path: Path):
        self.layer_id = layer_id
        self.file_name = file_name
        self.z_index = z_index
        self.parallax = parallax
        self.file_path = file_path

        if not self.file_path.exists():
            raise MissingAssetError(
                f"Missing required authored raster asset '{self.file_name}' for layer '{self.layer_id}' at path '{self.file_path}'"
            )


class ShotManifest:
    """Parses, validates, and manages deterministic camera interpolation for a shot manifest."""

    def __init__(self, manifest_path: Path):
        self.manifest_path = Path(manifest_path)
        self.shot_dir = self.manifest_path.parent

        if not self.manifest_path.exists():
            raise MissingAssetError(f"Missing required shot manifest at path '{self.manifest_path}'")

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as err:
            raise ShotManifestError(f"Failed to parse manifest JSON at '{self.manifest_path}': {err}") from err

        self.shot_id = data.get("shot_id", "unknown_shot")
        self.canvas = tuple(data.get("canvas", [426, 240]))
        self.duration_s = float(data.get("duration_s", 10.0))
        self.effects = data.get("effects", [])

        # Parse & Validate Layers (Sorted Deterministically by z_index)
        layers_data = data.get("layers", [])
        if not layers_data:
            raise ShotManifestError(f"Shot manifest '{self.manifest_path}' contains zero layers")

        self.layers: List[ShotLayer] = []
        for l_data in layers_data:
            l_id = l_data.get("id", "layer")
            f_name = l_data.get("file", "")
            z_idx = int(l_data.get("z", 0))
            par = float(l_data.get("parallax", 0.0))
            f_path = self.shot_dir / f_name

            layer = ShotLayer(layer_id=l_id, file_name=f_name, z_index=z_idx, parallax=par, file_path=f_path)
            self.layers.append(layer)

        self.layers.sort(key=lambda l: l.z_index)

        # Camera Specification
        camera_data = data.get("camera", {})
        self.start_pan = tuple(camera_data.get("start", [0.0, 0.0]))
        self.end_pan = tuple(camera_data.get("end", [0.0, 0.0]))
        self.camera_duration_s = float(camera_data.get("duration_s", self.duration_s))

    def interpolate_camera(self, progress: float) -> Tuple[float, float]:
        """Compute deterministic subpixel camera pan offset (x, y) for given progress [0.0, 1.0]."""
        p = max(0.0, min(1.0, progress))
        cam_x = self.start_pan[0] + (self.end_pan[0] - self.start_pan[0]) * p
        cam_y = self.start_pan[1] + (self.end_pan[1] - self.start_pan[1]) * p
        return (cam_x, cam_y)
