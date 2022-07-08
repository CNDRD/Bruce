from func.firebase_init import db

from disnake.ext import commands
import disnake
import time


class NFTsLink(disnake.ui.View):
    def __init__(self, uid: int):
        super().__init__()

        self.add_item(disnake.ui.Button(label="Your NFT collection sir", url=f"https://diskito.eu/nft?id={uid}"))


class NFT(commands.Cog):
    def __init__(self, client):
        """NFTs lmao."""
        self.client = client

    @commands.slash_command(
        name="nft",
        description="Creates a link to view all of your Diskíto NFT's"
    )
    async def _nft(self, inter: disnake.CommandInteraction):
        user_nfts = db.child("NFT").child("owned").child(inter.author.id).get().val() or None
        if user_nfts is None:
            return await inter.response.send_message("You do not own any NFT's! Go buy some, it's great!!", ephemeral=True)

        return await inter.response.send_message("Here you go:", view=NFTsLink(inter.author.id))

    @commands.slash_command(
        name="mint",
        description="Mints a random NFT from a collection of over 100 million custom Diskíto NFTs for ₪10k"
    )
    async def _mint(self, inter: disnake.CommandInteraction):
        buyer_money = db.child("users").child(inter.author.id).child("money").get().val()
        if buyer_money <= 10_000:
            return await inter.response.send_message("You do not have enough shekels to mint a new NFT!", ephemeral=True)

        minted = db.child("NFT").child("ids").get()

        minted_wo = [i for i in minted.val() if i]
        mint_key = len(minted.val())-len(minted_wo)
        mint_id = minted_wo[0]

        db.child("users").child(inter.author.id).update({"money": int(buyer_money - 10_000)})
        db.child("NFT").child("ids").child(mint_key).remove()
        db.child("NFT").child("owned").child(inter.author.id).update({mint_id: {"boughtAt": time.time(), "id": mint_id}})
        return await inter.response.send_message("Your new NFT:", view=NFTsLink(inter.author.id))


def setup(client):
    client.add_cog(NFT(client))
