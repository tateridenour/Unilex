import sqlite3

import discord
from discord.ui import Button, View

from dataclasses import dataclass

# Initializing sqlite3 for articles
art_path = "data/articles.db"
art_con = sqlite3.connect(art_path)
art_cur = art_con.cursor()

# Initializing sqlite3 for claims
clm_path = "data/claims.db"
clm_con = sqlite3.connect(clm_path)
clm_cur = clm_con.cursor()

# Colors for claimable and unclaimable
color_claimable = 0xCCCCCC
color_unclaimable = discord.Colour.dark_theme()

import hashlib
import colorsys


def make_wikipedia_link(
    article_name,
):  # Formats an article title as a link to that article
    article_name = article_name.replace(" ", "_")
    return f"https://en.wikipedia.org/wiki/{article_name}"


def rgb_to_hex(rgb):
    # Convert an RGB tuple with float values (0.0 to 1.0) to 0xRRGGBB hex format.
    r, g, b = rgb
    r_int = int(round(r * 255))
    g_int = int(round(g * 255))
    b_int = int(round(b * 255))
    return (r_int << 16) + (g_int << 8) + b_int


@dataclass
class ArticleImagePair:
    article_id: int
    image_idx: int


async def generate_embed_from_article_id(
    self,
    channel,
    article_id: int,
    image_idx: int = 1,
    footer_counter: str = "",
    isRoll: bool = False,
):
    article_id = int(article_id)

    article = art_cur.execute(
        "SELECT * FROM articles WHERE article_id = ?", (article_id,)
    ).fetchone()
    # Row format: article_id, title, description, char_count
    if article == None:
        await channel.send(f"Couldn't find article with ID {article_id}")
        return
    article_image_all = art_cur.execute(
        "SELECT * FROM article_images WHERE article_id = ?", (article[0],)
    ).fetchall()
    # Row format: image_id, image_url, caption, article_id
    if article_image_all != []:
        article_image = article_image_all[image_idx - 1]
    else:
        article_image = None

    article_description = article[2]

    article_claimdata = clm_cur.execute(
        "SELECT * FROM claims WHERE article_id = ?", (article_id,)
    ).fetchone()
    # Row format: article_id, user_id, selected_image, is_star, is_tag1, is_tag2, created_at, updated_at
    article_owner = None
    # User ID of the owner, if owner exists
    if article_claimdata:
        article_owner = article_claimdata[1]  # The user ID of the owner

    color = ord(article[1][0].lower()) - 97  # Color is based on first letter of article
    color = colorsys.hsv_to_rgb(color / 25, 1, 0.82)
    color = rgb_to_hex(color)

    print(footer_counter)

    embed = discord.Embed(
        # colour=color_claimable
        # if isRoll and article_owner == None
        # else color_unclaimable,
        colour=color,
        description=article_description
        + f"\n[Article]({make_wikipedia_link(article[1])}) ⋅ {article[0]}",
        # Example: [Description text] ⋅ 12345
        title=article[1],
    )
    if article_owner and article_owner != "NULL":
        embed.add_field(
            name="", value=f"Owned by **{self.bot.get_user(article_owner)}**"
        )

    if article_image:
        if isRoll:  # Smaller image and no footer for mobile viewability on rolls
            embed.set_thumbnail(url=article_image[1])  # Image url
            embed.set_footer(text=footer_counter)  # Example: 1/10

            if "wikipedia/commons/" in article_image[1]:
                embed.set_image(
                    url=article_image[1]
                    .replace("wikipedia/commons/", "wikipedia/en/")
                    .replace("250px", "90px")
                )  # Image url
        else:  # Full-size display of the image
            embed.set_image(url=article_image[1].replace("250px", "360px"))  # Image url
            if (
                article_image[2] != ""
            ):  # Avoiding separator if there's no description (nothing to separate)
                embed.set_footer(text=f"{article_image[2]} ⋅ {footer_counter}")
                # Example: [Image description] ⋅ 1/10
            else:
                embed.set_footer(text=footer_counter)  # Example: 1/10

            if "wikipedia/commons/" in article_image[1]:
                embed.set_thumbnail(
                    url=article_image[1].replace("wikipedia/commons/", "wikipedia/en/")
                )  # Backup for commons images. Use [fiximg
    else:  # Article with no image, only need to set footer
        embed.set_footer(text=footer_counter)  # Example: 1/10

    return embed


async def get_article_from_arg(ctx, message):
    message = message.strip()

    article_id = None
    if message.startswith("id:"):  # Example: []im id:12345
        try:
            message = int(message[3:])
        except ValueError:
            ctx.message.channel.send(f"{message} is not a valid ID.")
            return

        article = art_cur.execute(
            "SELECT * FROM articles WHERE article_id = ?",
            (message,),
        ).fetchone()
        if article == None:
            await ctx.message.channel.send(
                f"Couldn't find an article at ID **{message}**."
            )
            return

        return article
    else:
        article = art_cur.execute(
            "SELECT * FROM articles WHERE UPPER(title) LIKE UPPER(?)",
            (message,),
        ).fetchone()
        if article == None:
            await ctx.message.channel.send(f"Couldn't find the article **{message}**.")
            return

        return article  # After to avoid 'NoneType' object is not subscriptable error


async def get_article_id_from_arg(ctx, message):
    article = await get_article_from_arg(ctx, message)
    if article != None:
        return article[0]


async def get_article_title_from_arg(ctx, message):
    article = await get_article_from_arg(ctx, message)
    if article != None:
        return article[1]


async def generate_viewer_from_article_data(
    self, image_list, channel, isRoll: bool, article_id=1, idx: int = 0
):
    # No article images
    # article_id argument is optional for this purpose; it isn't used otherwise
    if image_list == []:
        embed = await generate_embed_from_article_id(
            self=self, article_id=article_id, channel=channel, isRoll=isRoll
        )
        return embed, None

    # Buttons
    button_left = Button(label="<", style=discord.ButtonStyle.grey)
    button_right = Button(label=">", style=discord.ButtonStyle.grey)

    def button_make_callback(
        isLeft: bool, isRoll: bool = False
    ):  # Nested to allow for both left and right with one function
        nonlocal idx

        async def callback(interaction):
            nonlocal idx

            image_count = len(image_list)

            if isLeft:
                idx -= 1
                if (
                    idx == -1
                ):  # If going back at first image, loop back to the last image
                    idx = image_count - 1
            else:
                idx += 1
                if (
                    idx == image_count
                ):  # If going forwards at the last image, loop back to the first image
                    idx = 0

            if (
                "fields" in interaction.message.embeds[0].to_dict()
            ):  # If the article has already been claimed, it will have a field saying so
                isRoll = False

            embed = await generate_embed_from_article_id(
                self=self,
                article_id=image_list[idx].article_id,
                image_idx=image_list[idx].image_idx,
                channel=channel,
                isRoll=isRoll,
                footer_counter=f"{idx + 1}/{len(image_list)}",
            )
            await interaction.response.edit_message(embed=embed)

        return callback

    button_left.callback = button_make_callback(isLeft=True, isRoll=isRoll)
    button_right.callback = button_make_callback(isLeft=False, isRoll=isRoll)

    view = View()
    view.add_item(button_left)
    view.add_item(button_right)

    embed = await generate_embed_from_article_id(
        self=self,
        article_id=image_list[idx].article_id,
        image_idx=image_list[idx].image_idx,
        footer_counter=f"{idx + 1}/{len(image_list)}",
        channel=channel,
        isRoll=isRoll,
    )

    return embed, view
