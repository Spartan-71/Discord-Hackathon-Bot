import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import bot
from backend.schemas import Hackathon


def build_hack(hack_id: str, source: str = "devpost", tags: list[str] | None = None):
    from datetime import date, timedelta

    return Hackathon(
        id=hack_id,
        title=f"Hack {hack_id}",
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=3),
        location="Online",
        url=f"https://example.com/{hack_id}",
        mode="Online",
        status="Open",
        source=source,
        tags=tags or ["ai"],
    )


def test_send_standard_paginated_notification_single_uses_embed_path(monkeypatch):
    fake_channel = SimpleNamespace(send=AsyncMock())
    fake_embed = object()
    fake_view = SimpleNamespace(children=[])
    monkeypatch.setattr(bot, "format_hackathon_embed", lambda _: ("hello", fake_embed, fake_view))

    asyncio.run(bot.send_standard_paginated_notification(fake_channel, [build_hack("n1")]))

    fake_channel.send.assert_awaited_once_with(content="hello", embed=fake_embed, view=fake_view)


def test_send_standard_paginated_notification_multiple_uses_paginator():
    fake_channel = SimpleNamespace(send=AsyncMock())
    hacks = [build_hack("n1"), build_hack("n2")]

    asyncio.run(bot.send_standard_paginated_notification(fake_channel, hacks))

    fake_channel.send.assert_awaited_once()
    kwargs = fake_channel.send.await_args.kwargs
    assert "Found **2** hackathon(s)" in kwargs["content"]
    assert kwargs["view"] is not None


def test_send_paginated_hackathons_routes_by_context(monkeypatch):
    fake_channel = SimpleNamespace(send=AsyncMock())
    hacks = [build_hack("n1"), build_hack("n2")]
    scheduled = AsyncMock()
    standard = AsyncMock()
    monkeypatch.setattr(bot, "send_scheduled_notification_with_pagination", scheduled)
    monkeypatch.setattr(bot, "send_standard_paginated_notification", standard)

    asyncio.run(bot.send_paginated_hackathons(fake_channel, hacks, context_type="scheduled"))
    asyncio.run(bot.send_paginated_hackathons(fake_channel, hacks, context_type="manual"))
    asyncio.run(bot.send_paginated_hackathons(fake_channel, [], context_type="scheduled"))

    scheduled.assert_awaited_once_with(fake_channel, hacks)
    standard.assert_awaited_once_with(fake_channel, hacks)


def test_send_hackathon_notifications_skips_when_missing_permissions(monkeypatch):
    send_paginated = AsyncMock()
    monkeypatch.setattr(bot, "send_paginated_hackathons", send_paginated)

    permissions = SimpleNamespace(send_messages=False, embed_links=True)
    target_channel = SimpleNamespace(
        id=123,
        guild=SimpleNamespace(me=object()),
        permissions_for=lambda _member: permissions,
    )

    asyncio.run(
        bot.send_hackathon_notifications(
            bot=SimpleNamespace(guilds=[]),
            new_hackathons=[build_hack("h1")],
            target_channel=target_channel,
        )
    )

    send_paginated.assert_not_awaited()


def test_send_hackathon_notifications_target_channel_uses_manual_fetch(monkeypatch):
    send_paginated = AsyncMock()
    monkeypatch.setattr(bot, "send_paginated_hackathons", send_paginated)

    permissions = SimpleNamespace(send_messages=True, embed_links=True)
    target_channel = SimpleNamespace(
        id=321,
        guild=SimpleNamespace(me=object()),
        permissions_for=lambda _member: permissions,
    )
    hacks = [build_hack("h1"), build_hack("h2")]

    asyncio.run(
        bot.send_hackathon_notifications(
            bot=SimpleNamespace(guilds=[]),
            new_hackathons=hacks,
            target_channel=target_channel,
        )
    )

    send_paginated.assert_awaited_once_with(
        channel=target_channel,
        hackathons=hacks,
        context_type="manual_fetch",
    )
