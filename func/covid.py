import requests
import datetime
import disnake
import os

from dotenv import load_dotenv
load_dotenv()

MZCR_API_KEY = os.getenv('MZCR_API_KEY')


def _get_nakazeni_reinfekce_data() -> dict[str: str | int] | dict[str: int]:
    url = "https://onemocneni-aktualne.mzcr.cz/api/v3/nakazeni-reinfekce"
    params = {
        "apiToken": MZCR_API_KEY,
        "itemsPerPage": 1,
        "datum[after]": (datetime.datetime.utcnow() - datetime.timedelta(days=1.2)).isoformat()
    }
    resp = requests.get(url, params=params, headers={"Content-Type": "application/json"})

    if resp.status_code != 200:
        return {"err": resp.status_code}
    else:
        return resp.json()["hydra:member"][0]


def get_nakazeni_reinfekce_embed() -> disnake.Embed:
    data = _get_nakazeni_reinfekce_data()

    if (err_c := data.get("err", None)) is not None:
        return disnake.Embed(title="Error", description=err_c, color=0xd31145)

    datum = f'{data["datum"].split("-")[2]}.{data["datum"].split("-")[1]}. {data["datum"].split("-")[0]}'
    celkem_nakazenych = data["nove_pripady"] + data["nove_reinfekce"]
    nove_pripady_ockovani = data["pripady_ockovani_neprodelali"] + data["pripady_ockovani_prodelali"]
    nove_pripady_neockovani = data["pripady_neockovani_neprodelali"] + data["pripady_neockovani_prodelali"]

    embed = disnake.Embed(title=f"COVID - 19 data", description=datum, color=0x280a59)
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/8/82/SARS-CoV-2_without_background.png")
    embed.set_footer(text=f"id: {data['id']}")

    embed.add_field(name="Celkem nakažených", value=f"{celkem_nakazenych:,}".replace(",", " "), inline=True)
    embed.add_field(name="Nové případy", value=f"{data['nove_pripady']:,}".replace(",", " "), inline=True)
    embed.add_field(name="Reinfekce", value=f"{data['nove_reinfekce']:,}".replace(",", " "), inline=True)

    embed.add_field(name="Případy očkovaní", value=f"{nove_pripady_ockovani:,}".replace(",", " "), inline=True)
    embed.add_field(name="Případy NEočkovaní", value=f"{nove_pripady_neockovani:,}".replace(",", " "), inline=True)
    embed.add_field(name="\u200B", value="\u200B")

    embed.add_field(name="Hospitalizovaní", value=f"{data['hospitalizace_vcetne_reinfekce']:,}".replace(",", " "), inline=True)
    embed.add_field(name="JIP", value=f"{data['jip_vcetne_reinfekce']:,}".replace(",", " "), inline=True)
    embed.add_field(name="\u200B", value="\u200B")

    embed.add_field(name="More data", value="[Click here for more data](https://onemocneni-aktualne.mzcr.cz/covid-19 'mzcr.cz')", inline=False)

    return embed
