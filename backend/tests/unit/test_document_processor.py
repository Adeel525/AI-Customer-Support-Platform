from app.utils.document_processor import clean_text, extract_from_text


def test_clean_text():
    text = "  Hello   world  \n\n\n  test  "
    cleaned = clean_text(text)
    assert "  " not in cleaned
    assert cleaned == "Hello world test"


def test_extract_from_text():
    content = b"Hello, this is a test document.\nIt has multiple lines."
    text, pages = extract_from_text(content)
    assert "Hello" in text
    assert pages == 1
