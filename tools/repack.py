#!/usr/bin/env python3
"""Repack the WebMUGEN game.pak + manifest.json for Ashar's anime crossover build.

The shipped site packs the whole IKEMEN GO virtual filesystem into a single
concatenated file (ikemen-fs/game.pak) with an offset table
(ikemen-fs/manifest.json: {pack, files: {vpath: [offset, length]}, stamp}).
The boot page downloads the pak once up front, so trimming the pak is what
shrinks the first-time download.

Usage:
  python3 repack.py extract --site <site-dir> --tree <work-tree>
  python3 repack.py build   --site <site-dir> --tree <work-tree> --spec <spec.json>

The spec (JSON) drives the build:
  {
    "remove": ["data/mugen1/", "data/big/", ...],   # path prefixes to drop
    "chars":  {"goku": "chars-dl/goku-z2", ...},    # vpath dir -> source dir
    "stages": {"tournament": "stages-dl/tournament", ...},
    "select_def": "[Characters]\n...\n\n[ExtraStages]\n...\n\n[Options]\n...",
    "stamp": "abcdef123456"   # optional; random 12-hex if omitted
  }

Validation (fatal on failure):
  - every character entry in select.def resolves to a .def that exists in tree
  - every char folder has .def + .sff + .air + at least one .cns/.st, and every
    file named in the char .def [Files] section exists
  - every stage entry resolves to a .def whose .sff exists
"""
import hashlib
import json
import os
import re
import shutil
import sys

SITE_FILES = ("game.pak", "manifest.json")


def load_manifest(site):
    with open(os.path.join(site, "ikemen-fs", "manifest.json"), encoding="utf-8") as f:
        return json.load(f)


def read_pak(site, manifest):
    if manifest.get("parts"):
        blob = bytearray()
        for part in manifest["parts"]:
            with open(os.path.join(site, "ikemen-fs", part["file"]), "rb") as f:
                blob += f.read()
        return bytes(blob)
    with open(os.path.join(site, "ikemen-fs", manifest["pack"]), "rb") as f:
        return f.read()


