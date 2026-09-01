from __future__ import annotations

from pipeline.pii.pii_guard import PIIGuard


def test_masks_string_values_by_sensitive_key() -> None:
    data = {"test_data": {"email": "user@example.com", "password": "secret123"}}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked["test_data"]["email"] == "<EMAIL>"
    assert masked["test_data"]["password"] == "<PASSWORD>"
    assert report.pii_detected is True
    assert report.total_matches == 2


def test_does_not_mask_locator_dicts_named_like_sensitive_fields() -> None:
    data = {
        "pages": [
            {
                "elements": {
                    "password": {"locator": "#Password", "type": "input"},
                }
            }
        ]
    }

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked["pages"][0]["elements"]["password"]["locator"] == "#Password"
    assert masked["pages"][0]["elements"]["password"]["type"] == "input"
    assert report.pii_detected is False


def test_masks_email_and_phone_patterns() -> None:
    data = {"text": "Contact user@example.com at +7 123 456-78-90"}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked["text"] == "Contact <EMAIL> at <PHONE>"
    assert {m.type for m in report.matches} == {"EMAIL", "PHONE"}


def test_leaves_numeric_and_other_values_untouched() -> None:
    data = {"token": 12345, "name": "Alice"}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked == {"token": 12345, "name": "Alice"}
    assert report.pii_detected is False