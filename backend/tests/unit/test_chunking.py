from core.utils.chunking import estimate_tokens, split_text


def test_split_text():
    text = "This is a test paragraph. " * 100
    chunks = split_text(text, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    assert all(len(chunk) > 0 for chunk in chunks)


def test_estimate_tokens():
    text = "Hello world, this is a test."
    tokens = estimate_tokens(text)
    assert tokens > 0
    assert tokens == len(text) // 4
