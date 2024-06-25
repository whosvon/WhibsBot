import discord
from discord.ext import commands
from discord.ui import Button, View
import aiohttp
import os
import sys

TOKEN = '0'  # Replace with your bot token
IMAGE_URL = 'https://miro.medium.com/v2/resize:fit:1400/1*g9ee7RUD831R9n6Km5Jizg.gif'
VOICE_PANEL_CHANNEL_ID = 1255275729919283251  # Replace with your channel ID
VERIFY_PANEL_CHANNEL_ID = 1206091007591063561  # Replace with your verify panel channel ID
VERIFY_ROLE_ID = 1255282250778546216  # Replace with your role ID
RULES_CHANNEL_ID = 123456789012345678  # Replace with your rules channel ID

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.messages = True
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable member intent

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
        try:
            await before.channel.delete()
        except discord.errors.NotFound:
            print(f"Channel {before.channel.id} not found for deletion.")
        except Exception as e:
            print(f"Error deleting channel {before.channel.id}: {e}")

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

    # Purge the specified voice panel channel and resend the voice panel
    await purge_and_send_panel(VOICE_PANEL_CHANNEL_ID, send_voice_panel)

    # Purge the specified verify panel channel and resend the verify panel
    await purge_and_send_panel(VERIFY_PANEL_CHANNEL_ID, send_verify_panel)

    # Update bot's status to show total members
    await update_status_with_total_members()

async def purge_and_send_panel(channel_id, send_panel_function):
    channel = bot.get_channel(channel_id)
    if channel:
        try:
            await channel.purge()
            await send_panel_function(channel)
            print(f'Purged and resent panel in channel {channel_id}.')
        except Exception as e:
            print(f'Error purging and sending panel in channel {channel_id}: {e}')
    else:
        print(f'Channel {channel_id} not found.')

async def send_voice_panel(channel):
    embed = discord.Embed(title="Create A Voice Channel!", description="Click the button below to create a voice channel", color=discord.Color.green())
    view = VoiceChannelView()
    await channel.send(embed=embed, view=view)

async def send_verify_panel(channel):
    embed = discord.Embed(
        title="Verification",
        description=(
            "Hey everyone! Welcome to CypHer's Basement, your new hangout spot for all things gaming, tech, and beyond. "
            "Whether you're here to chill, game, or dive into discussions, we're thrilled to have you join our community. "
            f"Please visit <#{1206091007880462367}> after verification."
        ),
        color=discord.Color.green()
    )
    view = VerifyRoleView()
    await channel.send(embed=embed, view=view)

async def update_status_with_total_members():
    # Calculate total members in all guilds
    total_members = sum([guild.member_count for guild in bot.guilds])
    game = discord.Game(name=f"Total Members: {total_members}")
    await bot.change_presence(activity=game)

    print(f'Bot status updated with total members: {total_members}')

@bot.command(name='reload')
@commands.is_owner()
async def reload(ctx):
    await ctx.send("Reloading bot...")
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send(f"Error: {error.original}")

@bot.event
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.errors.CommandInvokeError):
        await interaction.response.send_message(f"Error: {error.original}", ephemeral=True)

bot.run(TOKEN)