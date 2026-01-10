import os
import logging
import json
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from fetch_and_store import run as fetch_and_store_hackathons
# from backend.db import Base, engine
import backend.models

load_dotenv()

intents = discord.Intents.default()  # no privileged intents required for slash commands
intents.guilds = True  # needed to see guilds and channels


class MyClient(discord.Client):
    def __init__(self, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


    async def setup_hook(self):

        # Start the background task once the bot is ready
        if not check_and_notify_hackathons.is_running():
            check_and_notify_hackathons.start(self)

    async def on_ready(self):

        print(f"Logged on as {self.user}")
        
        # Sync commands after bot is ready - sync to each guild for instant updates
    
        try:
            # Sync to each guild for instant updates (faster than global sync)
            for guild in self.guilds:
                try:
                    synced = await self.tree.sync(guild=guild)
                    print(f"Synced {len(synced)} commands to {guild.name}")
                except Exception as e:

                    print(f"Failed to sync commands to {guild.name}: {e}")
            
            # Also sync globally (takes up to 1 hour but ensures commands work everywhere)
 
            synced_global = await self.tree.sync()

            print(f"Synced {len(synced_global)} commands globally")
        except Exception as e:
            print(f"Error syncing commands: {e}")


client = MyClient(intents=intents)


@client.tree.command(name="hi", description="Say hi")
async def hi(interaction: discord.Interaction):

    welcome_msg = (
        "👋 **Hello there!**\n\n"
        "I'm **HackRadar**, your personal hackathon assistant! 🚀\n"
        "I can help you find the latest hackathons from **Devpost**, **MLH**, **Devfolio**, and more.\n\n"
        "Use `/fetch` to manually check for new hackathons right now!\n"
        "I also run in the background to keep you updated automatically. Happy Hacking! 💻✨"
    )
    await interaction.response.send_message(welcome_msg)


@client.tree.command(name="fetch", description=
"Manually fetch hackathons and send notifications for newly added ones")
async def fetch(interaction: discord.Interaction):
    """Manually trigger hackathon fetching and send notifications."""
    # Defer the response since fetching might take some time
    await interaction.response.defer(thinking=True)
    
    try:
        logging.info(f"Manual fetch triggered by {interaction.user} in guild {interaction.guild_id}")
        
        # Run the fetch
        new_hackathons = fetch_and_store_hackathons()
        
        if not new_hackathons:
            await interaction.followup.send("✅ Fetch completed! No new hackathons found.")
            logging.info("Manual fetch completed: No new hackathons")
            return
        
        # Send summary message
        await interaction.followup.send(
            f"✅ Fetch completed! Found **{len(new_hackathons)}** new hackathon(s). Sending notifications..."
        )
        
        # Send notifications to the current channel
        channel = interaction.channel
        if channel and channel.permissions_for(interaction.guild.me).send_messages:
            await send_hackathon_notifications(client, new_hackathons, target_channel=channel)
            logging.info(f"Manual fetch completed: Sent {len(new_hackathons)} notifications")
        else:
            await interaction.followup.send(
                "⚠️ Fetch completed but I don't have permission to send messages in this channel."
            )
            logging.warning(f"Manual fetch completed but no permission to send in channel {channel.id}")
            
    except Exception as e:
        error_msg = f"❌ Error during fetch: {str(e)}"
        await interaction.followup.send(error_msg)
        logging.error(f"Error in manual fetch command: {e}")

def format_hackathon_embed(hackathon):
    """Create a Discord embed for a hackathon notification."""

    # Plain markdown with bold keys and highlighted values
    msg = f"## 🎉 New Hackathon: **{hackathon.title}**\n\n"
    msg += f"---\n"
    msg += f"**Duration:** {hackathon.start_date.strftime('%B %d')} - {hackathon.end_date.strftime('%B %d, %Y')}\n"
    msg += f"**Location:** {hackathon.location}\n"
    msg += f"**Mode:** {hackathon.mode}\n"
    msg += f"**Status:** {hackathon.status}\n"
    msg += f"---\n"
    msg += f"**Register Here**: {hackathon.url}"

    embed = None
    if hackathon.banner_url:
        embed = discord.Embed()
        embed.set_image(url=hackathon.banner_url)

    return msg, embed


async def send_hackathon_notifications(bot: MyClient, new_hackathons, target_channel=None):
    """
    Send hackathon notifications to channels.
    If target_channel is provided, send there. Otherwise, send to all guilds.
    """
    if not new_hackathons:
        return
    
    if target_channel:
        # Send to specific channel (for manual fetch command)
        for hackathon in new_hackathons:
            try:
                msg, embed = format_hackathon_embed(hackathon)
                await target_channel.send(msg, embed=embed)
                logging.info(f"Sent notification for hackathon '{hackathon.title}' to channel {target_channel.id}")
            except Exception as e:
                logging.error(f"Failed to send hackathon notification to channel {target_channel.id}: {e}")
    else:
        # Send to all guilds (for scheduled task)
        for guild in bot.guilds:
            channel = None

            # Prefer the system channel if available
            if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
                channel = guild.system_channel
            else:
                # Fallback: first text channel where the bot can send messages
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break

            if channel is None:
                logging.warning(f"No suitable channel found in guild {guild.id}")
                continue

            # Send notification for each new hackathon
            for hackathon in new_hackathons:
                try:
                    msg, embed = format_hackathon_embed(hackathon)
                    await channel.send(msg, embed=embed)
                    logging.info(f"Sent notification for hackathon '{hackathon.title}' to guild {guild.id}")
                except Exception as e:
                    logging.error(f"Failed to send hackathon notification in guild {guild.id}: {e}")


@tasks.loop(hours=12)  # Run every 12 hours (adjust as needed: seconds=30, minutes=5, hours=12, etc.)
async def check_and_notify_hackathons(bot: MyClient):
    """Background task that fetches hackathons and sends notifications for newly added ones."""
    if not bot.guilds:
        logging.warning("Bot is not in any guilds, skipping hackathon check")
        return

    try:
        logging.info("Starting hackathon fetch and notification check")
        new_hackathons = fetch_and_store_hackathons()
        
        if not new_hackathons:
            logging.info("No new hackathons found")
            return
        
        logging.info(f"Found {len(new_hackathons)} new hackathons, sending notifications")
        
        # Send notifications to all guilds
        await send_hackathon_notifications(bot, new_hackathons)
        
        logging.info("Completed hackathon notifications")
        
    except Exception as e:
        logging.error(f"Error in check_and_notify_hackathons task: {e}")


@check_and_notify_hackathons.before_loop
async def before_check_and_notify():
    """Wait until the bot is ready before starting the task."""
    await client.wait_until_ready()


token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("DISCORD_TOKEN is not set in the environment")

client.run(token)