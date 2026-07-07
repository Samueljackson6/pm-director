"""pm-director backend package.

Makes ``backend`` a regular (importable) package so that the absolute
imports used throughout the codebase (``from backend.database import ...``,
``from backend.routers import ...``) resolve reliably, including under the
pytest ``pythonpath`` configuration defined in ``backend/pytest.ini``.
"""
