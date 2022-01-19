from func.firebase_init import db

from disnake.ext import commands
import disnake
import time


class NFTsLink(disnake.ui.View):
    def __init__(self, ids: list[str] | str):
        super().__init__()

        if isinstance(ids, list):
            url = f"https://diskito.eu/NFT?ids={','.join([nft for nft in ids])}"
            self.add_item(disnake.ui.Button(label="Your NFT collection sir", url=url))
        else:
            url = f"https://diskito.eu/NFT?ids={ids}"
            self.add_item(disnake.ui.Button(label="Enjoy!", url=url))


class NFT(commands.Cog):
    def __init__(self, client):
        """NFTs lmao."""
        self.client = client

    @commands.slash_command(name="nft", description="Creates a link to view all of your Diskíto NFT's")
    async def _nft(self, inter: disnake.MessageInteraction):
        user_nfts = db.child("NFT").child("owned").child(inter.author.id).get().val() or None
        if user_nfts is None:
            return await inter.response.send_message("You do not own any NFT's! Go buy some, it's great!!", ephemeral=True)

        # Converting a nested OrderedDict to a list of strings..
        # Respectfully yoinked from https://stackoverflow.com/q/16228248/13186339
        nft_list = list(map(lambda x: x["id"], [*dict(user_nfts).values()]))
        return await inter.response.send_message("Here you go:", view=NFTsLink(nft_list))

    @commands.slash_command(
        name="mint",
        description="Mints a random NFT from a collection of over 100 million custom Diskíto NFTs for 100k shekels"
    )
    async def _mint(self, inter: disnake.MessageInteraction):
        buyer_money = db.child("users").child(inter.author.id).child("money").get().val()
        if buyer_money <= 100_000:
            return await inter.response.send_message("You do not have enough shekels to mint a new NFT!", ephemeral=True)

        minted = db.child("NFT").child("ids").get()

        minted_wo = [i for i in minted.val() if i]
        mint_key = len(minted.val())-len(minted_wo)
        mint_id = minted_wo[0]

        db.child("users").child(inter.author.id).update({"money": int(buyer_money - 100_000)})
        db.child("NFT").child("ids").child(mint_key).remove()
        db.child("NFT").child("owned").child(inter.author.id).update({mint_id: {"boughtAt": time.time(), "id": mint_id}})
        return await inter.response.send_message("Your new NFT:", view=NFTsLink(mint_id))


def setup(client):
    client.add_cog(NFT(client))