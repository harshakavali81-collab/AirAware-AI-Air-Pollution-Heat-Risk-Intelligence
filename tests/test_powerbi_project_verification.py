from pathlib import Path
import json
import shutil
import pytest
from scripts.verify_powerbi_project import ProjectValidationError, verify_project

PROJECT = Path(__file__).resolve().parents[1] / "powerbi" / "AirAwareReport"


def test_original_powerbi_project_structure():
    outcome = verify_project(PROJECT)
    assert outcome["status"] == "source_structure_verified_only"
    assert outcome["pages"] == 2
    assert outcome["visuals"] == 5


def test_missing_semantic_model_is_rejected(tmp_path):
    shutil.copytree(PROJECT, tmp_path / "pbip")
    (tmp_path / "pbip" / "AirAware.SemanticModel" / "model.bim").unlink()
    with pytest.raises(ProjectValidationError, match="missing JSON"):
        verify_project(tmp_path / "pbip")


def test_broken_page_order_is_rejected(tmp_path):
    shutil.copytree(PROJECT, tmp_path / "pbip")
    p = tmp_path / "pbip" / "AirAware.Report" / "definition" / "pages" / "pages.json"
    data = json.loads(p.read_text())
    data["activePageName"] = "not-a-page"
    p.write_text(json.dumps(data))
    with pytest.raises(ProjectValidationError, match="Active page"):
        verify_project(tmp_path / "pbip")


def test_unrecognized_measure_is_rejected(tmp_path):
    shutil.copytree(PROJECT, tmp_path / "pbip")
    p = tmp_path / "pbip" / "AirAware.Report" / "definition" / "pages" / "AirQualityOverview" / "visuals" / "KPI_AvgPM25" / "visual.json"
    data = json.loads(p.read_text())
    data["visual"]["query"]["queryState"]["Values"]["projections"][0]["field"]["Measure"]["Property"] = "not_existing"
    p.write_text(json.dumps(data))
    with pytest.raises(ProjectValidationError, match="Unknown measure"):
        verify_project(tmp_path / "pbip")
