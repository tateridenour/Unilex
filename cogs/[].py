import random
from discord.ext import commands

import global_functions as global_func

# # Initializing sqlite3 for articles
# art_path = 'data/articles.db'
# art_con = sqlite3.connect(art_path)
# art_cur = art_con.cursor()

# Getting number of articles
article_count = global_func.art_cur.execute("SELECT COUNT(*) FROM articles").fetchone()[
    0
]


class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="]")
    async def roll(self, ctx):
        article_id = random.randint(1, article_count)
        # article_id = 2

        embed = await global_func.generate_embed_from_article_id(
            self=self, article_id=article_id, channel=ctx.message.channel, isRoll=True
        )
        view = await global_func.generate_forward_and_backward_buttons(
            self=self,
            article_id=article_id,
            channel=ctx.message.channel,
            embed=embed,
            isRoll=True,
        )

        await ctx.message.channel.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Roll(bot))
