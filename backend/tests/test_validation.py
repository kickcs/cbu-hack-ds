"""Bad input: rejected loudly, or audited with the damage written down -- never repaired quietly."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.ingest import (
    MAX_FILE_BYTES,
    Role,
    check_upload,
    classify_frame,
    parse_amount,
    read_csv_any,
    resolve_column,
    safe_name,
    to_amounts,
    validate_register,
    validate_report,
)
from app.sampling import MIN_SAMPLE


def codes(issues) -> set[str]:
    return {i.code for i in issues}


# -- intake --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "size", "code"),
    [
        ("report.pdf", 100, "unsupported_format"),
        ("report", 100, "unsupported_format"),
        ("report.csv", 0, "empty_file"),
        ("report.csv", MAX_FILE_BYTES + 1, "file_too_large"),
    ],
)
def test_upload_rejected_before_it_is_written(name, size, code):
    assert codes(check_upload(name, size)) == {code}


def test_upload_accepted():
    assert check_upload("kredit_reyestri.CSV", 2048) == []


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("../../etc/passwd", "passwd"),
        ("..", "file"),
        ("", "file"),
        ("отчёт 2026.csv", "отчёт 2026.csv"),
        ("a/b/c.xlsx", "c.xlsx"),
    ],
)
def test_safe_name_cannot_escape_its_directory(raw, expected):
    assert safe_name(raw) == expected


# -- reading foreign files -----------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1 200 000", 1_200_000.0),
        ("1 200 000,50", 1_200_000.5),
        ("1,200,000.50", 1_200_000.5),
        # Anything carrying a unit or a placeholder is refused rather than guessed at.
        ("12 345,00 сум", None),
        ("", None),
        ("—", None),
        ("n/a", None),
    ],
)
def test_amount_parsing_covers_the_local_number_formats(raw, expected):
    assert parse_amount(raw) == expected


def test_unreadable_amounts_become_nan_not_zero():
    """A zero would carry a first digit into the histogram; NaN drops out of the test."""
    values, unreadable = to_amounts(pd.Series(["100", "abc", "", "200"]))
    assert unreadable == 2
    assert values.tolist()[0] == 100.0
    assert np.isnan(values.tolist()[1])


def test_csv_read_survives_separator_and_encoding(tmp_path):
    path = tmp_path / "reestr.csv"
    path.write_bytes("bank;summa\nAgro Bank;1 000\n".encode("cp1251"))
    frame = read_csv_any(path)
    assert list(frame.columns) == ["bank", "summa"]


def test_empty_csv_is_refused(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")
    with pytest.raises(ValueError):
        read_csv_any(path)


def test_column_resolution_ignores_case_and_wording():
    frame = pd.DataFrame(columns=["Bank Nomi", "Kredit summasi (so'm)"])
    assert resolve_column(frame, ("bank",)) == "Bank Nomi"
    assert resolve_column(frame, ("summa",)) == "Kredit summasi (so'm)"
    assert resolve_column(frame, ("period",)) is None


# -- classification ------------------------------------------------------------------


def test_unrecognisable_file_is_classified_unknown():
    assert classify_frame(pd.DataFrame({"a": [1], "b": [2]})) is Role.UNKNOWN


def test_register_and_normativ_are_told_apart():
    register = pd.DataFrame({"bank": ["A"], "kredit_summasi": [100]})
    normativ = pd.DataFrame({"bank": ["A"], "K1": [0.13], "LCR": [1.2]})
    assert classify_frame(register) is Role.REGISTER
    assert classify_frame(normativ) is Role.NORMATIV


# -- register defects ----------------------------------------------------------------


def register_frame(rows: int, bank: str = "Agro Bank") -> pd.DataFrame:
    rng = np.random.default_rng(3)
    return pd.DataFrame(
        {"bank": [bank] * rows, "kredit_summasi": rng.integers(10_000, 999_999, rows).astype(float)}
    )


def test_blank_bank_names_are_dropped_not_turned_into_a_phantom_bank():
    frame = register_frame(MIN_SAMPLE)
    frame.loc[0:4, "bank"] = ""
    cleaned, issues = validate_register(frame, "reestr.csv")
    assert "bank_missing" in codes(issues)
    assert set(cleaned["bank"]) == {"Agro Bank"}


def test_unreadable_and_nonpositive_amounts_are_reported():
    frame = register_frame(MIN_SAMPLE)
    frame["kredit_summasi"] = frame["kredit_summasi"].astype(object)
    frame.loc[0, "kredit_summasi"] = "не число"
    frame.loc[1, "kredit_summasi"] = 0
    _, issues = validate_register(frame, "reestr.csv")
    assert {"amounts_unreadable", "amounts_nonpositive"} <= codes(issues)


def test_duplicate_rows_are_flagged_because_they_inflate_the_sample():
    frame = pd.concat([register_frame(MIN_SAMPLE)] * 2, ignore_index=True)
    _, issues = validate_register(frame, "reestr.csv")
    assert "duplicate_rows" in codes(issues)


def test_small_bank_is_named_in_the_warning_not_silently_judged():
    frame = pd.concat([register_frame(MIN_SAMPLE), register_frame(10, bank="Davr Bank")])
    _, issues = validate_register(frame, "reestr.csv")
    small = next(i for i in issues if i.code == "sample_insufficient")
    assert "Davr Bank" in small.message and str(MIN_SAMPLE) in small.message


def test_register_without_usable_rows_is_an_error():
    frame = pd.DataFrame({"bank": ["A", "B"], "kredit_summasi": ["-", "n/a"]})
    _, issues = validate_register(frame, "reestr.csv")
    assert "register_empty" in codes(issues)


# -- report defects ------------------------------------------------------------------


def report_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "bank": ["A", "A", "B"],
            "period": ["2026-01", "2026-02", "2026-01"],
            "indicator": ["kapital"] * 3,
            "summa": [1.0, 2.0, 3.0],
        }
    )


def test_report_duplicates_and_single_period_banks_are_reported():
    frame = pd.concat([report_frame(), report_frame().head(1)], ignore_index=True)
    issues = validate_report(frame, "hisobotlar.csv", unknown_names=2)
    assert {"report_duplicates", "single_period", "indicators_unknown"} <= codes(issues)


def test_empty_report_is_an_error():
    empty = pd.DataFrame(columns=["bank", "period", "indicator", "summa"])
    assert codes(validate_report(empty, "hisobotlar.csv")) == {"report_empty"}
