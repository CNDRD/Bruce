import disnake
from disnake.ext import commands


class MessageCommands(commands.Cog):
    def __init__(self, client):
        """Message commands."""
        self.client = client
        self.pins_channel_id = 893274760463659029

    @commands.message_command(name="Pin this message")
    async def pin(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        # No repins under my watch
        if inter.channel_id == self.pins_channel_id:
            return await inter.response.send_message("Pinning a message in the pins channel. You must be a very special snowflake..", ephemeral=True)

        # Message doesn't have to have attachments
        if not inter.target.attachments:
            return await inter.response.send_message("Only pin the funni images / videos / gifs", ephemeral=True)

        # Create our View and add the profile link button
        # prettier than using mentions imo
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label=str(inter.target.author), url=f"discord://-/users/{inter.target.author.id}"))

        # Create the message by appending all the links together
        msg = '\n'.join([attachment.url for attachment in inter.target.attachments])

        await self.client.get_channel(self.pins_channel_id).send(msg, view=view)
        await inter.response.send_message("Successfully pinned that message!", ephemeral=True)


def setup(client):
    client.add_cog(MessageCommands(client))
