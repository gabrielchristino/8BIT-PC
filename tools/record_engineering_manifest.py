"""Record/check the provenance and byte hashes of active engineering outputs."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "verification/rev9842/manifest.json"


def main():
    if "--check" in sys.argv:
        report = json.loads(MANIFEST.read_text())
        failures = []
        for item in report["files"]:
            target = (ROOT/item["path"]).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():
                failures.append(item["path"])
                continue
            data = target.read_bytes()
            if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
                failures.append(item["path"])
        print(json.dumps({"checked": len(report["files"]), "failures": failures}))
        return int(bool(failures))
    files = set()
    for directory in ("sim", "hardware", "tools", "references", "docs/engineering",
                      "verification/rev9842"):
        files.update(p for p in (ROOT/directory).rglob("*")
                     if p.is_file() and p != MANIFEST and "__pycache__" not in p.parts)
    files.add(ROOT/"verification/environment.json")
    rows = []
    for filename in sorted(files):
        relative = filename.relative_to(ROOT).as_posix()
        data = filename.read_bytes()
        row = {"path": relative, "bytes": len(data),
               "sha256": hashlib.sha256(data).hexdigest(),
               "origin": "New ISA-1 engineering iteration 9.8.4.2, 2026-11-24"}
        if relative.startswith("references/ti/"):
            if not data.startswith(b"%PDF-"):
                raise ValueError("Invalid PDF: " + relative)
            row["origin"] = "Texas Instruments official datasheet"
            row["url"] = "https://www.ti.com/lit/ds/symlink/" + filename.name
        elif filename.name == "KICAD_SYMBOLS_COPYRIGHT.txt":
            row["origin"] = "Unmodified /usr/share/doc/kicad-symbols/copyright from Ubuntu package 7.0.11-1"
        rows.append(row)
    MANIFEST.write_text(json.dumps({"revision": "9.8.4.2", "date": "2026-11-24",
        "scope": "Active candidate and generated outputs, not historical archives", "files": rows}, indent=2)+"\n")
    print(json.dumps({"recorded": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
