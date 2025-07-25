import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Modal, TextInput

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Identifiants
MY_GUILD_ID = 1397890415474245682
OWNER_ID = 1055144899802050580

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Base de données simple (films / séries)
film_database = {
    "ninjago": {
        "description": "Ninjago - série d'animation de fantasy épique avec des héros qui sont des ninjas.",
        "saisons": {
            "Saison 1": "https://www.france.tv/france-3/lego-ninjago/saison-1/235125-la-legende-des-serpents.html",
            "Saison 2": "https://www.france.tv/france-3/lego-ninjago/saison-2/1119711-l-avenement-des-tenebres.html",
            "saison 3": "https://www.france.tv/france-3/lego-ninjago/saison-3/275721-l-ennemi-invisible.html"

        }
    }
}

# Modal
class RechercheModal(Modal, title="Recherche de série ou film"):
    recherche = TextInput(label="Nom du film ou de la série", placeholder="Ex: Ninjago")

    async def on_submit(self, interaction: Interaction):
        query = self.recherche.value.strip().lower()
        if query in film_database:
            data = film_database[query]
            embed = discord.Embed(
                title=query.title(),
                description=data["description"],
                color=discord.Color.blue()
            )

            for saison, lien in data.get("saisons", {}).items():
                embed.add_field(name=saison, value=f"[Regarder ici]({lien})", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                "❌ Ce film ou cette série n’est pas encore dans la base.\n"
                "Tu peux proposer ton idée dans <#1397931094707409027> !",
                ephemeral=True
            )

# View avec bouton
class RechercheView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔍 Rechercher", style=discord.ButtonStyle.primary, custom_id="recherche_btn")
    async def rechercher(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(RechercheModal())

# Événement au lancement
@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    try:
        print("⏳ Synchronisation des slash commandes...")
        synced = await bot.tree.sync(guild=discord.Object(id=MY_GUILD_ID))
        print(f"✅ {len(synced)} commande(s) synchronisée(s)")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation : {e}")

# Commande pour envoyer l'embed avec le bouton
@bot.tree.command(name="envoyer_recherche", description="Envoyer le message de recherche (admin uniquement)")
@app_commands.guilds(discord.Object(id=MY_GUILD_ID))
async def envoyer_recherche(interaction: Interaction):
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("⛔ Tu n'as pas la permission.", ephemeral=True)

    embed = discord.Embed(
        title="🎬 Système de recherche FNC",
        description="Clique sur le bouton ci-dessous pour rechercher un film ou une série.\n"
                    "Si elle est absente, propose-la dans le salon dédié.",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed, view=RechercheView())

# Commande de maintenance
@bot.tree.command(name="maintenance", description="Mode maintenance")
@app_commands.guilds(discord.Object(id=MY_GUILD_ID))
async def maintenance(interaction: Interaction):
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("⛔ Tu n'as pas la permission.", ephemeral=True)

    await interaction.response.send_message("🚧 Le bot est en maintenance. Merci de réessayer plus tard.", ephemeral=True)

bot.run(token)

