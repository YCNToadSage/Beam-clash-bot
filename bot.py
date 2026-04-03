import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import asyncio

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "characters.json"

# Load characters
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        characters = json.load(f)
else:
    characters = {}

# --- Stat Values ---
RESERVES = ["Low", "Standard", "High", "Exceptional", "Vast Exceptional", "Insurmountable"]
OUTPUT = ["Minimal", "Moderate", "High", "Immense", "Cataclysmic", "Catastrophic"]
MANIPULATION = ["Unrefined", "Basic", "Refined", "Advanced", "Expert", "Masterful", "Absolute"]
SPEED = ["<1x", "1x", "2x", ">=3x"]

# Helper: save characters
def save_characters():
    with open(DATA_FILE, "w") as f:
        json.dump(characters, f, indent=4)

# --- Add Stats Command ---
@bot.command()
async def addstats(ctx):
    """Add character stats via interactive buttons."""
    await ctx.send("Please type your **Character Name**:")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        char_name_msg = await bot.wait_for("message", check=check, timeout=60)
        char_name = char_name_msg.content.strip()

        await ctx.send("Now type your **Curse Technique Name**:")
        ct_msg = await bot.wait_for("message", check=check, timeout=60)
        curse_tech = ct_msg.content.strip()
    except asyncio.TimeoutError:
        await ctx.send("Timed out. Please try again.")
        return

    embed = discord.Embed(
        title="Select your stats",
        description="Click the buttons for each stat category, then **Confirm**."
    )
    embed.add_field(name="Character", value=char_name, inline=True)
    embed.add_field(name="Curse Technique", value=curse_tech, inline=True)
    msg = await ctx.send(embed=embed)

    user_selection = {
        "Character": char_name,
        "Curse Technique": curse_tech,
        "Reserves": 0,
        "Output": 0,
        "Manipulation": 0,
        "Speed": 0
    }

    # --- Button View ---
    class StatView(View):
        def __init__(self):
            super().__init__(timeout=None)
            for i, val in enumerate(RESERVES):
                self.add_item(Button(label=val, style=discord.ButtonStyle.primary, custom_id=f"reserves_{i}"))
            for i, val in enumerate(OUTPUT):
                self.add_item(Button(label=val, style=discord.ButtonStyle.success, custom_id=f"output_{i}"))
            for i, val in enumerate(MANIPULATION):
                self.add_item(Button(label=val, style=discord.ButtonStyle.secondary, custom_id=f"manip_{i}"))
            for i, val in enumerate(SPEED):
                self.add_item(Button(label=val, style=discord.ButtonStyle.danger, custom_id=f"speed_{i}"))
            self.add_item(Button(label="Confirm", style=discord.ButtonStyle.blurple, custom_id="confirm"))

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user == ctx.author

    view = StatView()

    async def button_callback(interaction: discord.Interaction):
        cid = interaction.data['custom_id']
        if cid.startswith("reserves_"):
            idx = int(cid.split("_")[1])
            user_selection["Reserves"] = idx
        elif cid.startswith("output_"):
            idx = int(cid.split("_")[1])
            user_selection["Output"] = idx
        elif cid.startswith("manip_"):
            idx = int(cid.split("_")[1])
            user_selection["Manipulation"] = idx
        elif cid.startswith("speed_"):
            idx = int(cid.split("_")[1])
            user_selection["Speed"] = idx
        elif cid == "confirm":
            characters[str(ctx.author.id)] = user_selection
            save_characters()
            await interaction.response.send_message(f"Character stats saved! ✅\n{user_selection}", ephemeral=True)
            view.stop()
            return
        await interaction.response.defer()

    for child in view.children:
        if isinstance(child, Button):
            child.callback = button_callback

    await msg.edit(view=view)

# --- Beam Clash Command with Cooldown and Single Embed ---
currently_clashing = False

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)  # 60 seconds per user
async def beam(ctx, target: discord.Member):
    """Initiate a beam clash between two characters."""
    global currently_clashing
    if currently_clashing:
        await ctx.send("⚡ A beam clash is already in progress. Please wait!")
        return

    # Optional: Restrict channel (uncomment if desired)
    # if ctx.channel.name != "beam-arena":
    #     await ctx.send("This command can only be used in #beam-arena!")
    #     return

    user1 = characters.get(str(ctx.author.id))
    user2 = characters.get(str(target.id))

    if not user1 or not user2:
        await ctx.send("Both participants must have added their stats using !addstats")
        return

    currently_clashing = True
    try:
        # Pre-clash embed
        pre_embed = discord.Embed(
            title="💥 Beam Clash Initiated 💥",
            description=f"{ctx.author.display_name} vs {target.display_name}\nLet's use every last drop!..."
        )
        pre_embed.add_field(name=ctx.author.display_name, value=f"{user1['Character']} | {user1['Curse Technique']}", inline=True)
        pre_embed.add_field(name=target.display_name, value=f"{user2['Character']} | {user2['Curse Technique']}", inline=True)
        msg = await ctx.send(embed=pre_embed)

 # Send GIF immediately after
        gif_url = "https://tenor.com/dLuL49zM8jk.gif"
        await ctx.send(gif_url)
        # --- Beam animation in single embed ---
        total_steps = 10
        for i in range(1, total_steps + 1):
            bar1 = "🔵" * (i + user1["Reserves"])
            bar2 = "🔴" * (i + user2["Reserves"])
            anim_embed = discord.Embed(
                title="💥 Beam Clash In Progress 💥",
                description=f"{ctx.author.display_name} vs {target.display_name}\nLet's use every last drop!"
            )
            anim_embed.add_field(name=ctx.author.display_name, value=bar1, inline=True)
            anim_embed.add_field(name=target.display_name, value=bar2, inline=True)
            await msg.edit(embed=anim_embed)
            await asyncio.sleep(1.2)

        # --- Scoring ---
        def score(char):
            return char["Reserves"]*3 + char["Output"]*4 + char["Manipulation"]*2 + char["Speed"]*1

        score1 = score(user1)
        score2 = score(user2)

        winner = ctx.author if score1 >= score2 else target
        loser = target if winner == ctx.author else ctx.author

        # --- Final Outcome ---
        final_embed = discord.Embed(
            title="💥 Beam Clash Result 💥",
            description=f"{ctx.author.display_name} vs {target.display_name}",
            color=0xFF4500
        )
        final_embed.add_field(name=f"{ctx.author.display_name}", value=f"Score: {score1}", inline=True)
        final_embed.add_field(name=f"{target.display_name}", value=f"Score: {score2}", inline=True)
        final_embed.add_field(name="Winner", value=winner.mention, inline=False)
        final_embed.add_field(name="Loser", value=loser.mention, inline=False)
        await msg.edit(embed=final_embed)

    finally:
        currently_clashing = False

# --- Cooldown Error Handler ---
@beam.error
async def beam_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"🕒 Please wait {error.retry_after:.1f} seconds before using this command again.")

# --- Run Bot ---
bot.run("YOUR-DISCORD-BOT-TOKEN")
