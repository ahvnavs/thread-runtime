"""Asset Provenance and Chain of Title Registry Validator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from thread_runtime.errors import StoryValidationError

VALID_PROVENANCE_STATUSES = {
    "ORIGINAL",
    "ORIGINAL_ART",
    "ORIGINAL_CODE",
    "PROCEDURAL_GENERATED",
    "AI_GENERATED",
    "PUBLIC_DOMAIN",
    "OPEN_LICENSE",
    "THIRD_PARTY_LICENSE",
    "GENERATED",
    "UNKNOWN",
    "REJECTED",
}


@dataclass(frozen=True)
class AssetProvenance:
    """Chain of title record for an individual media or narrative asset."""

    asset_id: str
    type: str
    origin: str
    creator: str
    license: str
    status: str
    source_ref: Optional[str] = None
    checksum: Optional[str] = None


def validate_asset_provenance(asset_data: List[Dict[str, Any]]) -> Dict[str, AssetProvenance]:
    """Validate asset provenance records and reject UNKNOWN or REJECTED statuses."""
    if not isinstance(asset_data, list):
        raise StoryValidationError("Asset provenance registry must be a list.")

    registry: Dict[str, AssetProvenance] = {}

    for idx, entry in enumerate(asset_data):
        if not isinstance(entry, dict):
            raise StoryValidationError(f"Asset record #{idx + 1} must be a JSON object.")

        aid = entry.get("id") or entry.get("asset_id")
        if not aid or not isinstance(aid, str):
            raise StoryValidationError(f"Asset record #{idx + 1} requires a non-empty 'id' string.")

        atype = entry.get("type", "unknown")
        origin = entry.get("source") or entry.get("origin") or "Project Local"
        creator = entry.get("creator") or entry.get("source") or "THREAD Pipeline"
        lic = entry.get("license", "Unspecified")

        status = entry.get("status", "ORIGINAL").upper()
        if status not in VALID_PROVENANCE_STATUSES:
            raise StoryValidationError(
                f"Invalid provenance status '{status}' for asset '{aid}'. Valid: {sorted(VALID_PROVENANCE_STATUSES)}"
            )

        if status in ("UNKNOWN", "REJECTED"):
            raise StoryValidationError(
                f"Release rejected due to asset '{aid}' having unacceptable provenance status '{status}'."
            )

        registry[aid] = AssetProvenance(
            asset_id=aid,
            type=atype,
            origin=origin,
            creator=creator,
            license=lic,
            status=status,
            source_ref=entry.get("source_ref"),
            checksum=entry.get("checksum"),
        )

    return registry
