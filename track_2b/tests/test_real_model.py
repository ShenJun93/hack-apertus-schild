import os

import pytest

from schild.config import load_settings
from schild.llm_detector import LlmDetector

pytestmark = pytest.mark.skipif(not os.environ.get("LLM_API_KEY"), reason="needs a real model endpoint")

CASES = [
    ("Ich überweise Ihnen Anna Keller. Sie leidet an Epilepsie.", {"Anna Keller", "Epilepsie"}),
    ("Je vous adresse Marc Favre, domicilié chemin des Lilas 12, 1004 Lausanne.", {"Marc Favre"}),
    ("La signora Rosa Bianchi riceve l'assistenza sociale.", {"Rosa Bianchi"}),
]


@pytest.mark.parametrize("text, must_find", CASES)
def test_real_model_finds_names(text, must_find):
    s = load_settings()
    found = {sp.text for sp in LlmDetector(s.llm_base_url, s.llm_api_key, s.llm_name).detect(text).spans}
    missing = {m for m in must_find if not any(m in f or f in m for f in found)}
    assert not missing, f"model missed {missing}; found {found}"
