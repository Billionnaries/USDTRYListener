import discord
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput

class DiscordBot(discord.Client):
    def __init__(self, guild_id, threshold_callback, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True  # Ensure message content intent is enabled
        super().__init__(intents = intents, *args, **kwargs)
        self.guild_id = guild_id
        self.threshold_callback = threshold_callback
        self.threshold = self.load_threshold_from_file()
        self.tree = app_commands.CommandTree(self)  # Initialize CommandTree

    def load_threshold_from_file(self):
        """
        Load the  current threshold from treshold txt.
        :return:
        """
        try:
            with open('threshold.txt', 'r') as f:
                return float(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0.005

    def save_threshold_to_file(self, new_threshold):
        """
        Save the  current threshold to treshold txt.
        :return:
        """
        with open('threshold.txt', 'w') as f:
            f.write(str(new_threshold))

    async def setup_hook(self):
        """
        Hook setup for creating SLASH COMMANDS
        """
        @self.tree.command(
            name = "resend_button",
            description = "Resend the threshold button",
            guild = discord.Object(id = 909453473043591198)
        )
        async def resend_button(interaction: discord.Interaction):
            await self.setup_threshold_button()
            await interaction.response.send_message("Threshold button has been re-sent.", ephemeral=True)

        guild = discord.Object(id = 909453473043591198)
        await self.tree.sync(guild = guild)
        print(f"Slash commands synced successfully to guild .")

    async def notify_threshold_exceeded(self, message):
        """
        Function to send threshold exceeded message
        :param message:
        :return:
        """
        guild = discord.utils.get(self.guilds, id = 909453473043591198)
        channel = discord.utils.get(guild.text_channels, id=self.guild_id)
        if channel:
            try:
                await channel.send(message)
            except Exception as e:
                print(f"Error sending message: {e}")

    async def on_ready(self):
        """
        On ready function for extra operations comes with bot log in.
        :return: 
        """
        print(f'The bot is in {len(self.guilds)} guild(s).')
        await self.setup_threshold_button()

    async def setup_threshold_button(self):
        """
        Function to configure treshold change button.
        :return: 
        """
        guild = discord.utils.get(self.guilds, id = 909453473043591198)
        channel = discord.utils.get(guild.text_channels, id=self.guild_id)
        change_threshold_button = Button(label="Change Threshold", style=discord.ButtonStyle.primary)
        change_threshold_button.callback = self.change_threshold_prompt
        view = View()
        view.add_item(change_threshold_button)
        try:
            await channel.send("Click the button to change the threshold:", view = view)
        except Exception as e:
            print(f"Error sending button: {e}")

    async def change_threshold_prompt(self, interaction: discord.Interaction):
        modal = ThresholdModal(self.threshold_callback, self, self.threshold)
        await interaction.response.send_modal(modal)

class ThresholdModal(Modal):
    def __init__(self, threshold_callback, bot, current_threshold):
        super().__init__(title = "Set New Threshold")
        self.threshold_callback = threshold_callback
        self.bot = bot
        self.add_item(TextInput(label = "Enter the new threshold (in percentage)",
                                placeholder = f"Current threshold: {current_threshold:.2f}"))

    async def on_submit(self, interaction: discord.Interaction):
        """
        Function to define and implement treshold update operations.
        :param interaction: 
        :return: 
        """
        try:
            new_threshold = float(self.children[0].value)
            self.threshold_callback(new_threshold) 
            self.bot.threshold = new_threshold
            self.bot.save_threshold_to_file(new_threshold)
            await interaction.response.send_message(f"Threshold updated to {new_threshold:.2f}%", ephemeral=True)
            await self.bot.setup_threshold_button()

        except ValueError:
            await interaction.response.send_message("Invalid input. Please enter a numeric value.", ephemeral=True)
