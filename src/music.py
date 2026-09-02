from discord.ext import commands
import discord
from discord import app_commands

import asyncio
import logging
import youtube_dl
import yt_dlp
import math
from urllib import request

from .exception.NotInVoiceChannelException import NotInVoiceChannelException
from .video import Video, Playlist, Video_Full
import ffmpeg
import random

import settings

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist"
}

FFMPEG_BEFORE_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
# ffmpeg args go here ^


async def audio_playing(interaction):
    client = interaction.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        return False


async def in_voice_channel(interaction):
    voice = interaction.user.voice
    bot_voice = interaction.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        return False


async def is_audio_requester(ctx):
    """Checks that the command sender is the song requester."""
    music = ctx.bot.get_cog("Music")
    state = music.get_state(ctx.guild)
    permissions = ctx.channel.permissions_for(ctx.author)
    if permissions.administrator or state.is_requester(ctx.author):
        return True
    else:
        return None


class Music(commands.Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.states = {}
        self.bot.add_listener(self.on_reaction_add, "on_reaction_add")


    def get_state(self, guild):
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @app_commands.command()
    @commands.guild_only()
    # @commands.has_permissions(administrator=True)
    async def stop(self, interaction: discord.Interaction):
        """Disconnect the music player"""
        await interaction.response.defer(thinking=True)

        client = interaction.guild.voice_client
        state = self.get_state(interaction.guild)

        if client and client.channel:
            state.playlist = []
            state.now_playing = None
            await client.disconnect(force=False)
            await interaction.edit_original_response(content="", embed=discord.Embed(description="Stopped music"))
        else:
            await interaction.edit_original_response(content="", embed=discord.Embed(description="Must be in voice channel to play music"))

    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    @commands.check(is_audio_requester)
    async def pause(self, interaction: discord.Interaction):
        """Pause the music player"""

        client = interaction.guild.voice_client
        self._pause_audio(client)

        if client.is_paused():
            await interaction.response.send_message("", embed=discord.Embed(description="Paused"))
        else:
            await interaction.response.send_message("", embed=discord.Embed(description="Unpaused"))

    def _pause_audio(self, client):     # pause/resume based on current player state
        if client.is_paused():
            client.resume()
        else:
            client.pause()

    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    async def skip(self, interaction: discord.Interaction):
        """Skip the currently playing song"""

        state = self.get_state(interaction.guild)
        client = interaction.guild.voice_client

        if not settings.settings["musicVoteSkip"] and not settings.settings["musicSkipRequiresAdmin"]:
            client.stop()
            await interaction.response.send_message("", embed=discord.Embed(description="Skipping song"))

        elif interaction.channel.permissions_for(interaction.user).administrator:
            client.stop()
            await interaction.response.send_message("", embed=discord.Embed(description="Skipping song"))

        else:
            if interaction.channel.permissions_for(interaction.user).administrator\
                    or state.is_requester(interaction.user):
                client.stop()
                await interaction.response.send_message("", embed=discord.Embed(description="Skipping song"))

            else:
                channel = client.channel
                self._vote_skip(channel, interaction.user)

                # announce vote
                users_in_channel = len([member for member in channel.members if not member.bot])    # no robots allowed
                required_votes = math.ceil(settings.settings["voteSkipRatio"] * users_in_channel)
                await interaction.response.send_message("",
                    embed=discord.Embed(description=f"{interaction.user.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes"))

    def _vote_skip(self, channel, member):
        logging.info(f"{member.name} votes to skip")
        state = self.get_state(channel.guild)
        state.skip_votes.add(member)
        users_in_channel = len([member for member in channel.members if not member.bot])    # no bots here either
        if (float(len(state.skip_votes)) / users_in_channel) >= settings.settings["musicVoteSkipRatio"]:
            logging.info(f"Skipping track")
            channel.guild.voice_client.stop()

    def _play_song(self, client, state, song):
        state.now_playing = song
        state.skip_votes = set()    # clear votes to skip
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=1.0)

        def after_playing(err):
            if len(state.playlist) > 0:
                next_song_short = state.playlist.pop(0)
                try:
                    next_song = Video_Full(next_song_short.video_url, next_song_short.requested_by)
                except yt_dlp.utils.DownloadError:
                    after_playing(None)
                    return
                self._play_song(client, state, next_song)
            elif state.now_playing is not None:
                asyncio.run_coroutine_threadsafe(client.disconnect(), self.bot.loop)
        client.play(source, after=after_playing)

    async def _queue_song(self, interaction, url) -> discord.embeds.Embed:
        client = interaction.guild.voice_client
        state = self.get_state(interaction.guild)

        # client connected to voice
        if client and client.channel:
            try:
                pl = Playlist(url, interaction.user)
            except (yt_dlp.DownloadError, yt_dlp.utils.DownloadError) as e:
                raise e

            state.playlist.extend(pl.playlist)
            if len(pl.playlist) > 1:
                return pl.get_embed()
            else:
                return pl.playlist[0].get_embed()

        # client not connected to voice
        else:
            if interaction.user.voice is not None and interaction.user.voice.channel is not None:
                channel = interaction.user.voice.channel
                try:
                    pl = Playlist(url, interaction.user)
                except (yt_dlp.DownloadError, yt_dlp.utils.DownloadError) as e:
                    raise e

                client = await channel.connect()
                try:
                    video = Video_Full(pl.playlist[0].video_url, interaction.user)
                except yt_dlp.utils.DownloadError as e:
                    await client.disconnect()
                    raise e

                state.playlist.extend(pl.playlist[1:])
                self._play_song(client, state, video)

                if len(pl.playlist) > 1:
                    return pl.get_embed()
                else:
                    return pl.playlist[0].get_embed()

            else:
                raise NotInVoiceChannelException()

    def _get_error_response(self, error: Exception) -> discord.embeds.Embed:
        msg = error.msg

        if type(error) is NotInVoiceChannelException:
            return discord.Embed(description=msg, color=discord.Color.red())

        if not msg:
            return discord.Embed(description="An unknown error occurred when downloading the video. " +
                                 "No further information is available.",
                                 color=discord.Color.red())

        if "please sign in" in msg:
            return discord.Embed(description="An error occurred when downloading the video. " +
                                             "This may be caused by video age restrictions.",
                                 color=discord.Color.red())

        return discord.Embed(description="An unknown error occurred when downloading the video.\n" + msg,
                             color=discord.Color.red())


    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    async def nowplaying(self, interaction: discord.Interaction):
        """Check the currently playing song"""

        state = self.get_state(interaction.guild)

        if await audio_playing(interaction) and await in_voice_channel(interaction):
            await interaction.response.send_message("", embed=state.now_playing.get_embed())
            message = await interaction.original_response()
            await self._add_reaction_controls(message)

        else:
            await interaction.response.send_message("", embed=discord.Embed(description="Bot is not playing"))

    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    async def queue(self, interaction: discord.Interaction):
        """View queue"""

        state = self.get_state(interaction.guild)
        numbers_per_msg = 15
        for i in range(0, len(state.playlist), numbers_per_msg):
            await interaction.response.send_message(self._queue_text(
                i, len(state.playlist), state.playlist[i:i+numbers_per_msg]))
        if len(state.playlist) == 0:
            await interaction.response.send_message('There is no music in the queue')

    def _queue_text(self, cur, total, queue):
        if len(queue) > 0:
            if cur == 0:
                message = [f"{total} songs in queue:"]
            else:
                message = [""]
            message += [
                f"  {index+1+cur}. **{song.title}** (requested by **{song.requested_by.name}**)"
                for (index, song) in enumerate(queue)
            ]
            return "\n".join(message)
        else:
            return "The queue is empty"

    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    # @commands.has_permissions(administrator=True)
    async def clear(self, interaction: discord.Interaction):
        """Clear queue"""

        state = self.get_state(interaction.guild)
        state.playlist = []
        await interaction.response.send_message("", embed=discord.Embed(description="Queue Cleared"))

    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    # @commands.has_permissions(administrator=True)
    async def move(self, interaction: discord.Interaction, song_index: int, new_index: int):
        """Move a song within the queue"""

        # move song to new location in queue
        state = self.get_state(interaction.guild)
        if 1 <= song_index <= len(state.playlist) and 1 <= new_index:
            song = state.playlist.pop(song_index - 1)
            state.playlist.insert(new_index - 1, song)

            numbers_per_msg = 15
            for i in range(0, len(state.playlist), numbers_per_msg):
                await interaction.response.send_message("", embed=discord.Embed(description=self._queue_text(i,
                                                        len(state.playlist), state.playlist[i:i+numbers_per_msg])))
        else:
            await interaction.response.send_message("",
                                                    embed=discord.Embed(description="Invalid Index"),
                                                    ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    async def remove(self, interaction: discord.Interaction, song_index: int):
        """Remove a song by index"""

        state = self.get_state(interaction.guild)
        if 1 <= song_index <= len(state.playlist):
            state.playlist.pop(song_index - 1)
            numbers_per_msg = 15

            if len(state.playlist) == 0:
                await interaction.response.send_message("", embed=discord.Embed(description="There is no music in the queue"))

            else:
                for i in range(0, len(state.playlist), numbers_per_msg):
                    await interaction.response.send_message("", embed=discord.Embed(description=self._queue_text(i,
                                                            len(state.playlist), state.playlist[i:i+numbers_per_msg])))
        else:
            await interaction.response.send_message("",
                                                    embed=discord.Embed(description="Invalid Index"),
                                                    ephemeral=True)

    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    async def shuffle(self, interaction: discord.Interaction):
        """Shuffle playlist"""

        state = self.get_state(interaction.guild)
        random.shuffle(state.playlist)
        await interaction.response.send_message("", embed=discord.Embed(description="Playlist shuffled"))

    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    async def playskip(self, interaction: discord.Interaction, *, url: str):
        """Skip current song and play requested one"""

        await interaction.response.defer(thinking=True)

        client = interaction.guild.voice_client
        state = self.get_state(interaction.guild)

        # bot not connected
        if not client or not client.channel:
            try:
                response = await self._queue_song(interaction, url)
                await interaction.edit_original_response(embed=response)
            except (yt_dlp.DownloadError, yt_dlp.utils.DownloadError, NotInVoiceChannelException) as e:
                error_response = self._get_error_response(msg=e.msg)
                await interaction.edit_original_response(content="An error occurred.", embed=error_response)
                return

        # standard behaviour
        else:
            state.playlist[:0] = Playlist(url, interaction.user).playlist
            client.stop()

        pl = Playlist(url, interaction.user)

        if len(pl.playlist) > 1:
            await interaction.edit_original_response(content="Playskipping", embed=pl.get_embed())
        else:
            await interaction.edit_original_response(content="Playskipping", embed=pl.playlist[0].get_embed())

        message = await interaction.original_response()
        await self._add_reaction_controls(message)

    @app_commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    async def playtop(self, interaction: discord.Interaction, *, url: str):
        """Add a song to the top of the queue"""

        await interaction.response.defer(thinking=True)

        client = interaction.guild.voice_client
        state = self.get_state(interaction.guild)

        # bot not connected
        if not client or not client.channel:
            try:
                response = await self._queue_song(interaction, url)
                await interaction.edit_original_response(embed=response)
            except (yt_dlp.DownloadError, yt_dlp.utils.DownloadError, NotInVoiceChannelException) as e:
                error_response = self._get_error_response(msg=e.msg)
                await interaction.edit_original_response(content="An error occurred.", embed=error_response)
                return

        # standard behaviour
        else:
            state.playlist[:0] = Playlist(url, interaction.user).playlist

        pl = Playlist(url, interaction.user)

        if len(pl.playlist) > 1:
            await interaction.edit_original_response(content="Added to top of queue", embed=pl.get_embed())
        else:
            await interaction.edit_original_response(content="Added to top of queue", embed=pl.playlist[0].get_embed())

        message = await interaction.original_response()
        await self._add_reaction_controls(message)

    @app_commands.command()
    async def play(self, interaction: discord.Interaction, *, url: str):
        """Play a song"""

        # defer our interaction response
        await interaction.response.defer(thinking=True)

        # early exit if video can't be downloaded
        try:
            response = await self._queue_song(interaction, url)
            await interaction.edit_original_response(embed=response)
        except (yt_dlp.DownloadError, yt_dlp.utils.DownloadError, NotInVoiceChannelException) as e:
            error_response = self._get_error_response(error = e)
            await interaction.edit_original_response(content="An error occurred.", embed=error_response)
            return

        message = await interaction.original_response()
        await self._add_reaction_controls(message)

    async def on_reaction_add(self, reaction, user):
        message = reaction.message

        # ignore reactions by the bot or to non-bot messages
        if user == self.bot.user or message.author != self.bot.user:
            return

        # remove reactions and ignore invalid ones
        await message.remove_reaction(reaction, user)
        if reaction.emoji not in ["⏯", "⏭", "⏮"]:
            return

        # do nothing if not connected
        if not message.guild or not message.guild.voice_client:
            return

        if message.guild and message.guild.voice_client:
            user_in_channel = user.voice and user.voice.channel and user.voice.channel == message.guild.voice_client.channel
            permissions = message.channel.permissions_for(user)
            guild = message.guild
            state = self.get_state(guild)

            if permissions.administrator or (user_in_channel and state.is_requester(user)):
                client = message.guild.voice_client
                if reaction.emoji == "⏯":   # play/pause
                    self._pause_audio(client)
                elif reaction.emoji == "⏭":     # skip track
                    client.stop()
                elif reaction.emoji == "⏮":     # restart track
                    state.playlist.insert(
                        0, state.now_playing
                    )
                    client.stop()

            elif reaction.emoji == "⏭" and settings.settings["musicVoteSkip"] and user_in_channel and message.guild.voice_client and message.guild.voice_client.channel:
                # ensure skip was pressed, vote skip enabled, user in channel, and bot in channel
                voice_channel = message.guild.voice_client.channel
                self._vote_skip(voice_channel, user)

                channel = message.channel
                users_in_channel = len([
                    member for member in voice_channel.members
                    if not member.bot
                ]) # no robots

                required_votes = math.ceil(settings.settings["musicVoteSkipRatio"] * users_in_channel)
                await channel.send(f"{user.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes)")

    async def _add_reaction_controls(self, message):
        # adds a reaction control to the bot
        controls = ["⏮", "⏯", "⏭"]
        for control in controls:
            await message.add_reaction(control)


class GuildState:
    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.skip_votes = set()
        self.now_playing = None

        def is_requester(self, user):
            return self.now_playing.requested_by == user


async def setup(bot):
    await bot.add_cog(Music(bot, settings.settings))