def extract(site, tree):
    manifest = load_manifest(site)
    pak = read_pak(site, manifest)
    if os.path.exists(tree):
        shutil.rmtree(tree)
    for vpath, (off, ln) in manifest["files"].items():
        dest = os.path.join(tree, *vpath.split("/"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(pak[off:off + ln])
    print(f"extracted {len(manifest['files'])} files -> {tree}")
    return manifest


def parse_def_files_section(text):
    """Return {key: value} of the [Files] section of a .def file (lowercased keys)."""
    m = re.search(r"\[Files\](.*?)(?:\n\[|\Z)", text, re.S | re.I)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        line = line.split(";", 1)[0].strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip().lower()] = v.strip().strip('"')
    return out


def validate_char(tree, char_dir):
    """char_dir like 'chars/goku'. Returns list of error strings (empty = ok)."""
    errs = []
    base = os.path.join(tree, *char_dir.split("/"))
    if not os.path.isdir(base):
        return [f"{char_dir}: folder missing"]
    defs = [f for f in os.listdir(base) if f.lower().endswith(".def")]
    if not defs:
        return [f"{char_dir}: no .def file"]
    # The main def is the one named in select.def; here validate every .def.
    have = {f.lower() for f in os.listdir(base)}
    # recursive file set (palettes etc. live in subdirs)
    allfiles = set()
    for root, _dirs, files in os.walk(base):
        for fn in files:
            allfiles.add(os.path.relpath(os.path.join(root, fn), base).lower().replace(os.sep, "/"))
    for d in defs:
        with open(os.path.join(base, d), encoding="utf-8", errors="replace") as f:
            text = f.read()
        files = parse_def_files_section(text)
        for key in ("sprite", "anim", "sound", "cmd"):
            v = files.get(key)
            if v and v.lower() not in allfiles and v.lower() not in have:
                errs.append(f"{char_dir}/{d}: [Files] {key}={v} missing")
        # .cns / .st files named in the def (st, stcommon, etc.). stcommon
        # resolves from data/ (the engine's common states), where the shipped
        # file is the .zss build of the .cns name the .def cites.
        for key, v in files.items():
            if key.startswith("st") and v.lower().endswith((".cns", ".st")):
                cand = os.path.join(tree, "data", *v.split("/"))
                if v.lower() not in allfiles and not (
                        os.path.isfile(cand) or os.path.isfile(cand + ".zss")):
                    errs.append(f"{char_dir}/{d}: [Files] {key}={v} missing")
    exts = {os.path.splitext(f)[1].lower() for f in allfiles}
    for need in (".sff", ".air"):
        if need not in exts:
            errs.append(f"{char_dir}: no {need} file")
    if not (".cns" in exts or ".st" in exts):
        errs.append(f"{char_dir}: no .cns/.st file")
    if ".cmd" not in exts and ".comand" not in exts:
        # .comand is the same command file under a typo'd extension
        # (Witherower's WR chars ship cmd.comand); the engine reads the
        # path from [Files] and does not care about the extension.
        errs.append(f"{char_dir}: no .cmd file")
    return errs


def validate_stage(tree, stage_def_path):
    """stage_def_path like 'stages/tournament.def'. Returns error list."""
    errs = []
    full = os.path.join(tree, *stage_def_path.split("/"))
    if not os.path.isfile(full):
        return [f"{stage_def_path}: missing"]
    with open(full, encoding="utf-8", errors="replace") as f:
        text = f.read()
    # spr = <file>.sff lives in [BGdef], not [StageInfo].
    spr = None
    m = re.search(r"(?m)^\s*spr\s*=\s*([^\s;]+)", text)
    if m:
        spr = m.group(1).strip().strip('"')
    if spr:
        # spr is relative to the stage def's directory (or stages/)
        cand = os.path.join(os.path.dirname(full), spr)
        if not os.path.isfile(cand):
            cand2 = os.path.join(tree, "stages", spr)
            if not os.path.isfile(cand2):
                errs.append(f"{stage_def_path}: spr={spr} missing")
    else:
        errs.append(f"{stage_def_path}: no spr= in [StageInfo]")
    return errs


def parse_select_def(text):
    chars, stages = [], []
    section = None
    for line in text.splitlines():
        s = line.split(";", 1)[0].strip()
        if not s:
            continue
        if s.startswith("["):
            section = s.lower()
            continue
        if section == "[characters]":
            chars.append(s)
        elif section == "[extrastages]":
            stages.append(s)
    return chars, stages


def build(site, tree, spec_path):
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    # --- removals ---
    removed = []
    for prefix in spec.get("remove", []):
        for root, dirs, files in os.walk(tree, topdown=False):
            rel = os.path.relpath(root, tree).replace(os.sep, "/")
            if rel == ".":
                rel = ""
            for fn in files:
                p = (rel + "/" + fn) if rel else fn
                if p.startswith(prefix):
                    os.remove(os.path.join(root, fn))
                    removed.append(p)
            for d in dirs:
                p = (rel + "/" + d) if rel else d
                if p.startswith(prefix):
                    shutil.rmtree(os.path.join(root, d), ignore_errors=True)
    print(f"removed {len(removed)} files under: {spec.get('remove', [])}")

    # --- additions: characters ---
    char_defs = {}  # select entry -> def filename
    for vdir, src in spec.get("chars", {}).items():
        dest = os.path.join(tree, "chars", vdir)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print(f"char chars/{vdir} <- {src}")

    # --- additions: stages ---
    for vname, src in spec.get("stages", {}).items():
        dest = os.path.join(tree, "stages", vname)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print(f"stage stages/{vname} <- {src}")

    # --- select.def ---
    select_text = spec["select_def"]
    with open(os.path.join(tree, "data", "select.def"), "w", encoding="utf-8", newline="\n") as f:
        f.write(select_text)
    base_sel = os.path.join(site, "ikemen-fs", "base-select.def")
    with open(base_sel, "w", encoding="utf-8", newline="\n") as f:
        f.write(select_text)

    # --- motif select-grid tweak (optional) ---
    motif = spec.get("motif_select_grid")
    if motif:
        for rel in ("data/ikemen1/system.def",):
            p = os.path.join(tree, *rel.split("/"))
            with open(p, encoding="utf-8", errors="replace") as f:
                txt = f.read()
            txt = re.sub(r"(?m)^rows\s*=.*$", f"rows = {motif['rows']}", txt)
            txt = re.sub(r"(?m)^columns\s*=.*$", f"columns = {motif['columns']}", txt)
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(txt)
            print(f"motif grid -> rows={motif['rows']} columns={motif['columns']} in {rel}")

    # --- validation ---
    errs = []
    chars, stages = parse_select_def(select_text)
    for entry in chars:
        # entry like "goku/goku.def" (relative to chars/)
        vdir = "chars/" + entry.rsplit("/", 1)[0]
        errs += validate_char(tree, vdir)
        defpath = os.path.join(tree, "chars", *entry.split("/"))
        if not os.path.isfile(defpath):
            errs.append(f"select entry {entry}: .def missing at chars/{entry}")
    for entry in stages:
        errs += validate_stage(tree, entry)
    if errs:
        print("VALIDATION FAILED:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print(f"validation ok: {len(chars)} characters, {len(stages)} extra stages")

    # --- rebuild pak ---
    files = {}
    blob = bytearray()
    for root, _dirs, filenames in os.walk(tree):
        for fn in sorted(filenames):
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, tree).replace(os.sep, "/")
            with open(full, "rb") as f:
                data = f.read()
            files[rel] = [len(blob), len(data)]
            blob += data
    stamp = spec.get("stamp") or hashlib.sha256(bytes(blob)).hexdigest()[:12]
    # Chunked pack: Vercel Hobby caps a single uploaded file at 100 MB, so the
    # pak is split into <=50 MB parts (50 MB also fits the deploy tool's 120 s
    # per-file upload timeout more comfortably than 90 MB). The loader
    # (vfs.js) reassembles the parts byte-identically. No "pack" key is
    # written: the Mod Studio reads man.pack with a Range request, and a
    # missing pack would 404; omitting the key makes the Studio fall back
    # cleanly to "own files only".
    CHUNK = 50 * 1024 * 1024
    fs_dir = os.path.join(site, "ikemen-fs")
    parts = []
    for i in range(0, len(blob), CHUNK):
        part_name = f"game.pak.part{i // CHUNK}"
        with open(os.path.join(fs_dir, part_name), "wb") as f:
            f.write(bytes(blob[i:i + CHUNK]))
        parts.append({"file": part_name, "size": min(CHUNK, len(blob) - i)})
    # remove the old single pak and any stale parts beyond the new count
    keep = {p["file"] for p in parts}
    for fn in os.listdir(fs_dir):
        if fn == "game.pak" or (fn.startswith("game.pak.part") and fn not in keep):
            os.remove(os.path.join(fs_dir, fn))
    manifest = {"parts": parts, "files": files, "stamp": stamp}
    man_path = os.path.join(fs_dir, "manifest.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f)
    print(f"pak rebuilt: {len(files)} files, {len(blob)/1048576:.2f} MB, {len(parts)} parts, stamp {stamp}")
    print(f"  parts dir: {fs_dir}\n  manifest: {man_path}")
    return manifest


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("extract", "build"):
        print(__doc__)
        sys.exit(2)
    cmd = sys.argv[1]
    args = dict(zip(sys.argv[2::2], sys.argv[3::2]))
    site = args.get("--site", os.path.expanduser("~/workspace/webmugen-build/site"))
    tree = args.get("--tree", os.path.expanduser("~/workspace/webmugen-build/build/tree"))
    if cmd == "extract":
        extract(site, tree)
    else:
        build(site, tree, args["--spec"])


if __name__ == "__main__":
    main()
