"""Offline source-integrity checks for a Power BI Project (PBIP/PBIR).

Does NOT claim Microsoft Power BI Desktop or PBIX compatibility.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


class ProjectValidationError(ValueError):
    pass


def _json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectValidationError(f"Invalid or missing JSON: {path}") from exc
    if not isinstance(data, dict):
        raise ProjectValidationError(f"Expected object in: {path}")
    return data


def verify_project(root: Path) -> dict:
    root = Path(root)
    manifest = _json(root / "AirAware.pbip")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ProjectValidationError("PBIP must reference exactly one report")
    report_name = artifacts[0].get("report", {}).get("path")
    if report_name != "AirAware.Report":
        raise ProjectValidationError("Unexpected report path")
    report = root / report_name
    pbir = _json(report / "definition.pbir")
    semantic_rel = pbir.get("datasetReference", {}).get("byPath", {}).get("path")
    if semantic_rel != "../AirAware.SemanticModel":
        raise ProjectValidationError("Report must reference the bundled semantic model")
    model_dir = root / "AirAware.SemanticModel"
    _json(model_dir / "definition.pbism")
    model = _json(model_dir / "model.bim").get("model", {})
    readings = next((t for t in model.get("tables", []) if t.get("name") == "Readings"), None)
    if not readings:
        raise ProjectValidationError("Semantic model is missing Readings table")
    cols = {c.get("name") for c in readings.get("columns", [])}
    if not {"date", "station", "pm25", "source"}.issubset(cols):
        raise ProjectValidationError("Semantic model is missing required data columns")
    measures = {m.get("name") for m in readings.get("measures", [])}
    page_root = report / "definition" / "pages"
    pages_json = _json(page_root / "pages.json")
    names = pages_json.get("pageOrder", [])
    if not isinstance(names, list) or len(names) < 2 or len(names) != len(set(names)):
        raise ProjectValidationError("Expected at least 2 unique report pages")
    if pages_json.get("activePageName") not in names:
        raise ProjectValidationError("Active page is not in the page order")
    visual_count = 0
    for name in names:
        if not isinstance(name, str) or "/" in name or "\\" in name or name in ("", ".", ".."):
            raise ProjectValidationError("Unsafe page name")
        folder = page_root / name
        page = _json(folder / "page.json")
        if page.get("name") != name:
            raise ProjectValidationError(f"Page filename/name mismatch: {name}")
        visuals = sorted((folder / "visuals").glob("*/visual.json"))
        if not visuals:
            raise ProjectValidationError(f"Page has no visuals: {name}")
        for visual_path in visuals:
            data = _json(visual_path)
            if data.get("name") != visual_path.parent.name:
                raise ProjectValidationError(f"Visual name mismatch: {visual_path}")
            if not isinstance(data.get("visual", {}).get("visualType"), str):
                raise ProjectValidationError(f"Visual type missing: {visual_path}")
            # Check that all known measure projections reference actual model measures.
            for projection in _walk(data):
                if isinstance(projection, dict) and "Measure" in projection:
                    m = projection["Measure"]
                    if isinstance(m, dict) and m.get("Property") not in measures:
                        raise ProjectValidationError(f"Unknown measure {m.get('Property')}: {visual_path}")
            visual_count += 1
    return {"status": "source_structure_verified_only", "pages": len(names), "visuals": visual_count,
            "tables": len(model.get("tables", [])), "report": report_name,
            "limitations": "Does not validate Power BI Desktop execution, refresh or PBIX export"}


def _walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _walk(value)
    elif isinstance(obj, list):
        for child in obj:
            yield from _walk(child)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=Path("powerbi/AirAwareReport"))
    args = parser.parse_args()
    print(json.dumps(verify_project(args.path), indent=2))


if __name__ == "__main__":
    main()
