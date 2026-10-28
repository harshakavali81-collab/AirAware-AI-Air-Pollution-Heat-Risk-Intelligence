"""Structural checks, not a substitute for opening report in Power BI Desktop."""
import json
from pathlib import Path


def test_native_powerbi_project_structure():
    base = Path(__file__).resolve().parents[1] / 'powerbi' / 'AirAwareReport'
    project = json.loads((base/'AirAware.pbip').read_text())
    assert project['artifacts'][0]['report']['path'] == 'AirAware.Report'
    report = json.loads((base/'AirAware.Report/definition.pbir').read_text())
    assert report['datasetReference']['byPath']['path'] == '../AirAware.SemanticModel'
    model = json.loads((base/'AirAware.SemanticModel/model.bim').read_text())
    assert model['model']['tables'][0]['name'] == 'Readings'
    assert 'SYNTHETIC DEMO' in model['model']['tables'][0]['partitions'][0]['source']['expression']
    pages = json.loads((base/'AirAware.Report/definition/pages/pages.json').read_text())
    assert len(pages['pageOrder']) == 2
    visuals = list((base/'AirAware.Report/definition/pages').rglob('visual.json'))
    assert len(visuals) >= 5
    for path in visuals:
        visual = json.loads(path.read_text())
        assert visual['visual']['visualType'] and visual['$schema']
