import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import os
import sys
import aiohttp

TOKEN = 'TOKENHERE'
IMAGE_URL = 'url to bot profile pic'
VOICE_PANEL_CHANNEL_ID = 1255275729919283251  # Replace with your channel ID

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.messages = True
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix='!', intents=intents)

class VoiceChannelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.channel_name = None

    @discord.ui.button(label='Create Here', style=discord.ButtonStyle.green)
    async def create_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Please type the name of the voice channel:", ephemeral=True)
        msg = await bot.wait_for('message', check=lambda m: m.author == interaction.user and m.channel == interaction.channel)
        self.channel_name = msg.content
        await msg.delete()  # Delete the user's message after capturing the channel name
        category = interaction.channel.category
        voice_channel = await interaction.guild.create_voice_channel(name=self.channel_name, category=category)
        await interaction.followup.send(f"Voice channel '{self.channel_name}' created!", ephemeral=True)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel and len(before.channel.members) == 0:
        await before.channel.delete()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}!')

    # Fetch and set the bot's profile picture
    async with aiohttp.ClientSession() as session:
        async with session.get(IMAGE_URL) as response:
            if response.status == 200:
                image_bytes = await response.read()
                await bot.user.edit(avatar=image_bytes)
                print('Bot profile picture updated!')
            else:
                print('Failed to fetch image.')

    # Purge the specified channel and resend the voice panel
    channel = bot.get_channel(VOICE_PANEL_CHANNEL_ID)
    if channel:
        await channel.purge()
        await send_voice_panel(channel)

async def send_voice_panel(channel):
    embed = discord.Embed(title="Create A Voice Channel!", description="Click the button below to create a voice channel", color=discord.Color.green())
    view = VoiceChannelView()
    await channel.send(embed=embed, view=view)

@bot.tree.command(name="voicepanel")
async def voicepanel(interaction: discord.Interaction):
    embed = discord.Embed(title="Create A Voice Channel!", description="Click the button below to create a voice channel", color=discord.Color.green())
    view = VoiceChannelView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="help")
async def help_command(interaction: discord.Interaction):
    commands_list = "/voicepanel - Create a voice channel\n/reload - Reload the bot"
    await interaction.response.send_message(commands_list)

@bot.command(name='reload')
@commands.is_owner()
async def reload(ctx):
    await ctx.send("Reloading bot...")
    os.execv(sys.executable, ['python'] + sys.argv)

bot.run(TOKEN)