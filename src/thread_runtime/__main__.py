"""THREAD Package CLI Main Entrypoint."""

import sys
from pathlib import Path
from thread_runtime.runtime import ThreadRuntimeEngine


def main():
    story_arg = sys.argv[1] if len(sys.argv) > 1 else "story/story_I/part_1/story.json"
    if story_arg == "story_I/part_1":
        story_arg = "story/story_I/part_1/story.json"

    story_path = Path(story_arg)
    engine = ThreadRuntimeEngine(story_path)
    engine.play()


if __name__ == "__main__":
    main()
