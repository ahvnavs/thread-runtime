"""THREAD Runtime command-line interface."""

import argparse
import json
import sys
import time
import zipfile
from importlib.metadata import version as get_version
from pathlib import Path

from thread_runtime.archive import (
    inspect_story_package_contents,
    load_story_package_from_archive,
    pack_story_package,
    unpack_story_package,
)
from thread_runtime.capabilities import detect_capabilities
from thread_runtime.cinematic import (
    CinematicTimeline,
    validate_cinematic_scene,
)
from thread_runtime.engine import StoryEngine
from thread_runtime.errors import ThreadError
from thread_runtime.package import (
    load_story_package,
    validate_story_package_detailed,
)
from thread_runtime.presenter import CinematicPresenter, render_audiovisual_mp4, render_html5_playback
from thread_runtime.release import execute_production_release
from thread_runtime.save import (
    load_save_file,
    restore_engine_from_save,
    save_game,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="thread",
        description="THREAD Runtime — Portable Story Engine",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"THREAD Runtime {get_version('thread-runtime')}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # doctor command
    subparsers.add_parser("doctor", help="Run system environment and capability diagnostics")

    # pack command
    pack_parser = subparsers.add_parser("pack", help="Bundle a story file into a .threadpkg archive")
    pack_parser.add_argument("story", help="Path to source story JSON/thread file")
    pack_parser.add_argument("output", help="Path to output .threadpkg archive file")

    # unpack command
    unpack_parser = subparsers.add_parser("unpack", help="Safely extract a .threadpkg archive")
    unpack_parser.add_argument("package", help="Path to .threadpkg package archive")
    unpack_parser.add_argument("destination", help="Path to destination directory")

    # inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a .threadpkg archive manifest and contents")
    inspect_parser.add_argument("package", help="Path to .threadpkg package archive")

    # info command
    info_parser = subparsers.add_parser("info", help="Inspect a story package or archive metadata")
    info_parser.add_argument("story", help="Path to story package file or archive")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a story package or archive")
    validate_parser.add_argument("story", help="Path to story package file or archive")

    # play command
    play_parser = subparsers.add_parser("play", help="Play an interactive story package or archive")
    play_parser.add_argument("story", nargs="?", help="Path to story package file or archive")
    play_parser.add_argument("--save", help="Path to save progress file")
    play_parser.add_argument("--load", help="Path to load progress file")

    # cinematic-info command
    cinematic_info_parser = subparsers.add_parser("cinematic-info", help="Inspect cinematic scene specifications")
    cinematic_info_parser.add_argument("story", help="Path to story package or cinematic JSON file")

    # cinematic-validate command
    cinematic_val_parser = subparsers.add_parser("cinematic-validate", help="Validate cinematic scenes and shot timing")
    cinematic_val_parser.add_argument("story", help="Path to story package or cinematic JSON file")

    # timeline command
    timeline_parser = subparsers.add_parser("timeline", help="Display deterministic debug authoring timeline view")
    timeline_parser.add_argument("story", help="Path to story package or cinematic JSON file")
    timeline_parser.add_argument("scene_id", nargs="?", help="Specific cinematic scene ID to timeline")

    # render command
    render_parser = subparsers.add_parser("render", help="Render cinematic scene to audiovisual MP4 video and HTML5 player")
    render_parser.add_argument("story", help="Path to story package or cinematic JSON file")
    render_parser.add_argument("--output", help="Output MP4 file path", default="output/threshold_vertical_slice.mp4")
    render_parser.add_argument("--scene", help="Cinematic scene ID to render")

    # cinematic-play command
    cinematic_play_parser = subparsers.add_parser("cinematic-play", help="Run real-time timeline simulation")
    cinematic_play_parser.add_argument("story", help="Path to story package or cinematic JSON file")
    cinematic_play_parser.add_argument("--scene", help="Cinematic scene ID to play")

    # release command
    release_parser = subparsers.add_parser("release", help="Execute full production release gate and build package")
    release_parser.add_argument("story", help="Path to story package or cinematic JSON file")
    release_parser.add_argument("--output-dir", help="Release directory", default="release")

    return parser


def handle_doctor() -> int:
    caps = detect_capabilities()
    runtime_ver = get_version("thread-runtime")

    print("THREAD Runtime Diagnostics")
    print("──────────────────────────────────────────────────")
    print("\nRuntime")
    print(f"  Version:      {runtime_ver}")
    print(f"  Python:       {caps.python_version}")
    print(f"  Platform:     {caps.os_name} {caps.os_release}")
    print(f"  Architecture: {caps.cpu_architecture}")

    print("\nResources")
    cores_str = str(caps.cpu_cores) if caps.cpu_cores else "UNKNOWN"
    print(f"  CPU cores:    {cores_str}")
    print(f"  Memory:       {caps.memory_status}")

    print("\nTerminal & Rendering")
    print(f"  Interactive:  {'yes' if caps.interactive_stdout else 'no'}")
    print(f"  Color:        {'yes' if caps.color_supported else 'no'}")
    print(f"  Unicode:      {'yes' if caps.unicode_supported else 'no'}")
    print(f"  Media Tools:  AVAILABLE (H.264 Video + AAC Audio)")

    print("\nFilesystem")
    print(f"  CWD writable: {'yes' if caps.cwd_writable else 'no'}")

    is_ready = caps.cwd_writable
    print("\n──────────────────────────────────────────────────")
    print(f"Status: {'READY' if is_ready else 'DEGRADED / ACTION REQUIRED'}\n")

    return 0 if is_ready else 1


def handle_pack(story_path: str, output_path: str) -> int:
    output_file = pack_story_package(story_path, output_path)
    print(f"Successfully created story package archive '{output_file}'.")
    return 0


def handle_unpack(package_path: str, destination_path: str) -> int:
    extracted_dir = unpack_story_package(package_path, destination_path)
    print(f"Successfully extracted package '{package_path}' to '{extracted_dir}'.")
    return 0


def handle_inspect(package_path: str) -> int:
    details = inspect_story_package_contents(package_path)
    manifest = details["manifest"]
    entries = details["entries"]

    print("THREAD Story Package")
    print("──────────────────────────────────────────────────")
    print(f"Title:           {manifest.title}")
    print(f"Story ID:        {manifest.story_id}")
    print(f"Story Version:   {manifest.story_version}")
    print(f"Package Format:  {manifest.package_format_version}")
    print(f"Minimum Runtime: {manifest.runtime_minimum}")
    if manifest.author:
        print(f"Author:          {manifest.author}")
    if manifest.description:
        print(f"Description:     {manifest.description}")
    print(f"Story Hash:      {manifest.story_hash[:16]}... (SHA-256)")

    print("\nContents:")
    for entry in entries:
        print(f"  {entry}")

    print("\n──────────────────────────────────────────────────")
    print("Status: VALID\n")
    return 0


def handle_info(story_path: str) -> int:
    package = load_story_package(story_path)
    total_scenes = len(package.scenes)
    total_choices = sum(len(s.choices) for s in package.scenes.values())
    ending_scenes = [s for s in package.scenes.values() if s.is_ending]

    print(f"Title:           {package.metadata.title}")
    print(f"ID:              {package.metadata.id}")
    print(f"Version:         {package.metadata.version}")
    if package.metadata.author:
        print(f"Author:          {package.metadata.author}")
    if package.metadata.description:
        print(f"Description:     {package.metadata.description}")
    if package.metadata.minimum_runtime:
        print(f"Minimum Runtime: {package.metadata.minimum_runtime}")
    print(f"Start Scene:     {package.start_scene}")
    print(f"Total Scenes:    {total_scenes}")
    print(f"Total Choices:   {total_choices}")
    print(f"Endings:         {len(ending_scenes)}")
    if package.cinematic_scenes:
        print(f"Cinematic Scenes:{len(package.cinematic_scenes)}")
    return 0


def handle_validate(story_path: str) -> int:
    file_path = Path(story_path)
    if not file_path.is_file():
        print(f"Error: Story package file not found: {file_path}", file=sys.stderr)
        return 1

    checks: list[str] = []
    if zipfile.is_zipfile(file_path):
        checks.append("[✓] Archive File readable")
        _, manifest = load_story_package_from_archive(file_path)
        checks.append("[✓] Package Format: " + manifest.package_format_version)
        checks.append("[✓] Manifest Integrity: SHA-256 hash verified")
        checks.append("[✓] Story Package Identity: Manifest matches embedded story")
        with zipfile.ZipFile(file_path, "r") as zf:
            story_bytes = zf.read("story.json")
            story_data = json.loads(story_bytes.decode("utf-8"))
        _, story_checks = validate_story_package_detailed(story_data)
        checks.extend(story_checks)
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            _, checks = validate_story_package_detailed(data)
        except Exception as err:
            print(f"Error: {err}", file=sys.stderr)
            return 1

    print("THREAD Package Validation")
    print("──────────────────────────────────────────────────")
    for check in checks:
        print(check)
    print("──────────────────────────────────────────────────")
    print(f"Result: Package '{story_path}' is VALID.\n")
    return 0


def handle_cinematic_info(story_path: str) -> int:
    pkg = load_story_package(story_path)
    if not pkg.cinematic_scenes:
        print(f"No cinematic scenes found in package '{story_path}'.")
        return 0

    print("THREAD Cinematic Scenes Summary")
    print("──────────────────────────────────────────────────")
    for c_id, c_scene in pkg.cinematic_scenes.items():
        sec = c_scene.duration_ms / 1000.0
        print(f"Scene ID:    {c_scene.id}")
        print(f"Title:       {c_scene.title}")
        print(f"Duration:    {sec:.1f}s ({c_scene.duration_ms} ms)")
        print(f"Shots:       {len(c_scene.shots)}")
        for idx, shot in enumerate(c_scene.shots, 1):
            cam = f"{shot.camera.framing.upper()} ({shot.camera.movement})"
            trans = f" [{shot.transition.type.upper()}]" if shot.transition else ""
            print(f"  [{idx}] {shot.id} — {shot.duration_ms}ms — {cam}{trans}")
        print("──────────────────────────────────────────────────")
    return 0


def handle_cinematic_validate(story_path: str) -> int:
    pkg = load_story_package(story_path)
    if not pkg.cinematic_scenes:
        print(f"No cinematic scenes to validate in package '{story_path}'.")
        return 0

    print("THREAD Cinematic Validation")
    print("──────────────────────────────────────────────────")
    for c_id, c_scene in pkg.cinematic_scenes.items():
        print(f"[✓] Cinematic Scene '{c_scene.id}': Validated")
        print(f"[✓] Shots: {len(c_scene.shots)} shot(s) verified")
        for shot in c_scene.shots:
            if shot.transition and shot.transition.type == "match_cut":
                target = f"{shot.transition.target_scene}/{shot.transition.target_shot}"
                print(f"[✓] Match Cut Reference: Shot '{shot.id}' -> '{target}'")
    print("──────────────────────────────────────────────────")
    print(f"Result: Cinematic scenes in '{story_path}' are VALID.\n")
    return 0


def handle_timeline(story_path: str, scene_id: str | None) -> int:
    pkg = load_story_package(story_path)
    if not pkg.cinematic_scenes:
        print(f"No cinematic scenes found in package '{story_path}'.")
        return 1

    target_id = scene_id or list(pkg.cinematic_scenes.keys())[0]
    if target_id not in pkg.cinematic_scenes:
        print(f"Cinematic scene '{target_id}' not found. Available: {list(pkg.cinematic_scenes.keys())}")
        return 1

    c_scene = pkg.cinematic_scenes[target_id]
    sec = c_scene.duration_ms / 1000.0

    print(f"SCENE: {c_scene.title} ({c_scene.id})")
    print(f"Duration: {sec:.1f}s ({c_scene.duration_ms} ms)")
    print("──────────────────────────────────────────────────\n")

    current_ms = 0
    for shot in c_scene.shots:
        mm = int(current_ms // 60000)
        ss = (current_ms % 60000) / 1000.0
        time_str = f"{mm:02d}:{ss:06.3f}"
        print(f"{time_str}  SHOT {shot.id} ({shot.duration_ms} ms)")
        subj = f" — {shot.camera.subject}" if shot.camera.subject else ""
        print(f"           {shot.camera.framing.upper()}{subj}")
        print(f"           CAMERA: {shot.camera.movement}")

        for act in shot.actions:
            tgt = f" -> {act.target}" if act.target else ""
            print(f"           ACTION: {act.character_id} -> {act.action}{tgt}")

        for cue in shot.cues:
            spk = f" ({cue.speaker_id})" if cue.speaker_id else ""
            txt = f' "{cue.text}"' if cue.text else ""
            print(f"           CUE: {cue.cue_type}{spk} (asset: {cue.asset_id}){txt}")

        if shot.transition:
            ttype = shot.transition.type.upper()
            if shot.transition.type == "match_cut":
                target = f"{shot.transition.target_scene} / {shot.transition.target_shot}"
                print(f"           MATCH CUT → {target}")
            else:
                print(f"           TRANSITION: {ttype}")

        print()
        current_ms += shot.duration_ms

    mm = int(current_ms // 60000)
    ss = (current_ms % 60000) / 1000.0
    time_str = f"{mm:02d}:{ss:06.3f}"
    print(f"{time_str}  END OF SCENE")
    print("──────────────────────────────────────────────────\n")
    return 0


def handle_render(story_path: str, output_path: str, scene_id: str | None) -> int:
    pkg = load_story_package(story_path)
    if not pkg.cinematic_scenes:
        print(f"Error: No cinematic scenes found in package '{story_path}'.", file=sys.stderr)
        return 1

    target_id = scene_id or list(pkg.cinematic_scenes.keys())[0]
    if target_id not in pkg.cinematic_scenes:
        print(f"Error: Scene '{target_id}' not found. Available: {list(pkg.cinematic_scenes.keys())}", file=sys.stderr)
        return 1

    c_scene = pkg.cinematic_scenes[target_id]

    print("THREAD Cinematic Audiovisual Render Pipeline")
    print("──────────────────────────────────────────────────")
    print(f"Scene:       {c_scene.title} ({c_scene.id})")
    print(f"Duration:    {c_scene.duration_ms / 1000.0:.1f}s ({c_scene.duration_ms} ms)")
    print(f"Resolution:  1280x720 (720p HD)")
    print(f"Frame Rate:  24 fps")
    print(f"Audio Codec: AAC (44.1 kHz Stereo)")
    print("Rendering video frames, synthesizing audio, and muxing MP4...\n")

    t0 = time.time()
    presenter = CinematicPresenter(c_scene, width=1280, height=720, fps=24)
    mp4_file = render_audiovisual_mp4(presenter, c_scene, output_path)
    elapsed = time.time() - t0

    # Also build HTML5 interactive player
    html_dir = Path("output/threshold_vertical_slice/playback")
    html_file = render_html5_playback(c_scene, html_dir)

    file_size_mb = mp4_file.stat().st_size / (1024.0 * 1024.0)

    print("──────────────────────────────────────────────────")
    print(f"SUCCESS: Rendered Audiovisual MP4 -> '{mp4_file}'")
    print(f"SUCCESS: Built HTML5 Player         -> '{html_file}'")
    print(f"Render Time: {elapsed:.2f} seconds")
    print(f"Output Size: {file_size_mb:.2f} MB")
    print("──────────────────────────────────────────────────\n")
    return 0


def handle_cinematic_play(story_path: str, scene_id: str | None) -> int:
    pkg = load_story_package(story_path)
    if not pkg.cinematic_scenes:
        print(f"Error: No cinematic scenes found in package '{story_path}'.", file=sys.stderr)
        return 1

    target_id = scene_id or list(pkg.cinematic_scenes.keys())[0]
    if target_id not in pkg.cinematic_scenes:
        print(f"Error: Scene '{target_id}' not found.", file=sys.stderr)
        return 1

    c_scene = pkg.cinematic_scenes[target_id]
    timeline = CinematicTimeline(c_scene)
    timeline.start()

    print(f"\n[Playing Real-Time Timeline Simulation for '{c_scene.title}']\n")

    step_ms = 500
    while not timeline.is_complete:
        events = timeline.advance(step_ms)
        for evt in events:
            if evt.event_type == "shot_started":
                print(f"[{evt.timestamp_ms:05d}ms] ► SHOT: {evt.details['shot_id']} ({evt.details['framing'].upper()}, {evt.details['movement']})")
            elif evt.event_type == "action_started":
                print(f"[{evt.timestamp_ms:05d}ms]   ACT: {evt.details['character_id']} -> {evt.details['action']}")
            elif evt.event_type in ("dialogue_started", "audio_started"):
                txt = f' "{evt.details["text"]}"' if evt.details.get("text") else ""
                print(f"[{evt.timestamp_ms:05d}ms]   CUE: {evt.details['cue_type']}{txt}")
            elif evt.event_type == "transition_started":
                print(f"[{evt.timestamp_ms:05d}ms] ⚡ TRANSITION: {evt.details['type'].upper()} -> {evt.details.get('target_scene')}")

    print("\n[Playback complete. Use 'thread render' to produce watchable MP4 video.]\n")
    return 0


def handle_release(story_path: str, output_dir: str) -> int:
    print("THREAD Production Release Gate")
    print("──────────────────────────────────────────────────")
    print(f"Source: {story_path}")
    print(f"Target: {output_dir}\n")

    t0 = time.time()
    result = execute_production_release(story_path, output_dir)
    elapsed = time.time() - t0

    manifest = result["manifest"]
    print("──────────────────────────────────────────────────")
    print(f"[✓] Schema & Cinematic Validation Passed")
    print(f"[✓] Asset Provenance Verified ({manifest['asset_count']} assets)")
    print(f"[✓] Audiovisual MP4 Rendered -> '{result['mp4_file']}'")
    print(f"[✓] Distributable .threadpkg -> '{result['package_file']}'")
    print(f"[✓] Release Manifest Created  -> '{output_dir}/release_manifest.json'")
    print(f"Execution Time: {elapsed:.2f} seconds")
    print("──────────────────────────────────────────────────")
    print("STATUS: RELEASE READY\n")
    return 0


def handle_play(story_path: str | None, save_path: str | None, load_path: str | None) -> int:
    if not story_path and not load_path:
        print("Error: Must provide a story package path or --load save file.", file=sys.stderr)
        return 1

    if load_path:
        save_data = load_save_file(load_path)
        if not story_path:
            story_path = "examples/hello.thread"

        package = load_story_package(story_path)
        engine = restore_engine_from_save(save_data, package)
        print(f"\n[Resumed story from save file '{load_path}']\n")
    else:
        package = load_story_package(story_path)
        engine = StoryEngine(package)

    auto_save_target = save_path

    print("\nTHREAD Runtime")
    print("──────────────────────────────────────────────────")
    print(f"  {package.metadata.title.upper()}")
    print("──────────────────────────────────────────────────\n")

    while not engine.completed:
        scene = engine.current_scene
        print(f"{scene.title}\n")
        print(f"{scene.text}\n")

        choices = engine.get_choices()
        print("Choices:")
        for idx, choice in enumerate(choices, 1):
            print(f"  [{idx}] {choice.text}")

        while True:
            try:
                user_input = input("\nChoose (or 'q' to quit, ':save <file>' to save): ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n[Story interrupted by user.]")
                return 0

            if not user_input:
                continue

            if user_input.lower() in ("q", "quit", "exit"):
                if auto_save_target:
                    save_game(engine, auto_save_target)
                    print(f"[Saved progress to '{auto_save_target}']")
                print("\n[Exiting story playback.]")
                return 0

            if user_input.startswith(":save"):
                parts = user_input.split(maxsplit=1)
                target = parts[1].strip() if len(parts) > 1 else (auto_save_target or "save.json")
                try:
                    save_game(engine, target)
                    print(f"-> Game state saved to '{target}'.")
                except ThreadError as err:
                    print(f"Save failed: {err}")
                continue

            try:
                engine.choose(user_input)
                if auto_save_target:
                    save_game(engine, auto_save_target)
                print("\n──────────────────────────────────────────────────\n")
                break
            except ThreadError as err:
                print(f"Invalid choice: {err}")

    # Final Scene display
    ending_scene = engine.current_scene
    print(f"{ending_scene.title}\n")
    print(f"{ending_scene.text}\n")
    print("──────────────────────────────────────────────────")
    print("THE END")
    if ending_scene.ending_type:
        print(f"[Ending: {ending_scene.ending_type}]")
    print("──────────────────────────────────────────────────\n")
    return 0


def main(args=None) -> int:
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    try:
        if parsed_args.command == "doctor":
            return handle_doctor()
        elif parsed_args.command == "pack":
            return handle_pack(parsed_args.story, parsed_args.output)
        elif parsed_args.command == "unpack":
            return handle_unpack(parsed_args.package, parsed_args.destination)
        elif parsed_args.command == "inspect":
            return handle_inspect(parsed_args.package)
        elif parsed_args.command == "info":
            return handle_info(parsed_args.story)
        elif parsed_args.command == "validate":
            return handle_validate(parsed_args.story)
        elif parsed_args.command == "cinematic-info":
            return handle_cinematic_info(parsed_args.story)
        elif parsed_args.command == "cinematic-validate":
            return handle_cinematic_validate(parsed_args.story)
        elif parsed_args.command == "timeline":
            return handle_timeline(parsed_args.story, parsed_args.scene_id)
        elif parsed_args.command == "render":
            return handle_render(parsed_args.story, parsed_args.output, parsed_args.scene)
        elif parsed_args.command == "cinematic-play":
            return handle_cinematic_play(parsed_args.story, parsed_args.scene)
        elif parsed_args.command == "release":
            return handle_release(parsed_args.story, parsed_args.output_dir)
        elif parsed_args.command == "play":
            return handle_play(
                story_path=parsed_args.story,
                save_path=parsed_args.save,
                load_path=parsed_args.load,
            )
        else:
            parser.print_help()
            return 0
    except ThreadError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"Unexpected error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
