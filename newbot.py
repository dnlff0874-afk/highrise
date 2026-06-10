from highrise import BaseBot, User, Position
from highrise.models import SessionMetadata
from datetime import datetime
import random
import pytz

class HighriseEliteBot(BaseBot):
    
    def __init__(self, owner_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اسم المالك الأساسي للبوت
        self.OWNER_USERNAME = "2e8"
        
        # قائمة الكلمات المحظورة لحماية الغرفة من السباب
        self.banned_words = ["سب1", "سب2", "كلمة_سيئة"] 
        
        # قائمة المشرفين (يمكن للمالك إضافتهم أثناء اللعبة)
        self.moderators = []
        
        # عدادات إحصائيات الغرفة
        self.total_joins = 0
        self.commands_executed = 0

        # ⏰ قاموس المناطق الزمنية للدول
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
        print(f"⚡ تم تشغيل البوت بنجاح! المالك الحالي هو: {self.OWNER_USERNAME}")
        print("🤖 أنظمة الحماية، التوقيت، الجلب، والتفاعل الجديد تعمل بكفاءة 100%.")

    async def on_user_join(self, user: User, position: Position) -> None:
        try:
            self.total_joins += 1
            await self.highrise.chat(f"مرحباً بك يا {user.username} في الغرفة الأسطورية! اكتب 'اوامر' لرؤية قدراتي ✨")
        except Exception as e:
            print(f"خطأ في الترحيب: {e}")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip()
        command = msg.lower()
        username_lower = user.username.lower()
        
        # التحقق من الصلاحيات
        is_owner = (username_lower == self.OWNER_USERNAME.lower())
        is_mod = (username_lower in [m.lower() for m in self.moderators]) or is_owner

        # ----------------------------------------------------------------------
        # 0. نظام الفلتر والحماية التلقائي (Anti-Toxic Filter)
        # ----------------------------------------------------------------------
        for word in self.banned_words:
            if word in command:
                try:
                    await self.highrise.chat(f"⚠️ | تم رصد مخالفة من @{user.username}. يرجى الالتزام بالقوانين!")
                    await self.highrise.kick_user(user.id)
                    return
                except Exception as e:
                    print(f"فشل الطرد التلقائي: {e}")

        try:
            # الرد التفاعلي عند ذكر كلمة بوت
            if "بوت" in command:
                responses = ["نعم! أنا هنا لخدمتكم 😎", "كيف يمكنني مساعدتك اليوم؟ 🔥"]
                await self.highrise.chat(random.choice(responses))
                return

            # ----------------------------------------------------------------------
            # 1. نظام التوقيت العالمي ومعرفة الساعة (World Time System)
            # ----------------------------------------------------------------------
            if msg.startswith("وقت ") or msg.startswith("!time "):
                parts = msg.split(" ")
                if len(parts) > 1:
                    country = parts[1].replace("@", "").lower()
                    if country in self.timezone_mapping:
                        self.commands_executed += 1
                        tz = pytz.timezone(self.timezone_mapping[country])
                        current_time = datetime.now(tz).strftime("%I:%M %p")
                        await self.highrise.chat(f"⏰ | الساعة الآن في {parts[1]} هي: {current_time} بالضبط.")
                    else:
                        await self.highrise.chat(f"❌ عذراً، لم يتم إدخال دولة '{parts[1]}' في نظامي بعد.")
                return

            # ----------------------------------------------------------------------
            # 2. أوامر الإشراف والتحكم (للمشرفين والمالك)
            # ----------------------------------------------------------------------
            if is_mod:
                # أمر "هات" أو "جيب" لجلب اللاعب إليك فوراً
                if msg.startswith("!get ") or msg.startswith("هات ") or msg.startswith("جيب "):
                    target_username = msg.split(" ")[1].replace("@", "")
                    room_users = await self.highrise.get_room_users()
                    caller_position = None
                    target_user = None
                    
                    for u, pos in room_users.content:
                        if u.username.lower() == username_lower:
                            caller_position = pos
                        if u.username.lower() == target_username.lower():
                            target_user = u
                    
                    if target_user and caller_position:
                        self.commands_executed += 1
                        new_position = Position(caller_position.x + 0.5, caller_position.y, caller_position.z, caller_position.facing)
                        await self.highrise.teleport(target_user.id, new_position)
                        await self.highrise.chat(f"🛸 | تم إحضار اللاعب @{target_username} بنجاح!")
                    else:
                        await self.highrise.chat(f"❌ تعذر العثور على اللاعب @{target_username} في الغرفة.")
                    return

                # أمر الطرد (Kick)
                elif msg.startswith("!kick "):
                    target_username = msg.split(" ")[1].replace("@", "")
                    target_user = await self.get_user_by_username(target_username)
                    if target_user:
                        self.commands_executed += 1
                        await self.highrise.kick_user(target_user.id)
                        await self.highrise.chat(f"🚫 تم طرد @{target_username} بواسطة الإدارة.")
                    return

                # أمر الحظر الدائم (Ban)
                elif msg.startswith("!ban "):
                    target_username = msg.split(" ")[1].replace("@", "")
                    target_user = await self.get_user_by_username(target_username)
                    if target_user:
                        self.commands_executed += 1
                        await self.highrise.ban_user(target_user.id, duration=86400) 
                        await self.highrise.chat(f"🚷 تم حظر @{target_username} نهائياً من الغرفة!")
                    return

            # ----------------------------------------------------------------------
            # 3. أوامر المالك فقط (Owner Only)
            # ----------------------------------------------------------------------
            if is_owner:
                if msg.startswith("!addmod "):
                    target = msg.split(" ")[1].replace("@", "")
                    if target not in self.moderators:
                        self.moderators.append(target)
                        await self.highrise.chat(f"✅ تم تعيين @{target} كمشرف في البوت.")
                    return
                
                elif msg.startswith("!removemod "):
                    target = msg.split(" ")[1].replace("@", "")
                    if target in self.moderators:
                        self.moderators.remove(target)
                        await self.highrise.chat(f"❌ تم إلغاء إشراف @{target}.")
                    return
                
                elif command == "احصائيات":
                    status_text = f"📊 إحصائيات البوت الحالية:\n🔹 عدد الزيارات الكلية: {self.total_joins}\n🔹 عدد الأوامر المنفذة: {self.commands_executed}"
                    await self.highrise.chat(status_text)
                    return

            # ----------------------------------------------------------------------
            # 4. أوامر التفاعل العامة الجديدة (All Users)
            # ----------------------------------------------------------------------
            
            # أمر الكف (Highfive)
            if msg.startswith("كف ") or msg.startswith("!h5 "):
                target_username = msg.split(" ")[1].replace("@", "")
                target_user = await self.get_user_by_username(target_username)
                if target_user:
                    self.commands_executed += 1
                    await self.highrise.chat(f"👋 | @{user.username} يعطي كفاً حماسياً لـ @{target_user.username}! 💥")
                    await self.highrise.send_emote("emote-fistbump", user.id)
                    await self.highrise.send_emote("emote-fistbump", target_user.id)
                else:
                    await self.highrise.chat(f"اللاعب @{target_username} غير موجود حالياً.")
                return

            # ❤️ أمر إرسال القلوب (جديد)
            elif msg.startswith("طلب قلب ") or msg.startswith("قلب ") or msg.startswith("!heart "):
                target_username = msg.split(" ")[1].replace("@", "")
                target_user = await self.get_user_by_username(target_username)
                if target_user:
                    self.commands_executed += 1
                    await self.highrise.chat(f"❤️ | @{user.username} يرسل طاقة حب وقلوب دافئة إلى @{target_user.username}! ✨💖")
                    await self.highrise.send_emote("emote-blowkiss", user.id) # حركة إرسال القلوب باليد
                    await self.highrise.send_emote("emote-waving", target_user.id)
                else:
                    await self.highrise.chat(f"اللاعب @{target_username} غير موجود حالياً في الروم.")
                return

            # 💋 أمر البوسة والقبلة التفاعلية (جديد)
            elif msg.startswith("بوسه ") or msg.startswith("بوسة ") or msg.startswith("!kiss "):
                target_username = msg.split(" ")[1].replace("@", "")
                target_user = await self.get_user_by_username(target_username)
                if target_user:
                    self.commands_executed += 1
                    await self.highrise.chat(f"💋 | أمواااح! @{user.username} يعطي بوسة لطيفة لـ @{target_user.username}! 🥰عاشوا واجتمعوا")
                    await self.highrise.send_emote("emote-blowkiss", user.id) # حركة التقبيل ونفخ الهواء
                    await self.highrise.send_emote("emote-shy", target_user.id) # حرك الخجل للمستلم
                else:
                    await self.highrise.chat(f"اللاعب @{target_username} غير متواجد حالياً.")
                return

            # قائمة المساعدة العامة لعرض كافة القدرات
            elif command in ["الأوامر", "اوامر", "!help"]:
                self.commands_executed += 1
                help_text = (
                    "📋 قائمة أوامر التفاعل والتحكم المحدثة:\n"
                    "🔹 'وقت السعودية' أو 'وقت مصر' لمعرفة الساعة\n"
                    "🔹 'كف @الاسم' لتبادل الكفوف الحماسية 👋\n"
                    "🔹 'قلب @الاسم' لإرسال قلوب حب متطايرة ❤️\n"
                    "🔹 'بوسه @الاسم' لإعطاء قبلة تفاعلية مضحكة 💋\n"
                    "👮 للمشرفين: 'جيب @الاسم' | !kick @الاسم\n"
                    "👑 للمالك: !addmod @الاسم | احصائيات"
                )
                await self.highrise.chat(help_text)

        except Exception as e:
            print(f"حدث خطأ أثناء تنفيذ الأمر: {e}")

    async def get_user_by_username(self, username: str):
        room_users = await self.highrise.get_room_users()
        for u, pos in room_users.content:
            if u.username.lower() == username.lower():
                return u
        return None

# --- [ إعدادات التشغيل والربط بالسيرفر ] ---
from highrise.__main__ import main, BotDefinition
import asyncio

ROOM_ID = "6a2748e7446ef40e6d5ee2c1"
API_TOKEN = "dfc25c6247a23d811e2066d7c0ec325cba8f5819c6f3b39113567b52520abd62"
OWNER_NAME = "2e8"

bot_instance = HighriseEliteBot(owner_username=OWNER_NAME)

definition = BotDefinition(
    bot_instance,
    ROOM_ID,
    API_TOKEN
)

print(API_TOKEN)
asyncio.run(main([definition]))