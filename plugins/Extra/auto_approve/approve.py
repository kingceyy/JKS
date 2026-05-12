
import os, string, logging, random, asyncio, time, datetime, re, sys, json, base64
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from database.ia_filterdb import get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db
from database.join_reqs import JoinReqs
from info import *
from utils import get_settings, pub_is_subscribed, get_size, is_subscribed, save_group_settings, temp, get_seconds
from database.connections_mdb import active_connection
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
logger = logging.getLogger(__name__)

BATCH_FILES = {}
join_db = JoinReqs

@Client.on_chat_join_request((filters.group | filters.channel))
async def auto_approve(client, message: ChatJoinRequest):
    if AUTO_APPROVE_MODE == True:
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
        if message.chat.id == AUTH_CHANNEL:
            return 
        chat = message.chat 
        user = message.from_user  
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        text = f"<b>hEllo {message.from_user.mention} 👋,\n\nyour rEquEst to join {message.chat.title} is ApprovED.\n\npowErED By - {CHNL_LNK}</b>"
        await client.send_message(chat_id=user.id, text=text)
         
    if REQUEST_TO_JOIN_MODE == False:
        return 
    if message.chat.id != AUTH_CHANNEL:
        return 
    if not join_db().isActive():
        return
    ap_user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    date = message.date
    await join_db().add_user(user_id=ap_user_id, first_name=first_name, username=username, date=date)
    if TRY_AGAIN_BTN == True:
        return 
    data = await db.get_msg_command(ap_user_id)
        
    if data.split("-", 1)[0] == "VJ":
        user_id = int(data.split("-", 1)[1])
        buttons = [[
            InlineKeyboardButton('Aide 📖', callback_data='help'),
            InlineKeyboardButton('A propos ℹ️', callback_data='about')
        ],[
            InlineKeyboardButton('Rejoindre le groupe 👥', url=GRP_LNK),
            InlineKeyboardButton('Canal de mise a jour 📢', url=CHNL_LNK)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
            
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
        
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("<b>Veuillez patienter...</b>")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs

        filesarr = []
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except:
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                if STREAM_MODE == True:
                    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=msg.get("file_id"))
                    fileName = {quote_plus(get_name(log_msg))}
                    stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                    download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

                if STREAM_MODE == True:
                    button = [[
                        InlineKeyboardButton("• DownloAD •", url=download),
                        InlineKeyboardButton('• Regarder •', url=stream)
                    ],[
                        InlineKeyboardButton("• Regarder in wEB App •", web_app=WebAppInfo(url=stream))
                    ]]
                    reply_markup = InlineKeyboardMarkup(button)
                else:
                    reply_markup = None
                    
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=reply_markup
                )
                filesarr.append(msg)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(button)
                )
                filesarr.append(msg)
            except:
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        k = await client.send_message(chat_id = message.from_user.id, text=f"<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nce message sera supprime dans <b><u>10 min</u> 🫥 <i></b>(pour des raisons de droits d\'auteur)</i>.\n\n<b><i>veuillez transmettre ce message a vos messages sauvegardes ou un chat prive.</i></b></blockquote>")
        await asyncio.sleep(600)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>✅ Votre message a ete supprime avec succes</b>")  
        return
        
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("<b>Veuillez patienter...</b>")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        filesarr = []
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                file_type = msg.media
                file = getattr(msg, file_type.value)
                size = get_size(int(file.file_size))
                file_name = getattr(media, 'file_name', '')
                f_caption = getattr(msg, 'caption', file_name)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=file_name, file_size='' if size is None else size, file_caption=f_caption)
                    except:
                        f_caption = getattr(msg, 'caption', '')
                file_id = file.file_id
                if STREAM_MODE == True:
                    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=file_id)
                    fileName = {quote_plus(get_name(log_msg))}
                    stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                    download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
 
                if STREAM_MODE == True:
                    button = [[
                        InlineKeyboardButton("• DownloAD •", url=download),
                        InlineKeyboardButton('• Regarder •', url=stream)
                    ],[
                        InlineKeyboardButton("• Regarder in wEB App •", web_app=WebAppInfo(url=stream))
                    ]]
                    reply_markup = InlineKeyboardMarkup(button)
                else:
                    reply_markup = None
                try:
                    p = await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False, reply_markup=reply_markup)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    p = await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False, reply_markup=reply_markup)
                except:
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    p = await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    p = await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except:
                    continue
            filesarr.append(p)
            await asyncio.sleep(1)
        await sts.delete()
        k = await client.send_message(chat_id = message.from_user.id, text=f"<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nce message sera supprime dans <b><u>10 min</u> 🫥 <i></b>(pour des raisons de droits d\'auteur)</i>.\n\n<b><i>veuillez transmettre ce message a vos messages sauvegardes ou un chat prive.</i></b></blockquote>")
        await asyncio.sleep(600)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>✅ Votre message a ete supprime avec succes</b>")
        return

    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(text="<b>invAliD link or ExpirED link</b>", protect_content=True)
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            text = "<b>hEy {} 👋,\n\nyou hAvE ComplEtED thE vEriFiCAtion...\n\nnow you hAvE unlimitED ACCEss till toDAy now Enjoy\n\n</b>"
            await message.reply_text(text=text.format(message.from_user.mention), protect_content=True)
        else:
            return await message.reply_text(text="<b>invAliD link or ExpirED link</b>", protect_content=True)
            
    if data.startswith("sendfiles"):
        chat_id = int("-" + file_id.split("-")[1])
        userid = message.from_user.id if message.from_user else None
        settings = await get_settings(chat_id)
        pre = 'allfilesp' if settings['file_secure'] else 'allfiles'
        g = f"https://telegram.me/{temp.U_NAME}?start={pre}_{file_id}"
        btn = [[
            InlineKeyboardButton('Telecharger maintenant', url=g)
        ]]
        text = "<b>✅ your filE rEADy CliCk on Telecharger maintenant Button thEn opEn link to gEt filE\n\n</b>"
        k = await client.send_message(chat_id=message.from_user.id, text=text, reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(300)
        await k.edit("<b>✅ Votre message a ete supprime avec succes</b>")
        return

    elif data.startswith("short"):
        user = message.from_user.id
        chat_id = temp.SHORT.get(user)
        settings = await get_settings(chat_id)
        pre = 'filep' if settings['file_secure'] else 'file'
        g = f"https://telegram.me/{temp.U_NAME}?start={pre}_{file_id}"
        btn = [[
            InlineKeyboardButton('Telecharger maintenant', url=g)
        ]]
        text = "<b>✅ your filE rEADy CliCk on Telecharger maintenant Button thEn opEn link to gEt filE\n\n</b>"
        k = await client.send_message(chat_id=user, text=text, reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(1200)
        await k.edit("<b>✅ Votre message a ete supprime avec succes</b>")
        return
        
    elif data.startswith("all"):
        files = temp.GETALL.get(file_id)
        if not files:
            return await message.reply('<b><i>Ce fichier n\'existe pas.</b></i>')
        filesarr = []
        for file in files:
            file_id = file["file_id"]
            files1 = await get_file_details(file_id)
            title = files1["file_name"]
            size=get_size(files1["file_size"])
            f_caption=files1["caption"]
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except:
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"@VJ_Bots {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1['file_name'].split()))}"
            if STREAM_MODE == True:
                button = [[InlineKeyboardButton('Streaming et telechargement', callback_data=f'generate_stream_link:{file_id}')]]
                reply_markup=InlineKeyboardMarkup(button)
            else:
                reply_markup = None
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if pre == 'allfilesp' else False,
                reply_markup=reply_markup
            )
            filesarr.append(msg)
        k = await client.send_message(chat_id = message.from_user.id, text=f"<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nce message sera supprime dans <b><u>10 min</u> 🫥 <i></b>(pour des raisons de droits d\'auteur)</i>.\n\n<b><i>veuillez transmettre ce message a vos messages sauvegardes ou un chat prive.</i></b></blockquote>")
        await asyncio.sleep(600)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>✅ Votre message a ete supprime avec succes</b>")
        return    

    elif data.startswith("files"):
        user = message.from_user.id
        if temp.SHORT.get(user)==None:
            await message.reply_text(text="<b>Please Search Again in Group</b>")
        else:
            chat_id = temp.SHORT.get(user)
        settings = await get_settings(chat_id)
        pre = 'filep' if settings['file_secure'] else 'file'
    user = message.from_user.id
    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            if STREAM_MODE == True:
                button = [[InlineKeyboardButton('Streaming et telechargement', callback_data=f'generate_stream_link:{file_id}')]]
                reply_markup=InlineKeyboardMarkup(button)
            else:
                reply_markup = None
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                reply_markup=reply_markup
            )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(caption=f_caption)
            btn = [[InlineKeyboardButton("✅ Obtenir le fichier ✅", callback_data=f'del#{file_id}')]]
            k = await msg.reply(text=f"<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nce message sera supprime dans <b><u>10 min</u> 🫥 <i></b>(pour des raisons de droits d\'auteur)</i>.\n\n<b><i>veuillez transmettre ce message a vos messages sauvegardes ou un chat prive.</i></b></blockquote>")
            await asyncio.sleep(600)
            await msg.delete()
            await k.edit_text("<b>✅ Votre message a ete supprime avec succes si vous le souhaitez a nouveau, cliquez sur le bouton ci-dessous</b>",reply_markup=InlineKeyboardMarkup(btn))
            return
        except:
            pass
        return await message.reply('Ce fichier n\'existe pas.')
        
    files = files_
    title = files["file_name"]
    size=get_size(files["file_size"])
    f_caption=files["caption"]
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except:
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"@VJ_Bots {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files['file_name'].split()))}"
    if STREAM_MODE == True:
        button = [[InlineKeyboardButton('Streaming et telechargement', callback_data=f'generate_stream_link:{file_id}')]]
        reply_markup=InlineKeyboardMarkup(button)
    else:
        reply_markup = None
    msg = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
        reply_markup=reply_markup
    )
    btn = [[InlineKeyboardButton("✅ Obtenir le fichier ✅", callback_data=f'del#{file_id}')]]
    k = await msg.reply(text=f"<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nce message sera supprime dans <b><u>10 min</u> 🫥 <i></b>(pour des raisons de droits d\'auteur)</i>.\n\n<b><i>veuillez transmettre ce message a vos messages sauvegardes ou un chat prive.</i></b></blockquote>")
    await asyncio.sleep(600)
    await msg.delete()
    await k.edit_text("<b>✅ Votre message a ete supprime avec succes si vous le souhaitez a nouveau, cliquez sur le bouton ci-dessous</b>",reply_markup=InlineKeyboardMarkup(btn))
    return   
