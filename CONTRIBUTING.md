# Contributing

Thanks for improving the AirAware AI educational portfolio. Issues or pull requests should explain intended behavior, data source/provenance, changes to units or timestamps, and validation tests.

1. Fork and create a feature branch.
2. `python -m pip install -e '.[dev]'` and `python -m pytest -q`.
3. For frontend changes, run `cd frontend && npm install && npm run build`.
4. For figures, run `python -m scripts.make_assets && python -m scripts.make_gallery`; label synthetic examples.
5. Do not commit API keys, user location traces, third-party graphics without permission, or unsupported medical recommendations.
