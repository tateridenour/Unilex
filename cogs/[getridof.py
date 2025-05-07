from discord.ext import commands
import asyncio
import re

import global_functions as global_func
from datetime import UTC, datetime, timedelta


class GetRidOf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["giveup", "getawayfromme"])
    async def getridof(self, ctx, *, message: str):
        # Getting ID from user input
        article = await global_func.get_article_from_arg(ctx, message)
        if article == None:
            return

        article_id = article[0]
        article_title = article[1]

        # If nobody owns it
        passive_aggressive_denial_message = (
            f"Nobody owns **{article_title}**, not even you."
        )
        article_owner = global_func.clm_cur.execute(
            "SELECT user_id FROM claims WHERE article_id = ?", (article_id,)
        ).fetchone()
        if article_owner == None:
            await ctx.send(passive_aggressive_denial_message)
            return
        article_owner = article_owner[0]
        if article_owner == "NULL":
            await ctx.send(passive_aggressive_denial_message)
            return

        # If somebody else owns it
        if article_owner != ctx.author.id:
            print(ctx.author.id)
            print(article_owner)
            await ctx.send(
                f"{self.bot.get_user(article_owner)} owns **{article_title}**, not you."
            )
            return

        await ctx.send(f"Do you really want to get rid of **{article_title}**?")

        def checkyes(msg):
            msg.content = msg.content.strip("!").lower()
            return (
                msg.author == ctx.author
                and msg.channel == ctx.channel
                and bool(re.match(r"^y+e+s+$", msg.content))
                or msg.content == "y"
                or bool(re.match(r"^n+o+$", msg.content))
                or msg.content == "n"
                # Matches stuff like yeeesssssssss!!!! because I think it's funny
            )

        try:
            msg = await self.bot.wait_for("message", timeout=20.0, check=checkyes)

            content = msg.content.strip("!").lower()
            if re.match(r"^ye+s+$", content) or content == "y":  # Confirm
                await ctx.send(f"Goodbye, **{article_title}**.")

                global_func.clm_cur.execute(
                    """
                    UPDATE claims
                    SET user_id = ?, updated_at = ?
                    WHERE article_id = ?
                """,
                    ("NULL", datetime.now(UTC), article_id),
                )
                global_func.clm_con.commit()

            elif re.match(r"^no+$", content) or content == "n":
                await ctx.send(
                    f"Never mind, **{article_title}**. **{ctx.author}** missed you."
                )
            # Place your action here
        except asyncio.TimeoutError:
            await ctx.send(
                "Cancelled delete request. No confirmation received in time."
            )


async def setup(bot):
    await bot.add_cog(GetRidOf(bot))
