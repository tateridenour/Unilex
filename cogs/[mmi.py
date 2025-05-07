from discord.ext import commands

import global_functions as global_func


class Mmi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Displays all claims owned by a specific user in a navigable list
    @commands.command(aliases=['mymarvelousitems', 'monmi'])
    async def mmi(self, ctx, *, message: str):

        article_id = await global_func.get_article_id_from_arg(ctx, message)
        if article_id == None:
            return

        image_list=global_func.clm_cur.execute("""
            SELECT * FROM claims WHERE user_id=?                            
        """, (ctx.message.author.id,)).fetchall()
        print(ctx.message.author.id)

        embed, view = await global_func.generate_navbuttons_for_image_list(
            self=self,
            article_id=article_id,
            image_list=image_list, 
            channel=ctx.message.channel,
            isRoll=False,
        )

        if embed != None:
            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Mmi(bot))
