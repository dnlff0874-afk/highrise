import threading
import asyncio
import random
import os
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
from highrise import BaseBot, Position
from highrise.models import User, SessionMetadata
import pytz

# ========================================================
# 1. سيرفر الويب المطور لقراءة البورت تلقائياً ومنع الفصل
# ========================================================
def run_dummy_server():
    class SafeHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
    
    # قراءة البورت الذي يطلبه Render تلقائياً، وإذا لم يجده يختار 10000 كاحتياطي
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SafeHandler)
    print(f"🌍 Keep-Alive server is running on port {port}")
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# ========================================================
# 2. فئة البوت وإعدادات الأنظمة الأساسية الشاملة
# ========================================================
class HighriseEliteBot(BaseBot):
    
    def __init__(self, owner_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.OWNER_USERNAME = "2e8"
        self.TARGET_USER = "A__4o"
        self.banned_words = ["سب1", "سب2"] 
        self.moderators = []
        
        self.total_joins = 0
        self.commands_executed = 0
        self.is_frozen = False      
        self.room_users = {}        
        self.muted_users = {}       
        self.saved_position = None  

        self.bot_emotes = [
            "emote-fashion", "emote-shy", "emote-dance-tiktok",
            "emote-charging", "emote-shoppingcart", "emote-superpose",
            "emote-russianwave", "emote-blackpink", "emote-customtrack"
        ]

        self.timezone_mapping = {
            "السعودية": "Asia/Riyadh", "saudi": "Asia/Riyadh",
            "مصر": "Africa/Cairo", "egypt": "Africa/Cairo",
            "الإمارات": "Asia/Dubai", "uae": "Asia/Dubai",
            "الكويت": "Asia/Kuwait", "kuwait": "Asia/Kuwait",
            "العراق": "Asia/Baghdad", "iraq": "Asia/Baghdad",
            "المغرب": "Africa/Casablanca", "morocco": "Africa/Casablanca",
            "الجزائر": "Africa/Algiers", "algeria": "Africa/Algiers",
            "تونس": "Africa/Tunis", "tunisia": "Africa/Tunis",
            "الأردن": "Asia/Amman", "jordan": "Asia/Amman",
            "فلسطين": "Asia/Gaza", "palestine": "Asia/Gaza",
            "قطر": "Asia/Qatar", "qatar": "Asia/Qatar",
            "البحرين": "Asia/Bahrain", "bahrain": "Asia/Bahrain",
            "عمان": "Asia/Muscat", "oman": "Asia/Muscat",
            "لبنان": "Asia/Beirut", "lebanon": "Asia/Beirut",
            "سوريا": "Asia/Damascus", "syria": "Asia/Damascus",
            "اليمن": "Asia/Aden", "yemen": "Asia/Aden",
            "ليبيا": "Africa/Tripoli", "libya": "Africa/Tripoli",
            "السودان": "Africa/Khartoum", "sudan": "Africa/Khartoum"
        }

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print(f"⚡ تم تشغيل البوت بنجاح! المالك: {self.OWNER_USERNAME}")
        asyncio.create_task(self.send_trade_announcements())
        asyncio.create_task(self.recommend_random_shop())

    async def send_trade_announcements(self):
        while True:
            await asyncio.sleep(10)
            if not self.is_frozen:
                await self.highrise.chat("🏪 الغرفة غرفتكم والمكان مكانكم! هنا يقدم كل اللاعبين متاجرهم وعروضهم مجاناً وبدون أي رسوم! اعرضوا سلعكم وفالكم التوفيق يا ملوك البزنس والبيع 🛍️✨")
                await asyncio.sleep(2.0)
                await self.highrise.chat("⚠️ ولكن احذر يا صديقي ويا صديقتي من النصب والاحتيال! لا تندفعوا وتأكدوا من المقايضة 100% قبل الضغط على زر القبول. التجارة شطارة والحرص واجب دائماً! 🤝❌")

    async def recommend_random_shop(self):
        while True:
            await asyncio.sleep(120)
            if self.room_users and not self.is_frozen:
                random_user = random.choice(list(self.room_users.values()))
                if random_user.username.lower() != self.OWNER_USERNAME.lower():
                    await self.highrise.chat(f"✨ عيونكم هناااا يا تجار! 👀 تعالوا شوفوا متجر هذا الشخص المحظوظ والعشوائي لليوم: @{random_user.username} ✨ ادخلوا بروفايله وشوفوا عروضه الأسطورية! 🔥🛒")

    async def on_user_join(self, user: User, position: Position) -> None:
        try:
            self.total_joins += 1
            self.room_users[user.id] = user

            if user.username.lower() == self.OWNER_USERNAME.lower():
                await self.highrise.chat(f"👑 أهلاً وسهلاً بتاج راسنا ومالك الغرفة الغالي @{user.username} ! نورت بيتك ومطرحك يا كبير! ❤️✨")
                return

            if user.username.lower() == self.TARGET_USER.lower():
                await self.highrise.chat(f"🗼 أوه @{user.username} وصل! راعي برج إيفل اللي يلبس في رجله مقاس 40 😂🫵🏻 نورتنا يا وحش الملاعب!")
                return

            welcome_messages = [
                f"👋 يا هلا وغلا بـ @{user.username} في أكبر سوق تجاري! نور الروم بوجودك ✨🛍️",
                f"🔥 أرحبببب يا @{user.username}! جهز متجرك واعرض عروضك القوية معنا اليوم 🛒🌟",
                f"💎 نورت غرفة النخبة للتجارة يا @{user.username}! نتمنى لك مقايضات ناجحة ومربحة 🤝⚡"
            ]
            await self.highrise.chat(random.choice(welcome_messages))
        except Exception as e:
            print(f"Error join: {e}")

    async def on_user_leave(self, user: User) -> None:
        if user.id in self.room_users:
            del self.room_users[user.id]

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip()
        command = msg.lower()
        username_lower = user.username.lower()
        
        is_owner = (username_lower == self.OWNER_USERNAME.lower())
        is_mod = (username_lower in [m.lower() for m in self.moderators]) or is_owner

        if user.id in self.muted_users:
            if asyncio.get_event_loop().time() < self.muted_users[user.id]:
                return
            else:
                del self.muted_users[user.id]

        if self.is_frozen and not is_mod:
            return

        for word in self.banned_words:
            if word in command:
                await self.highrise.kick_user(user.id)
                return

        try:
            if "بوت" in command:
                await self.highrise.chat("لبيه! كيف يمكنني مساعدتك اليوم؟ 🔥")
                return

            if msg.startswith("وقت ") or msg.startswith("!time "):
                parts = msg.split(" ")
                if len(parts) > 1:
                    country = parts[1].replace("@", "").lower()
                    if country in self.timezone_mapping:
                        self.commands_executed += 1
                        tz = pytz.timezone(self.timezone_mapping[country])
                        current_time = datetime.now(tz).strftime("%I:%M %p")
                        await self.highrise.chat(f"⏰ | الساعة الآن في {parts[1]} هي: {current_time} بالضبط.")
                return

            if is_mod:
                if msg.startswith("طرد ") or command.startswith("kick "):
                    target = msg.split(" ")[1].replace("@", "")
                    t_user = await self.get_user_by_username(target)
                    if t_user: await self.highrise.kick_user(t_user.id)
                    return

                elif msg.startswith("حظر ") or command.startswith("ban "):
                    parts = msg.split(" ")
                    target = parts[1].replace("@", "")
                    duration = int(parts[2]) * 60 if len(parts) > 2 and parts[2].isdigit() else 300
                    t_user = await self.get_user_by_username(target)
                    if t_user: await self.highrise.ban_user(t_user.id, duration=duration)
                    return

                elif msg.startswith("كتم ") or command.startswith("mute "):
                    parts = msg.split(" ")
                    target = parts[1].replace("@", "")
                    minutes = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 5
                    t_user = await self.get_user_by_username(target)
                    if t_user: self.muted_users[t_user.id] = asyncio.get_event_loop().time() + (minutes * 60)
                    return

                elif msg.startswith("اجلب ") or command.startswith("br "):
                    target = msg.split(" ")[1].replace("@", "")
                    room_users = await self.highrise.get_room_users()
                    caller_pos = None
                    t_user = None
                    for u, pos in room_users.content:
                        if u.username.lower() == username_lower: caller_pos = pos
                        if u.username.lower() == target.lower(): t_user = u
                    if t_user and caller_pos and isinstance(caller_pos, Position):
                        await self.highrise.teleport(t_user.id, Position(caller_pos.x + 0.5, caller_pos.y, caller_pos.z, caller_pos.facing))
                    return

                elif msg.startswith("تبديل ") or command.startswith("swap "):
                    parts = msg.split(" ")
                    u1_name = parts[1].replace("@", "")
                    u2_name = parts[2].replace("@", "")
                    room_users = await self.highrise.get_room_users()
                    user1, user2, pos1, pos2 = None, None, None, None
                    for u, pos in room_users.content:
                        if u.username.lower() == u1_name.lower(): user1, pos1 = u, pos
                        if u.username.lower() == u2_name.lower(): user2, pos2 = u, pos
                    if user1 and user2 and pos1 and pos2:
                        await self.highrise.teleport(user1.id, pos2)
                        await self.highrise.teleport(user2.id, pos1)
                    return

                elif msg.startswith("رقصوا") or command.startswith("danceall"):
                    parts = msg.split(" ")
                    emote_id = parts[1] if len(parts) > 1 else "emote-dance-tiktok"
                    for u_id in self.room_users.keys(): await self.highrise.send_emote(emote_id, u_id)
                    return

                elif msg == "احفظ" or command == "savepos":
                    room_users = await self.highrise.get_room_users()
                    for u, pos in room_users.content:
                        if u.username.lower() == username_lower: self.saved_position = pos
                    return

                elif msg == "تجميد":
                    self.is_frozen = True
                    return
                elif msg in ["فك", "تفعيل"]:
                    self.is_frozen = False
                    return

            if command in ["الأوامر", "اوامر", "!help"]:
                help_text = "📋 أوامر الإشراف: طرد، حظر، كتم، اجلب، تبديل، رقصوا، احفظ، تجميد/فك."
                await self.highrise.chat(help_text)

        except Exception as e:
            print(f"Error command: {e}")

    async def get_user_by_username(self, username: str):
        room_users = await self.highrise.get_room_users()
        for u, pos in room_users.content:
            if u.username.lower() == username.lower(): return u
        return None

# --- [ إعدادات التشغيل والربط ] ---
from highrise.__main__ import main, BotDefinition

ROOM_ID = "6a2926cfc5102b78599c32b8"
API_TOKEN = "385ebb75af320dae0a416e51bb5b79151b4b7c2c52b6d8257ce75bca69ba0952"
OWNER_NAME = "2e8"

bot_instance = HighriseEliteBot(owner_username=OWNER_NAME)
definition = BotDefinition(bot_instance, ROOM_ID, API_TOKEN)

asyncio.run(main([definition]))