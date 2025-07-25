import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import View, Button, Modal, TextInput

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

MY_GUILD_ID = 1397890415474245682
OWNER_ID = 1055144899802050580
AVIS_CHANNEL_ID = 1398335560979841144

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----- BASE DE DONNÉES -----

film_database = {
    "ninjago": {
        "description": "Ninjago - série d'animation de fantasy épique avec des héros mais ce sont des ninjas.",
        "saisons": {
            "Saison 1": "https://www.france.tv/france-3/lego-ninjago/saison-1/235125-la-legende-des-serpents.html",
            "Saison 2": "https://www.france.tv/france-3/lego-ninjago/saison-2/1119711-l-avenement-des-tenebres.html"
            # Tu peux continuer à ajouter ici
        }
    }
}

# ----- MODALS -----

class RechercheModal(Modal, title="Recherche de série ou film"):
    recherche = TextInput(label="Nom du film ou de la série", placeholder="Ex: Ninjago")

    async def on_submit(self, interaction: Interaction):
        query = self.recherche.value.strip().lower()
        if query in film_database:
            data = film_database[query]
            embed = discord.Embed(title=query.title(), description=data["description"], color=discord.Color.blue())
            for saison, lien in data.get("saisons", {}).items():
                embed.add_field(name=saison, value=f"[Regarder ici]({lien})", inline=False)
            embed.set_image(url="https://i.postimg.cc/mgfDz100/image.png")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                "❌ Ce film ou cette série n’est pas encore dans la base.\nTu peux proposer ton idée dans <#1397931094707409027> !",
                ephemeral=True
            )

class SuggestionModal(Modal, title="Proposer une série ou un film"):
    titre = TextInput(label="Nom", placeholder="Nom du film ou de la série")
    description = TextInput(label="Pourquoi cette suggestion ?", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: Interaction):
        embed = discord.Embed(title="📩 Nouvelle suggestion", color=discord.Color.green())
        embed.add_field(name="Titre", value=self.titre.value, inline=False)
        embed.add_field(name="Raison", value=self.description.value, inline=False)
        embed.set_footer(text=f"Proposé par {interaction.user.display_name}")
        salon = interaction.guild.get_channel(1397931094707409027)
        await salon.send(embed=embed)
        await interaction.response.send_message("✅ Suggestion envoyée avec succès !", ephemeral=True)

class UpdateLinkModal(Modal, title="Demander une mise à jour de lien"):
    titre = TextInput(label="Nom", placeholder="Nom du film ou série concerné")
    saison = TextInput(label="Saison ou épisode concerné")

    async def on_submit(self, interaction: Interaction):
        embed = discord.Embed(title="🔁 Demande de mise à jour de lien", color=discord.Color.orange())
        embed.add_field(name="Titre", value=self.titre.value)
        embed.add_field(name="Saison", value=self.saison.value)
        embed.set_footer(text=f"Signalé par {interaction.user.display_name}")
        salon = interaction.guild.get_channel(1398266579111907368)
        await salon.send(embed=embed)
        await interaction.response.send_message("📨 Signalement envoyé. Merci !", ephemeral=True)

class AvisModal(Modal, title="Donner ton avis"):
    avis = TextInput(label="Ton avis (positif ou négatif)", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: Interaction):
        embed = discord.Embed(title="🗣️ Nouvel avis", description=self.avis.value, color=discord.Color.purple())
        embed.set_footer(text=f"Avis envoyé par {interaction.user.display_name}")
        salon = interaction.guild.get_channel(1398393220123328594)
        await salon.send(embed=embed)
        await interaction.response.send_message("✅ Merci pour ton retour !", ephemeral=True)

# ----- VIEWS -----

class RechercheView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔎 Recherche", style=discord.ButtonStyle.blurple, custom_id="recherche")
    async def recherche_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(RechercheModal())

    @discord.ui.button(label="💡 Suggestion", style=discord.ButtonStyle.green, custom_id="suggestion")
    async def suggestion_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(SuggestionModal())

    @discord.ui.button(label="🛠️ Lien cassé", style=discord.ButtonStyle.red, custom_id="lien_casse")
    async def lien_casse_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(UpdateLinkModal())

    @discord.ui.button(label="📚 Catalogue", style=discord.ButtonStyle.gray, custom_id="catalogue")
    async def catalogue_button(self, interaction: Interaction, button: Button):
        catalogue_embed = discord.Embed(title="🎞 Catalogue complet", color=discord.Color.orange())
        for titre, data in film_database.items():
            saisons = "\n".join(f"- [{s}]({l})" for s, l in data.get("saisons", {}).items())
            catalogue_embed.add_field(name=titre.title(), value=f"{data['description']}\n{saisons}", inline=False)
        await interaction.response.send_message(embed=catalogue_embed, ephemeral=True)

    @discord.ui.button(label="🗣 Donner ton avis", style=discord.ButtonStyle.secondary, custom_id="avis")
    async def avis_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(AvisModal())

# ----- EVENTS -----

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=MY_GUILD_ID))
        print(f"✅ {len(synced)} commande(s) synchronisée(s)")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

# ----- COMMANDES -----

@bot.tree.command(name="envoyer_recherche", description="Envoyer le message de recherche avec boutons")
@app_commands.guilds(discord.Object(id=MY_GUILD_ID))
async def envoyer_recherche(interaction: Interaction):
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("⛔ Tu n'as pas la permission.", ephemeral=True)

    embed = discord.Embed(
        title="**🎬 FCC vous souhaite une bonne séance !**",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="🔎 Comment chercher une série ou un film",
        value="Clique sur le bouton **Recherche** ci-dessous pour trouver ta série ou ton film préféré.",
        inline=False
    )
    embed.add_field(
        name="💡 Comment faire une suggestion",
        value="Utilise le bouton **Suggestion** si tu veux proposer un ajout au catalogue.",
        inline=False
    )
    embed.add_field(
        name="🛠️ Comment signaler un lien cassé",
        value="Clique sur **Lien cassé** pour signaler un lien expiré ou invalide.",
        inline=False
    )
    embed.add_field(
        name="📚 Voir le catalogue",
        value="Appuie sur **Catalogue** pour afficher tout ce qui est dispo.",
        inline=False
    )
    embed.add_field(
        name="🗣 Donner ton avis",
        value="Partage ce que tu penses avec le bouton **Avis**.",
        inline=False
    )
    embed.set_image(url="https://i.postimg.cc/mgfDz100/image.png")

    await interaction.response.send_message(embed=embed, view=RechercheView())

@bot.tree.command(name="maintenance", description="Mode maintenance")
@app_commands.guilds(discord.Object(id=MY_GUILD_ID))
async def maintenance(interaction: Interaction):
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("⛔ Tu n'as pas la permission.", ephemeral=True)

    await interaction.response.send_message("🚧 Le bot est en maintenance. Merci de réessayer plus tard.", ephemeral=True)

# ----- DÉMARRAGE -----

try:
    bot.run(token)
except Exception as e:
    print(f"❌ Erreur au démarrage du bot: {e}")
    input("🔁 Appuie sur Entrée pour fermer...")