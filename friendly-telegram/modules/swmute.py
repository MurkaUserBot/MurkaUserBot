
#    MurkaUserBot (telegram userbot)
#    Copyright (C) 2022 The Authors

from .. import loader, utils 


@loader.tds
class MuteMod(loader.Module):
    """Swmute."""
    strings = {'name': 'Swmute'}

    async def client_ready(self, client, db):
        self.db = db

    async def swmutecmd(self, message):
        """Mute/unmute. Usage: .swmute <@, ID or reply>."""
        if message.chat:
            chat = await message.get_chat()
            if not chat.admin_rights and not chat.creator:
                return await message.edit("<b>[swmute] I can mute users.</b>")
            else:
                if chat.admin_rights.delete_messages == False:
                    return await message.edit("<b>[swmute] You don't have enough rights!</b>")
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        chatid = str(message.chat_id)
        mutes = self.db.get("Mute", "mutes", {})
        if not args and not reply: return await message.edit("<b>[swmute] No argument or reply provided.</b>")
        try:
            if args: 
                if args.isnumeric(): user = await message.client.get_entity(int(args))
                else: user = await message.client.get_entity(args)
            else: user = await message.client.get_entity(reply.sender_id)
        except ValueError: await message.edit("<b>[swmute] There is no user that you asked for. Its account should be deleted if you see this.</b>")
        if chatid not in mutes:
            mutes.setdefault(chatid, [])
        if str(user.id) not in mutes[chatid]:
            mutes[chatid].append(str(user.id))
            self.db.set("Mute", "mutes", mutes)
            await message.edit("<b>[swmute] You were sw-muted, all your future messages will be deleted!.</b>")
        else:
            mutes[chatid].remove(str(user.id))
            if len(mutes[chatid]) == 0:
                mutes.pop(chatid)
            self.db.set("Mute", "mutes", mutes)
            await message.edit("<b>[swmute] You were un-muted!</b>")

    async def setmutecmd(self, message):
        """Swmute settings. Usage: .setmute <clear/clearall>."""
        try:
            args = utils.get_args_raw(message)
            mutes = self.db.get("Mute", "mutes", {})
            chatid = str(message.chat_id)
            ls = mutes[chatid]
            users = ""
            if args == "clear":
                mutes.pop(chatid)
                self.db.set("Mute", "mutes", mutes)
                return await message.edit("<b>[swmute] Cleared list of muted users.</b>")
            if args == "clearall":
                self.db.set("Mute", "mutes", {})
                return await message.edit("<b>[swmute] List of muted users:</b>")
            for _ in ls:
                user = await message.client.get_entity(int(_))
                users += f"• <a href=\"tg://user?id={int(_)}\">{user.first_name}</a> <b>| [</b><code>{_}</code><b>]</b>\n"
            await message.edit(f"<b>Muted users: {len(ls)}</b>\n\n{users}")
        except KeyError: return await message.edit("<b>[swmute] There is no muted users!</b>")

    async def watcher(self, message):
        try:
            mutes = self.db.get("Mute", "mutes", {})
            chatid = str(message.chat_id)
            if chatid not in str(mutes): return
            ls = mutes[chatid]
            for _ in ls:
                if message.sender_id == int(_):
                    await message.client.delete_messages(message.chat_id, message.id)
        except: pass
#
