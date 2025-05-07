from discord.ext import commands

import global_functions as global_func


class Mmi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Displays all claims owned by a specific user in a navigable list
    @commands.command(aliases=["mymarvelousitems", "monmi"])
    async def mmi(self, ctx):
        claim_list = global_func.clm_cur.execute(
            """
            SELECT * FROM claims WHERE user_id=?                            
        """,
            (ctx.message.author.id,),
        ).fetchall()

        if claim_list == []:
            await ctx.send("You have NOTHING. YOU HAVE NOTHINGGGG!!!")
            return
        claim_list = sorted(claim_list, key=lambda x: x[4])  # Article position

        article_ids = [item[0] for item in claim_list]  # Article ID
        image_idxs = [item[2] for item in claim_list]  # Image ID per article

        image_list = [
            global_func.ArticleImagePair(image_idx=image_idx, article_id=article_id)
            for image_idx, article_id in zip(image_idxs, article_ids)
        ]
        print(image_list)
        embed, view = await global_func.generate_viewer_from_article_data(
            self=self,
            image_list=image_list,
            channel=ctx.message.channel,
            isRoll=False,
        )

        if embed != None:
            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Mmi(bot))
