from pyrogram.errors import UserNotParticipant, FloodWait
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from FileStream.utils.translation import LANG
from FileStream.utils.database import Database
from FileStream.utils.human_readable import humanbytes
from FileStream.config import Telegram, Server
from FileStream.bot import FileStream
import asyncio
from typing import (
    Union
)
import requests

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)


async def get_invite_link(bot, chat_id: Union[str, int]):
    try:
        invite_link = await bot.create_chat_invite_link(chat_id=chat_id)
        return invite_link
    except FloodWait as e:
        print(f"Sleep of {e.value}s caused by FloodWait ...")
        await asyncio.sleep(e.value)
        return await get_invite_link(bot, chat_id)


async def is_user_joined(bot, message: Message):
    if Telegram.FORCE_SUB_ID and Telegram.FORCE_SUB_ID.startswith("-100"):
        channel_chat_id = int(Telegram.FORCE_SUB_ID)  # When id startswith with -100
    elif Telegram.FORCE_SUB_ID and (not Telegram.FORCE_SUB_ID.startswith("-100")):
        channel_chat_id = Telegram.FORCE_SUB_ID  # When id not startswith -100
    else:
        return 200
    try:
        user = await bot.get_chat_member(chat_id=channel_chat_id, user_id=message.from_user.id)
        if user.status == "BANNED":
            await message.reply_text(
                text=LANG.BAN_TEXT.format(Telegram.OWNER_ID),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False
    except UserNotParticipant:
        invite_link = await get_invite_link(bot, chat_id=channel_chat_id)
        if Telegram.VERIFY_PIC:
            ver = await message.reply_photo(
                photo=Telegram.VERIFY_PIC,
                caption="<i>Jᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ 🔐</i>",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("❆ Jᴏɪɴ Oᴜʀ Cʜᴀɴɴᴇʟ ❆", url=invite_link.invite_link)
                    ]]
                )
            )
        else:
            ver = await message.reply_text(
                text="<i>Jᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ 🔐</i>",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("❆ Jᴏɪɴ Oᴜʀ Cʜᴀɴɴᴇʟ ❆", url=invite_link.invite_link)
                    ]]
                ),
                parse_mode=ParseMode.HTML
            )
        await asyncio.sleep(30)
        try:
            await ver.delete()
            await message.delete()
        except Exception:
            pass
        return False
    except Exception:
        await message.reply_text(
            text=f"<i>Sᴏᴍᴇᴛʜɪɴɢ ᴡʀᴏɴɢ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ᴅᴇᴠᴇʟᴏᴘᴇʀ</i> <b><a href='https://t.me/{Telegram.UPDATES_CHANNEL}'>[ ᴄʟɪᴄᴋ ʜᴇʀᴇ ]</a></b>",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True)
        return False
    return True


# ---------------------[ PRIVATE GEN LINK + CALLBACK ]---------------------#
def shorturl(file_link):
    Short_url = "https://tnshort.net/api?api=86bd6df4bdf3efd9bedeee2ba03c17e33e32978f&url={}".format(
        file_link)
    response = requests.request('GET', Short_url)
    if response.status_code == 200:
        try:
            # Parse the JSON response
            response_data = response.json()
            shortened_url = response_data.get('shortenedUrl', None)
            if shortened_url:

                return shortened_url
            else:
                return file_link
        except Exception as e:
            print(e)
    else:
        return file_link


def remove_otherword(file_name):
    modified_message = file_name.replace("dealadda", "")
    modified_message = modified_message.replace('movieshubmt', '')
    modified_message = modified_message.replace('@movieshubmt', '')
    modified_message = modified_message.replace('𝖬𝖠𝖯𝖮𝗋𝗂𝗀𝗂𝗇𝖺𝗅𝗌', '')
    modified_message = modified_message.replace('@𝖬𝖠𝖯𝖮𝗋𝗂𝗀𝗂𝗇𝖺𝗅𝗌', '')
    modified_message = modified_message.replace('@Cinemaa_boxoffice', '')
    modified_message = modified_message.replace('https://k*', '')
    modified_message = modified_message.replace('https://t.me/*', '')
    modified_message = modified_message.replace('https://mdisk.info/*', '')
    modified_message = modified_message.replace('@TN69Links', '')
    modified_message = modified_message.replace('@*', '')
    modified_message = modified_message + "\n \n"
    modified_message = modified_message + "❤️Jᴏɪɴ : Main Channel @movies_all_HUb and backup channel @PandaSupportgroup"
    return modified_message


