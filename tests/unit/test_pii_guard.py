from pipeline.pii_guard import PIIGuard


def test_masks_email() -> None:
    data = {"email": "user@example.com"}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked["email"] == "<EMAIL>"
    assert report.pii_detected is True
    assert report.total_matches == 1
    assert report.matches[0].type == "EMAIL"


def test_masks_password() -> None:
    data = {"password": "DemoPassword123"}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked["password"] == "<PASSWORD>"
    assert report.total_matches == 1
    assert report.matches[0].type == "PASSWORD"


def test_masks_phone() -> None:
    data = {"phone": "+375291234567"}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked["phone"] == "<PHONE>"
    assert report.total_matches == 1
    assert report.matches[0].type == "PHONE"


def test_masks_pii_inside_text() -> None:
    data = {"description": "Contact user@example.com or call +375291234567"}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked["description"] == ("Contact <EMAIL> or call <PHONE>")
    assert report.total_matches == 2


def test_masks_nested_data() -> None:
    data = {"user": {"credentials": {"email": "user@example.com","password": "DemoPassword123" }}}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked["user"]["credentials"]["email"] == "<EMAIL>"
    assert masked["user"]["credentials"]["password"] == "<PASSWORD>"
    assert report.total_matches == 2


def test_masks_list_items() -> None:
    data = {"users": [{"email": "one@example.com"},{"email": "two@example.com"}]}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked["users"][0]["email"] == "<EMAIL>"
    assert masked["users"][1]["email"] == "<EMAIL>"
    assert report.total_matches == 2


def test_original_data_is_not_modified() -> None:
    data = {"email": "user@example.com","password": "DemoPassword123"}

    PIIGuard().scan_and_mask(data)

    assert data["email"] == "user@example.com"
    assert data["password"] == "DemoPassword123"


def test_no_pii() -> None:
    data = {"name": "Test User","age": 30}

    masked, report = PIIGuard().scan_and_mask(data)

    assert masked == data
    assert report.pii_detected is False
    assert report.total_matches == 0


def test_report_does_not_contain_raw_pii() -> None:
    data = {"email": "user@example.com", "password": "DemoPassword123"}

    _, report = PIIGuard().scan_and_mask(data)

    report_json = report.model_dump_json()

    assert "user@example.com" not in report_json
    assert "DemoPassword123" not in report_json