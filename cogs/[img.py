from discord.ext import commands

import global_functions as global_func


class Img(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Displays all images from a specific article in a navigable list
    @commands.command(aliases=["im", "img", "giveme", "theycallmethe"])
    async def images(self, ctx, *, message: str):
        article_id = await global_func.get_article_id_from_arg(ctx, message)
        if article_id == None:
            return

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
            isRoll=False,
        )

        if embed != None:
            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Img(bot))
