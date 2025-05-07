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

        image_count = len(
            global_func.art_cur.execute(
                """
            SELECT * FROM article_images WHERE article_id=?                            
        """,
                (article_id,),
            ).fetchall()
        )
        image_list = [
            global_func.ArticleImagePair(image_idx=i, article_id=article_id)
            for i in range(1, image_count + 1)
        ]

        embed, view = await global_func.generate_viewer_from_article_data(
            self=self,
            article_id=article_id,
            image_list=image_list,
            channel=ctx.message.channel,
            isRoll=True,
        )

        await ctx.message.channel.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Roll(bot))
