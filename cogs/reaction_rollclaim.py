import sqlite3
from datetime import UTC, datetime, timedelta

import discord
from discord.ext import commands
from discord.ui import Button, View

import global_functions as global_func

# Initializing sqlite3 for claims
clm_path = "data/claims.db"
clm_con = sqlite3.connect(clm_path)
clm_cur = clm_con.cursor()

# Getting number of articles
article_count = global_func.art_cur.execute("SELECT COUNT(*) FROM articles").fetchone()[
    0
]


class ClaimRollOnReaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):  # Claiming a roll
        # Get message that was reacted to
        message = await self.bot.get_channel(payload.channel_id).fetch_message(
            payload.message_id
        )
        if message.author.id != 1368289651064045679:  # Must be the bot's user ID
            return
        if message.embeds == []:  # Must have an embed
            return

        try:
            time_since_message = datetime.now(UTC) - message.created_at
            if time_since_message < timedelta(seconds=120):  # Successful claim
                embed = message.embeds[0].to_dict()  # Gets embed from message
                if (
                    "fields" in embed
                ):  # If the article has already been claimed, it will have a field saying so
                    return
                # if embed['color'] == 3224376:  # 0xcccccc. Need to change this if color is changed
                #     return

                article_id = int(
                    embed["description"].split(" ")[-1]
                )  # The end of the description is the ID
                article_claimdata = clm_cur.execute(
                    "SELECT * FROM claims WHERE article_id = ?", (article_id,)
                ).fetchone()
                if article_claimdata == None:  # Makes new item in claims table
                    clm_cur.execute(
                        """
                        INSERT INTO claims
                            (article_id,
                            user_id,
                            selected_image,
                            is_star,
                            is_tag1,
                            is_tag2,
                            created_at,
                            updated_at
                        ) VALUES (?, ?, 1, 0, 0, 0, ?, NULL)
                    """,
                        (article_id, payload.member.id, datetime.now(UTC)),
                    )
                else:  # Updates existing item in claims table
                    clm_cur.execute(
                        """
                        UPDATE claims
                        SET user_id = ?, updated_at = ?
                        WHERE article_id = ?
                    """,
                        (payload.member.id, datetime.now(UTC), article_id),
                    )
                clm_con.commit()

                # Generate embed and send it
                await message.edit(
                    embed=await global_func.generate_embed_from_article_id(
                        self=self,
                        article_id=article_id,
                        channel=message.channel,
                        isRoll=False,
                    )
                )
                # Claim message
                await message.channel.send(self.bot.get_user(payload.member.id))

            return message.created_at

        except discord.NotFound:
            return "Message not found"

        except discord.HTTPException:
            return "An error occurred while retrieving the message"


async def setup(bot):
    await bot.add_cog(ClaimRollOnReaction(bot))
