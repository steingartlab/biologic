import json
import pytest

from biologic import techniques


@pytest.fixture
def technique():
    technique = techniques.Technique()

    return technique

def test_set_technique_params(technique: techniques.Technique):
    technique.set_technique_params()
    # assert isinstance(technique.c_technique_params, structures.TEccParams)



