import asyncio
import random
import os
import json
import time
from aiohttp import web
from highrise import BaseBot, Position
from highrise.models import User, SessionMetadata

# ========================================================
# 1. خادم ويب حقيقي ومتوافق مع نظام Asyncio لمنع إعادة التشغيل
# ========================================================
async def handle_ping(request):
    return web.Response(text="Bot is perfectly alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    try:
        await site.start()
        print(f"🌍 Asyncio Web Server Listening perfectly on port {port}")
    except Exception as e:
        print(f"⚠️ Web Server Failed to bind: {e}")

# ========================================================
# 2. فئة البوت الاحترافية بالألوان وإيموجيات اللعبة الحقيقية
# ========================================================
class HighriseEliteBot(BaseBot):
    
    def __init__(self, owner_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.OWNER_USERNAME = "2e8"
        self.TARGET_USER = "A__4o"
        self.moderators = ["2e8"] 
        
        self.banned_words = ["امك", "عاهره", "ابن كلبه", "ابن عاهره", "عاهرة"] 
        self.room_users = {}        
        self.bot_user_id = None  
        self.is_frozen = False      

        self.db_file = "database.json"
        self.db = self.load_database()

        self.locations = {
            "1": Position(12.0, 8.5, 12.0, "facingRight"),  
            "2": Position(5.0, 12.0, 5.0, "facingLeft"),    
            "3": Position(3.0, 0.0, 3.0, "facingRight")     
        }

    def load_database(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    return json.load(f)
            except: pass
        return {"bot_position": None, "muted_users": {}, "frozen_players": {}, "user_warnings": {}}

    def save_database(self):
        try:
            with open(self.db_file, "w") as f:
                json.dump(self.db, f)
        except Exception as e:
            print(f"Error saving database: {e}")

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print(f"⚡ بوت الأوامر الحقيقية جاهز! المالك: {self.OWNER_USERNAME}")
        self.bot_user_id = session_metadata.user_id 
        
        await asyncio.sleep(2.0)
        
        try:
            initial_users = await self.highrise.get_room_users()
            for u, pos in initial_users.content:
                self.room_users[u.id] = u
            print("✅ تم ربط المستخدمين بنجاح البوت يعمل الآن.")
        except Exception as e:
            print(f"Error packing users: {e}")
        
        if self.db.get("bot_position"):
            bp = self.db["bot_position"]
            try:
                await self.highrise.teleport(self.bot_user_id, Position(bp["x"], bp["y"], bp["z"], bp["facing"]))
            except: pass

        asyncio.create_task(self.send_trade_announcements())

    async def on_user_move(self, user: User, destination: Position) -> None:
        try:
            uid_str = str(user.id)
            if uid_str in self.db["frozen_players"]:
                if time.time() > self.db["frozen_players"][uid_str]["expire_time"]:
                    del self.db["frozen_players"][uid_str]
                    if uid_str in self.db["muted_users"]: del self.db["muted_users"][uid_str]
                    self.save_database()
                    await self.highrise.chat(f"<color=#00FF00>🕊️ انتهت العقوبة، تم فك تجميد وكتم @{user.username} تلقائياً.</color>")
                    return
                
                fp = self.db["frozen_players"][uid_str]
                await self.highrise.teleport(user.id, Position(fp["x"], fp["y"], fp["z"], fp["facing"]))
                return

            if user.username.lower() == self.OWNER_USERNAME.lower():
                if isinstance(destination, Position):
                    if 0.0 <= destination.x <= 1.5 and 0.0 <= destination.z <= 1.5:
                        await self.highrise.teleport(user.id, self.locations["1"])
                        await self.highrise.send_whisper(user.id, "🚀 تم سحبك تلقائياً للمنصة العلوية!")
        except Exception as e:
            print(f"Error in move system: {e}")

    async def on_whisper(self, user: User, message: str) -> None:
        username_lower = user.username.lower()
        is_mod = (username_lower in [m.lower() for m in self.moderators]) or (username_lower == self.OWNER_USERNAME.lower())
        if not is_mod: return
        
        msg = message.strip().lower()
        if msg in self.locations:
            await self.highrise.teleport(user.id, self.locations[msg])
            return

    async def send_trade_announcements(self):
        while True:
            try:
                await asyncio.sleep(90) 
                if not self.is_frozen and self.bot_user_id:
                    announcements = [
                        "<color=#FFFF00>🏪 متجرك جاهز؟ اعرض عروضك وسلعك الأسطورية هنا مجاناً وفالك الملايين والربح يا ملك التجارة! 🛍️✨</color>",
                        "<color=#FFA500>⚠️ انتبه يا ملك! تأكد من المقايضة وفحص العناصر 100% قبل الضغط على زر القبول لتجنب الخداع. 🤝❌</color>"
                    ]
                    await self.highrise.chat(random.choice(announcements))
            except:
                await asyncio.sleep(10)

    async def on_user_join(self, user: User, position: Position) -> None:
        try:
            self.room_users[user.id] = user 
            if user.id == self.bot_user_id: return

            if user.username.lower() == self.OWNER_USERNAME.lower():
                await self.highrise.chat(f"<color=#FF0000>👑 انحناء وترحيب حار لتاج راسنا ومالك السيرفر @{user.username} وصل يا ملوك الروم! ❤️✨</color>")
                await self.highrise.react("heart", user.id) 
                return

            if user.username.lower() == self.TARGET_USER.lower():
                await self.highrise.chat(f"<color=#00FF7F>🗼 راعي برج إيفل ومقاس 40 وصل @{user.username} 😂🫵🏻 أرحب يا أسطورة النكتة!</color>")
                await self.highrise.react("wink", user.id) 
                return

            reactions = ["clap", "heart", "thumbs", "wink"]
            chosen_reaction = random.choice(reactions)
            await self.highrise.chat(f"<color=#00FFFF>👋 أرحب يا @{user.username} نورت سوق النخبة للتجارة والمقايضة! 🛒💎</color>")
            await self.highrise.react(chosen_reaction, user.id)
        except Exception as e:
            print(f"Error in user join flow: {e}")

    async def on_user_leave(self, user: User) -> None:
        if user.id in self.room_users: del self.room_users[user.id]

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip()
        command = msg.lower()
        username_lower = user.username.lower()
        
        is_owner = (username_lower == self.OWNER_USERNAME.lower())
        is_mod = (username_lower in [m.lower() for m in self.moderators]) or is_owner

        if str(user.id) in self.db["muted_users"]:
            if time.time() < self.db["muted_users"][str(user.id)]: 
                return 
            else: 
                del self.db["muted_users"][str(user.id)]
                self.save_database()

        if self.is_frozen and not is_mod: return

        for word in self.banned_words:
            if word in command:
                if is_mod: return 
                room_users_data = await self.highrise.get_room_users()
                current_player_pos = Position(2,0,2)
                for u, pos in room_users_data.content:
                    if u.id == user.id: current_player_pos = pos; break

                uid_str = str(user.id)
                self.db["user_warnings"][uid_str] = self.db["user_warnings"].get(uid_str, 0) + 1
                self.save_database()
                
                if self.db["user_warnings"][uid_str] == 1:
                    await self.highrise.chat(f"<color=#FF8C00>⚠️ | إنذار أول للمخالف @{user.username} ! ممنوع السب في غرفتنا، المرة القادمة عقاب صارم! 🤬❌</color>")
                    await self.highrise.react("thumbs", user.id) 
                    return
                elif self.db["user_warnings"][uid_str] >= 2:
                    expire_time = time.time() + (5 * 60)
                    self.db["muted_users"][uid_str] = expire_time
                    if isinstance(current_player_pos, Position):
                        self.db["frozen_players"][uid_str] = {
                            "x": current_player_pos.x, "y": current_player_pos.y, "z": current_player_pos.z, "facing": current_player_pos.facing,
                            "expire_time": expire_time
                        }
                    self.save_database()
                    await self.highrise.chat(f"<color=#FF0000>🥶⛔ | تم قفل الحساب عقابياً! المخالف @{user.username} تكرر منه السب، النتيجة: كتم وتجميد لمدة 5 دقائق! 🤫💥</color>")
                    return

        try:
            if "بوت" in command:
                await self.highrise.chat("<color=#FF00FF>لبيه وآمرني! البوت الأسطوري الحارس في خدمتك الحين 🔥😉</color>")
                return

            if is_mod:
                if msg.startswith("تجميد ") or command.startswith("freeze "):
                    parts = msg.split(" ")
                    target = parts[1].replace("@", "")
                    t_user = await self.get_user_by_username(target)
                    if t_user:
                        if t_user.username.lower() in [m.lower() for m in self.moderators]:
                            await self.highrise.chat("❌ لا يمكنك تجميد إداري!")
                            return
                        
                        room_users_data = await self.highrise.get_room_users()
                        current_player_pos = Position(2,0,2)
                        for u, pos in room_users_data.content:
                            if u.id == t_user.id: current_player_pos = pos; break

                        uid_str = str(t_user.id)
                        expire_time = time.time() + (5 * 60)
                        
                        self.db["muted_users"][uid_str] = expire_time
                        if isinstance(current_player_pos, Position):
                            self.db["frozen_players"][uid_str] = {
                                "x": current_player_pos.x, "y": current_player_pos.y, "z": current_player_pos.z, "facing": current_player_pos.facing,
                                "expire_time": expire_time
                            }
                        self.save_database()
                        await self.highrise.chat(f"<color=#FF4500>🥶🔒 | بأمر الإدارة، تم تجميد حركتك وكتم شاتك يا @{target} لمدة 5 دقائق كاملة!</color>")
                    return

                elif msg.startswith("كتم ") or command.startswith("mute "):
                    parts = msg.split(" ")
                    target = parts[1].replace("@", "")
                    minutes = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 5
                    t_user = await self.get_user_by_username(target)
                    if t_user:
                        if t_user.username.lower() in [m.lower() for m in self.moderators]:
                            await self.highrise.chat("❌ لا يمكنك كتم إداري!")
                            return
                        self.db["muted_users"][str(t_user.id)] = time.time() + (minutes * 60)
                        self.save_database()
                        await self.highrise.chat(f"<color=#1E90FF>🤫 تم ربط لسان @{target} وكتم شاته بالكامل لمدة {minutes} دقائق.</color>")
                    return

                elif msg.startswith("طرد ") or command.startswith("kick "):
                    parts = msg.split(" ")
                    target = parts[1].replace("@", "")
                    t_user = await self.get_user_by_username(target)
                    if t_user: 
                        if t_user.username.lower() in [m.lower() for m in self.moderators]:
                            await self.highrise.chat("❌ لا يمكنك طرد إداري!")
                            return
                        await self.highrise.kick_user(t_user.id)
                        await self.highrise.chat(f"<color=#FF0000>👞 تم طرد المشاغب @{target} خارج الروم!</color>")
                    return

                elif msg.startswith("فك_تجميد ") or command.startswith("unfreeze "):
                    parts = msg.split(" ")
                    target = parts[1].replace("@", "")
                    t_user = await self.get_user_by_username(target)
                    if t_user:
                        uid_str = str(t_user.id)
                        if uid_str in self.db["frozen_players"]: del self.db["frozen_players"][uid_str]
                        if uid_str in self.db["muted_users"]: del self.db["muted_users"][uid_str]
                        if uid_str in self.db["user_warnings"]: self.db["user_warnings"][uid_str] = 0
                        self.save_database()
                        await self.highrise.chat(f"<color=#00FF00>🕊️ تم العفو عن @{target} وفك تجميده وكتمه بنجاح.</color>")
                    return

                elif msg.startswith("اجلب ") or command.startswith("br "):
                    parts = msg.split(" ")
                    target = parts[1].replace("@", "")
                    room_users = await self.highrise.get_room_users()
                    caller_pos = None; t_user = None
                    for u, pos in room_users.content:
                        if u.username.lower() == username_lower: caller_pos = pos
                        if u.username.lower() == target.lower(): t_user = u
                    if t_user and caller_pos and isinstance(caller_pos, Position):
                        await self.highrise.teleport(t_user.id, Position(caller_pos.x + 0.5, caller_pos.y, caller_pos.z, caller_pos.facing))
                    return

                elif msg.startswith("ارقص ") or command.startswith("dance "):
                    parts = msg.split(" ")
                    if len(parts) > 1:
                        target = parts[1].replace("@", "")
                        emote_id = parts[2] if len(parts) > 2 else "emote-dance-tiktok"
                        t_user = await self.get_user_by_username(target)
                        if t_user: 
                            await self.highrise.send_emote(emote_id, t_user.id)
                    return

                elif msg.startswith("قصف ") or command.startswith("roast "):
                    parts = msg.split(" ")
                    target = parts[1].replace("@", "")
                    roasts = [
                        f"<color=#FFD700>يا @{target} شكلك نسيت تلبس هيبتك وأنت داخل الروم اليوم؟ 😂🫵🏻</color>",
                        f"<color=#FFD700>تكفى يا @{target} صجيتنا، روح رتب متجرك المكسر بعدين تعال تفلسف علينا 🤫🛒</color>"
                    ]
                    await self.highrise.chat(random.choice(roasts))
                    return

                if command in ["تثبيت", "هنا", "قفل_مكاني"] and is_owner:
                    room_users_data = await self.highrise.get_room_users()
                    owner_pos = None
                    for u, pos in room_users_data.content:
                        if u.username.lower() == self.OWNER_USERNAME.lower(): owner_pos = pos; break
                    
                    if owner_pos and isinstance(owner_pos, Position):
                        self.db["bot_position"] = {"x": owner_pos.x, "y": owner_pos.y, "z": owner_pos.z, "facing": owner_pos.facing}
                        self.save_database()
                        await self.highrise.teleport(self.bot_user_id, owner_pos)
                        await self.highrise.chat("<color=#FFFF00>📍 تم التقاط وتثبيت هذا الموقع في الذاكرة الدائمة بنجاح! 🫡👑</color>")
                    return

                elif msg == "تجميد_الشات":
                    self.is_frozen = True
                    await self.highrise.chat("<color=#BA55D3>❄️ تم تجميد شات الروم بالكامل!</color>")
                    return
                elif msg in ["فك", "تفعيل"]:
                    self.is_frozen = False
                    await self.highrise.chat("<color=#BA55D3>🔥 تم فك تجميد الشات!</color>")
                    return

            if command in ["الأوامر", "اوامر", "!help"]:
                help_text = "📋 لوحة التحكم الشاملة بالمنشن:\n🔹 تجميد @username | كتم @username\n🔹 طرد @username | فك_تجميد @username\n🔹 اجلب @username | ارقص @username"
                await self.highrise.chat(help_text)

        except Exception as e:
            print(f"Error command execution: {e}")

    async def get_user_by_username(self, username: str):
        for u in self.room_users.values():
            if u.username.lower() == username.lower(): return u
        try:
            room_users = await self.highrise.get_room_users()
            for u, pos in room_users.content:
                if u.username.lower() == username.lower():
                    self.room_users[u.id] = u
                    return u
        except: pass
        return None

# --- [ إعدادات التشغيل والربط بالتوازي ] ---
from highrise.__main__ import main, BotDefinition

async def run_bot():
    ROOM_ID = "6a2926cfc5102b78599c32b8"
    API_TOKEN = "385ebb75af320dae0a416e51bb5b79151b4b7c2c52b6d8257ce75bca69ba0952"
    OWNER_NAME = "2e8"

    bot_instance = HighriseEliteBot(owner_username=OWNER_NAME)
    definition = BotDefinition(bot_instance, ROOM_ID, API_TOKEN)
    await main([definition])

async def main_execution():
    # تشغيل سيرفر الويب والبوت معاً لضمان عدم توقف الخدمة على Render
    await asyncio.gather(
        start_web_server(),
        run_bot()
    )

if __name__ == "__main__":
    asyncio.run(main_execution())