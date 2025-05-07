import sqlite3

import requests
from discord.ext import commands

import global_functions as global_func

# Initializing sqlite3 for articles
art_path = "data/articles.db"
art_con = sqlite3.connect(art_path)
art_cur = art_con.cursor()


class FixImg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fiximg")
    async def fiximg(self, ctx, *, message: str):
        message = message.split("|")
        if len(message) == 1:  # Only one argument
            message = [message[0], 1]  # Correct first image by default
        if len(message) != 2:
            await ctx.send(f"Command fiximg takes 2 arguments.")
            return

        article = await global_func.get_article_id_from_arg(ctx, str(message[0]))
        if article == None:
            return
        image_id_per_article = int(message[1])

        image_url = art_cur.execute(
            "SELECT image_url FROM article_images WHERE (article_id = ? AND image_id_per_article = ?)",
            (int(article), int(image_id_per_article)),
        ).fetchone()
        if image_url == None:
            await ctx.send(
                f'Couldn\'t find image **{image_id_per_article}** for the article **{message[0]!s}**.'
            )
            return
        image_url = image_url[
            0
        ]  # After to avoid 'NoneType' object is not subscriptable error

        # See if proposed broken URL doesn't display
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        try:
            response = requests.get(image_url, headers=headers)
            if response.status_code != 404:
                await ctx.send(
                    "The image already displays in full size."
                )
                return
        except requests.exceptions.RequestException:
            print("RequestException")
            return

        image_url = image_url.replace("/wikipedia/commons/", "/wikipedia/en/")
        # See if a non-Wikipedia-commons version displays
        try:
            response = requests.get(image_url, headers=headers)
            if response.status_code == 404:
                await ctx.send(
                    f"Non Wikimedia Commons version does not display. Contact olc. Probably."
                )
                return
        except requests.exceptions.RequestException:
            print("RequestException")
            return

        art_cur.execute(
            """
            UPDATE article_images
            SET image_url = ?
            WHERE (article_id = ? AND image_id_per_article = ?)
        """,
            (image_url, int(article), int(image_id_per_article)),
        )
        await ctx.message.add_reaction("✅")
        art_con.commit()


async def setup(bot):
    await bot.add_cog(FixImg(bot))
