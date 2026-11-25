"""Verify byte integrity of recovered sources and original ZIP extractions."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {"ISA-1_rev93.zip": "rev93", "ISA-1_rev983.zip": "rev983", "ISA-1_rev984.zip": "rev984"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((ROOT / "archive/manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest["files"]:
        target = (ROOT / entry["path"]).resolve()
        if not target.is_relative_to(ROOT):
            failures.append(f"Path outside repository: {entry['path']}")
            continue
        if not target.is_file():
            failures.append(f"Missing: {entry['path']}")
            continue
        data = target.read_bytes()
        if len(data) != entry["bytes"] or digest(data) != entry["sha256"]:
            failures.append(f"Hash/size mismatch: {entry['path']}")
    checked = 0
    for package, revision in PACKAGES.items():
        with zipfile.ZipFile(ROOT / "archive/packages" / package) as bundle:
            expected = set()
            for item in bundle.infolist():
                if item.is_dir():
                    continue
                expected.add(item.filename)
                target = (ROOT / "revisions" / revision / item.filename).resolve()
                if not target.is_relative_to(ROOT / "revisions" / revision):
                    failures.append(f"Unsafe ZIP path: {item.filename}")
                    continue
                if not target.exists() or target.read_bytes() != bundle.read(item):
                    failures.append(f"ZIP differs from extraction: {revision}/{item.filename}")
                checked += 1
            actual = {p.relative_to(ROOT / "revisions" / revision).as_posix()
                      for p in (ROOT / "revisions" / revision).rglob("*") if p.is_file()}
            if actual != expected:
                failures.append(f"Unexpected/missing extracted files in {revision}: {sorted(actual ^ expected)}")
    report = {"date": "2026-11-24", "manifest_files_checked": len(manifest["files"]),
              "zip_entries_checked": checked, "failures": failures}
    (ROOT / "verification/integrity.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
