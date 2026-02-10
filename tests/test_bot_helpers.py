import asyncio
from datetime import date, timedelta

from backend.schemas import Hackathon
from bot import HackathonPaginator, format_hackathon_embed


def build_hack(hack_id: str, *, with_banner: bool = True, with_url: bool = True):
    return Hackathon(
        id=hack_id,
        title=f"Hack {hack_id}",
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=3),
        location="Online",
        url=f"https://example.com/{hack_id}" if with_url else "",
        mode="Online",
        status="Open",
        source="devpost",
        tags=["ai"],
        banner_url="https://example.com/banner.png" if with_banner else None,
        prize_pool="$5,000",
        team_size="1-4",
        eligibility="All",
    )


def test_format_hackathon_embed_with_banner_and_link():
    hack = build_hack("embed-1", with_banner=True, with_url=True)

    async def run():
        return format_hackathon_embed(hack)

    msg, embed, view = asyncio.run(run())

    assert "Hack embed-1" in msg
    assert "Duration:" in msg
    assert embed is not None
    assert embed.image.url == "https://example.com/banner.png"
    assert len(view.children) == 1
    assert view.children[0].url == "https://example.com/embed-1"


def test_format_hackathon_embed_without_banner_or_link():
    hack = build_hack("embed-2", with_banner=False, with_url=False)

    async def run():
        return format_hackathon_embed(hack)

    msg, embed, view = asyncio.run(run())

    assert "Hack embed-2" in msg
    assert embed is None
    assert len(view.children) == 0


def test_paginator_button_state_and_footer():
    hacks = [build_hack("page-1"), build_hack("page-2")]

    async def run():
        paginator = HackathonPaginator(hacks, context_type="manual")

        assert paginator.current_index == 0
        assert paginator.previous_button.disabled is True
        assert paginator.next_button.disabled is False

        _, first_embed, _ = paginator.create_embed()
        assert first_embed is not None
        assert first_embed.footer.text == "📄 1/2"

        paginator.current_index = 1
        paginator.update_buttons()

        assert paginator.previous_button.disabled is False
        assert paginator.next_button.disabled is True

        _, second_embed, _ = paginator.create_embed()
        assert second_embed is not None
        assert second_embed.footer.text == "📄 2/2"

    asyncio.run(run())
