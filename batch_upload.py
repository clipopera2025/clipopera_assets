import json
import subprocess
import argparse


def run_entry(entry):
    cmd = [
        "python",
        "create_notion_page.py",
        "--project",
        entry["project"],
        "--status",
        entry["status"],
        "--link",
        entry["link"],
        "--budget",
        str(entry["budget"]),
    ]

    if "drive" in entry:
        cmd.extend(["--drive", entry["drive"]])
    if "webmaster" in entry:
        cmd.extend(["--webmaster", entry["webmaster"]])
    if "codex" in entry:
        cmd.extend(["--codex", entry["codex"]])
    if "sora" in entry:
        cmd.extend(["--sora", entry["sora"]])
    if "gpts" in entry:
        cmd.extend(["--gpts", entry["gpts"]])
    if "library" in entry:
        cmd.extend(["--library", entry["library"]])
    if "registry" in entry:
        cmd.extend(["--registry", entry["registry"]])

    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Batch upload projects to Notion")
    parser.add_argument("file", help="Path to JSONL file with one project per line")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            run_entry(entry)


if __name__ == "__main__":
    main()