async def gen_link(_id):
    file_info = await db.get_file(_id)
    file_name = file_info['file_name']
    file_name_without_channel_name = remove_otherword(file_name)
    file_size = humanbytes(file_info['file_size'])
    mime_type = file_info['mime_type']

    stream_link = f"{Server.URL}watch/{_id}"
    Download_link = f"{Server.URL}dl/{_id}"
    file_link = f"https://t.me/{FileStream.username}?start=file_{_id}"
    Youtube_link = str(Telegram.Youtube_link)

    # file_link_new = shorturl(file_link)
    if Telegram.SHORTERN_ENABLED:
        Download_link = shorturl(Download_link)
        print(Download_link)
        stream_link = shorturl(stream_link)
        print(stream_link)
    else:
        print("ShortUrl disabled")

    if "video" in mime_type:
        stream_text = LANG.STREAM_TEXT.format(file_name_without_channel_name, file_size)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Click to Download", url=file_link)],
                [InlineKeyboardButton("Fast Download link", url=Download_link),
                 InlineKeyboardButton("Stream link", url=stream_link)],
                [InlineKeyboardButton("How to download via Fast link", url=Youtube_link)]
            ]
        )
    else:
        stream_text = LANG.STREAM_TEXT_X.format(file_name_without_channel_name, file_size, stream_link, file_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Fast ᴅᴏᴡɴʟᴏᴀᴅ", url=Download_link)],
                [InlineKeyboardButton("Stream Link", url=stream_link)],
                [InlineKeyboardButton("Click to Download", url=file_link),
                 InlineKeyboardButton("ʀᴇᴠᴏᴋᴇ ғɪʟᴇ", callback_data=f"msgdelpvt_{_id}")],
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")],
                [InlineKeyboardButton("How to download via Fast link", url=Youtube_link)]
            ]
        )
    return reply_markup, stream_text


# ---------------------[ GEN STREAM LINKS FOR CHANNEL ]---------------------#

async def gen_linkx(m: Message, _id, name: list):
    file_info = await db.get_file(_id)
    file_name = file_info['file_name']
    file_name = remove_otherword(file_name)
    mime_type = file_info['mime_type']
    file_size = humanbytes(file_info['file_size'])
    Youtube_link = Telegram.Youtube_link

    page_link = f"{Server.URL}watch/{_id}"
    stream_link = f"{Server.URL}dl/{_id}"
    file_link = f"https://t.me/{FileStream.username}?start=file_{_id}"
    if Telegram.SHORTERN_ENABLED:
        stream_link = shorturl(stream_link)
        print(stream_link)
        stream_link = shorturl(stream_link)
        print(stream_link)
        page_link = shorturl(page_link)
        print(page_link)
    else:
        print("ShortUrl disabled")

    if "video" in mime_type:
        stream_text = LANG.STREAM_TEXT_X.format(file_name, file_size, stream_link, page_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("sᴛʀᴇᴀᴍ", url=page_link), InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ", url=stream_link)],
                [InlineKeyboardButton("How to download via Fast link", url=Youtube_link)]
            ]
        )

    else:
        stream_text = LANG.STREAM_TEXT_X.format(file_name, file_size, stream_link, file_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ", url=stream_link)],
                [InlineKeyboardButton("How to download via Fast link", url=Youtube_link)]
            ]
        )
    return reply_markup, stream_text


# ---------------------[ USER BANNED ]---------------------#

async def is_user_banned(message):
    if await db.is_user_banned(message.from_user.id):
        await message.reply_text(
            text=LANG.BAN_TEXT.format(Telegram.OWNER_ID),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return True
    return False


# ---------------------[ CHANNEL BANNED ]---------------------#

async def is_channel_banned(bot, message):
    if await db.is_user_banned(message.chat.id):
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.id,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"ᴄʜᴀɴɴᴇʟ ɪs ʙᴀɴɴᴇᴅ", callback_data="N/A")]])
        )
        return True
    return False


# ---------------------[ USER AUTH ]---------------------#

async def is_user_authorized(message):
    if hasattr(Telegram, 'AUTH_USERS') and Telegram.AUTH_USERS:
        user_id = message.from_user.id

        if user_id == Telegram.OWNER_ID:
            return True

        if not (user_id in Telegram.AUTH_USERS):
            await message.reply_text(
                text="Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    return True


# ---------------------[ USER EXIST ]---------------------#

async def is_user_exist(bot, message):
    if not bool(await db.get_user(message.from_user.id)):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Telegram.ULOG_CHANNEL,
            f"**#NᴇᴡUsᴇʀ**\n**⬩ ᴜsᴇʀ ɴᴀᴍᴇ :** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**⬩ ᴜsᴇʀ ɪᴅ :** `{message.from_user.id}`"
        )


async def is_channel_exist(bot, message):
    if not bool(await db.get_user(message.chat.id)):
        await db.add_user(message.chat.id)
        members = await bot.get_chat_members_count(message.chat.id)
        await bot.send_message(
            Telegram.ULOG_CHANNEL,
            f"**#NᴇᴡCʜᴀɴɴᴇʟ** \n**⬩ ᴄʜᴀᴛ ɴᴀᴍᴇ :** `{message.chat.title}`\n**⬩ ᴄʜᴀᴛ ɪᴅ :** `{message.chat.id}`\n**⬩ ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs :** `{members}`"
        )


async def verify_user(bot, message):
    if not await is_user_authorized(message):
        return False

    if await is_user_banned(message):
        return False

    await is_user_exist(bot, message)

    if Telegram.FORCE_SUB:
        if not await is_user_joined(bot, message):
            return False

    return True
