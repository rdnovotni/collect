"""Command-line interface: `collect <command>`."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, SPEC_VERSION
from .csvmap import CsvError, csv_to_records, records_to_csv
from .validate import check_standard, issues_to_json, load_records, to_sarif, validate_records


def _report(issues, fmt: str, strict: bool, count: int | None = None) -> int:
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    if fmt == "json":
        print(issues_to_json(issues))
    elif fmt == "sarif":
        print(to_sarif(issues))
    else:
        for i in issues:
            print(i)
        what = f"{count} record(s): " if count is not None else ""
        print(f"{what}{len(errors)} error(s), {len(warnings)} warning(s)")
    failed = bool(errors) or (strict and bool(warnings))
    return 1 if failed else 0


def cmd_validate(args) -> int:
    # Each package directory is a self-contained dataset. All other files given
    # together form one dataset, so references can cross between them.
    groups: list[list] = []
    loose: list = []
    for p in args.paths:
        path = Path(p)
        try:
            recs = load_records(path)
        except (OSError, json.JSONDecodeError) as e:
            print(f"ERROR   {p}: could not read: {e}", file=sys.stderr)
            return 2
        if path.is_dir() and (path / "datapackage.json").is_file():
            groups.append(recs)
        else:
            loose.extend(recs)
    if loose:
        groups.append(loose)
    issues = [i for g in groups for i in validate_records(g)]
    return _report(issues, args.format, args.strict, sum(len(g) for g in groups))


def cmd_check_standard(args) -> int:
    return _report(check_standard(), args.format, args.strict)


def cmd_csv2json(args) -> int:
    text = Path(args.input).read_text(encoding="utf-8-sig")
    try:
        records = csv_to_records(text)
    except CsvError as e:
        print(f"ERROR   {args.input}: {e}", file=sys.stderr)
        return 1
    if args.jsonl:
        out = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    else:
        out = json.dumps(records, indent=2, ensure_ascii=False) + "\n"
    _write(args.output, out)
    return 0


def cmd_json2csv(args) -> int:
    records = []
    for p in args.inputs:
        records.extend(r.data for r in load_records(Path(p)))
    text, dropped = records_to_csv(records)
    _write(args.output, text)
    for note in dropped:
        print(f"NOTE    {note}", file=sys.stderr)
    return 0


def _write(dest: str | None, text: str) -> None:
    if dest:
        Path(dest).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="collect", description=f"Tools for the Collect data standard (v{SPEC_VERSION}).")
    ap.add_argument("--version", action="version", version=f"collect-tools {__version__} (spec {SPEC_VERSION})")
    sub = ap.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="validate record files, JSONL files or package directories")
    v.add_argument("paths", nargs="+")
    v.add_argument("--strict", action="store_true", help="treat warnings as errors")
    v.add_argument("--format", choices=["text", "json", "sarif"], default="text")
    v.set_defaults(func=cmd_validate)

    s = sub.add_parser("check-standard", help="validate the standard's own profiles and vocabularies")
    s.add_argument("--strict", action="store_true")
    s.add_argument("--format", choices=["text", "json", "sarif"], default="text")
    s.set_defaults(func=cmd_check_standard)

    c = sub.add_parser("csv2json", help="convert a CSV spreadsheet to Collect records")
    c.add_argument("input")
    c.add_argument("-o", "--output")
    c.add_argument("--jsonl", action="store_true", help="write one record per line")
    c.set_defaults(func=cmd_csv2json)

    j = sub.add_parser("json2csv", help="flatten Collect records into a CSV spreadsheet (lossy)")
    j.add_argument("inputs", nargs="+")
    j.add_argument("-o", "--output")
    j.set_defaults(func=cmd_json2csv)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
