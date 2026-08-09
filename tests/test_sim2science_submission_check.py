from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_checker() -> ModuleType:
    root = Path(__file__).resolve().parents[1]
    path = root / "papers/paper_a_methods/workshops/sim2science/check_submission.py"
    spec = importlib.util.spec_from_file_location("sim2science_submission_check", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pdfinfo_parser_preserves_colons_in_values() -> None:
    checker = _load_checker()
    parsed = checker.parse_pdfinfo("Author: Anonymous\nCreationDate: Fri 10:20:30\n")
    assert parsed == {"Author": "Anonymous", "CreationDate": "Fri 10:20:30"}


def test_reference_page_uses_first_standalone_heading() -> None:
    checker = _load_checker()
    pages = ["A sentence mentions references.\n", "  133   References  \nEntry\n"]
    assert checker.reference_page(pages) == 2
    assert checker.reference_page(["No heading\n"]) is None


def test_main_text_limit_rejects_content_before_page_six_references() -> None:
    checker = _load_checker()
    clean = ["main\n"] * 5 + ["  163   References  \nEntry\n"]
    overflow = ["main\n"] * 5 + ["Conclusion overflow\n  163   References  \nEntry\n"]
    assert checker.main_text_within_five_pages(clean)
    assert not checker.main_text_within_five_pages(overflow)
