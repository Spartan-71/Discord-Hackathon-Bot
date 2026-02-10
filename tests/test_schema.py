from datetime import date

from backend.schemas import Hackathon


def test_schema_splits_and_normalizes_tags_from_string():
    hack = Hackathon(
        id="hack-schema-1",
        title="Schema Hackathon",
        start_date=date.today(),
        end_date=date.today(),
        location="Online",
        url="https://example.com/schema",
        mode="Online",
        status="Open",
        source="devpost",
        tags=" AI ,  Data Science,WEB ",
    )

    assert hack.tags == ["ai", "data science", "web"]


def test_schema_accepts_list_tags_without_mutation():
    hack = Hackathon(
        id="hack-schema-2",
        title="Schema Hackathon 2",
        start_date=date.today(),
        end_date=date.today(),
        location="Online",
        url="https://example.com/schema2",
        mode="Hybrid",
        status="Open",
        source="devfolio",
        tags=["AI", "Cloud"],
    )

    assert hack.tags == ["AI", "Cloud"]
