import pytest

@pytest.fixture
def range_area():
    from app.polygon_builder.Rangearea import Rangearea

    range_area = Rangearea()

    return range_area