from unittest.mock import MagicMock, patch
import pytest

from openai import OpenAI
from main import get_openai_client, get_region_name_keyword_extract
from settings.settings import settings


def test_get_openai_client() -> None:
    client = get_openai_client()
    assert isinstance(client, OpenAI)
    assert client.api_key == settings.openai_api_key


# @pytest.mark.skip
@pytest.mark.parametrize(
    "query, expected",
    [
        ("서울의 날씨 알려줘", "서울"),
        ("오늘 경기도 날씨 알려줘", "경기도"),
        ("제주도 날씨 어때?", "제주도"),
    ],
)
def test_get_region_name_keyword_extract(query: str, expected: str) -> None:
    mock_client = MagicMock(spec=OpenAI)
    mock_response = MagicMock()
    mock_response.choices[0].message.content = expected
    mock_client.chat.completions.create.return_value = mock_response

    assert get_region_name_keyword_extract(mock_client, query) == expected
    mock_client.chat.completions.create.assert_called_once()
