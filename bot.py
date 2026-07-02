import os
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# DIQQAT: Tokenni har safar GitHub'ga yuklashdan oldin o'chirib qo'ying!
TOKEN = "8849386246:AAEKJWj9uKJMI3PdkOTookVGZrcLGudClkw"

ADMINS = [
    1628119985,
    6506671718,
    1810163607
]

FIO, PHONE, DISTRICT, TEXT, FILE = range(5)

counter = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Assalomu alaykum!\n\n"
        "Respublika Tez Tibbiy Yordam Markazi Toshkent viloyati filiali "
        "murojaatlar botiga xush kelibsiz.\n\n"
        "✍️ F.I.Sh. kiriting:"
    )
    return FIO

async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("📍 Tuman/Shahar nomini kiriting:")
    return DISTRICT

async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["district"] = update.message.text
    await update.message.reply_text("📝 Murojaat matnini kiriting:")
    return TEXT

async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text
    await update.message.reply_text(
        "📎 Foto yoki fayl yuboring.\n\n"
        "Agar ilova qilmoqchi bo‘lmasangiz /skip yuboring."
    )
    return FILE

async def skip_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_to_admins(update, context, msg_with_file=None)
    return ConversationHandler.END

async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_to_admins(update, context, msg_with_file=update.message)
    return ConversationHandler.END

async def send_to_admins(update: Update, context: ContextTypes.DEFAULT_TYPE, msg_with_file=None):
    global counter

    appeal_id = f"2026-{counter:04d}"
    counter += 1
    
    user_id = update.effective_user.id

    # ID aniqlash oson bo'lishi uchun xabar oxiriga aniq qilib yozib qo'yamiz
    text = (
        f"📨 YANGI MUROJAAT\n\n"
        f"🆔 {appeal_id}\n\n"
        f"👤 F.I.Sh.: {context.user_data['fio']}\n"
        f"📞 Telefon: {context.user_data['phone']}\n"
        f"📍 Hudud: {context.user_data['district']}\n\n"
        f"📝 Murojaat:\n"
        f"{context.user_data['text']}\n\n"
        f"👤 Foydalanuvchi: <a href='tg://user?id={user_id}'>Profilga o'tish</a>\n"
        f"🔑 [User_ID: {user_id}]"  # Regex orqali kafolatlangan qidiruv uchun
    )

    for admin in ADMINS:
        try:
            if msg_with_file:
                if msg_with_file.photo:
                    await context.bot.send_photo(
                        chat_id=admin,
                        photo=msg_with_file.photo[-1].file_id,
                        caption=text,
                        parse_mode="HTML"
                    )
                elif msg_with_file.document:
                    await context.bot.send_document(
                        chat_id=admin,
                        document=msg_with_file.document.file_id,
                        caption=text,
                        parse_mode="HTML"
                    )
                else:
                    await context.bot.send_message(chat_id=admin, text=text, parse_mode="HTML")
            else:
                await context.bot.send_message(chat_id=admin, text=text, parse_mode="HTML")
        except Exception as e:
            print(f"Adminga yuborishda xatolik ({admin}): {e}")

    await update.message.reply_text(
        f"✅ Murojaatingiz qabul qilindi.\n\n"
        f"🆔 Murojaat raqami: {appeal_id}\n\n"
        f"📌 Murojaatingiz ko'rib chiqiladi va javob beriladi.\n"
        f"Yangi murojaat qoldirish uchun /start buyrug'ini bosing."
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Murojaat bekor qilindi. Qayta boshlash uchun /start bosing.")
    return ConversationHandler.END

async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Faqat adminlar javob yoza olishini tekshirish
    if update.effective_user.id not in ADMINS:
        return

    reply_to = update.message.reply_to_message
    if not reply_to:
        return

    user_id = None
    
    # 1-usul: Xabar matni yoki izoh (caption) ichidan [User_ID: 12345] ni matn qidirish (Regex) orqali topish
    target_text = reply_to.text or reply_to.caption
    if target_text:
        match = re.search(r"\[User_ID:\s*(\d+)\]", target_text)
        if match:
            user_id = int(match.group(1))

    # 2-usul: Agar matndan topilmasa, havola (link) entity'laridan qidirish (Zaxira usul)
    if not user_id:
        entities = reply_to.entities or reply_to.caption_entities
        if entities:
            for entity in entities:
                if entity.type == "text_link" and entity.url.startswith("tg://user?id="):
                    user_id = int(entity.url.split("id=")[1])
                    break

    # Agar foydalanuvchi aniqlangan bo'lsa, unga javobni yuboramiz
    if user_id:
        try:
            reply_text = f"🔔 <b>Murojaatingizga javob xati keldi:</b>\n\n{update.message.text}"
            await context.bot.send_message(chat_id=user_id, text=reply_text, parse_mode="HTML")
            await update.message.reply_text("✅ Javobingiz foydalanuvchiga muvaffaqiyatli yetkazildi!")
        except Exception as e:
            await update.message.reply_text(f"❌ Javobni yuborishda xatolik (Foydalanuvchi botni bloklagan bo'lishi mumkin): {e}")
    else:
        await update.message.reply_text(
            "⚠️ Xatolik: Foydalanuvchi ID-si aniqlanmadi!\n"
            "Iltimos, faqat bot yuborgan asosiy ma'lumotlar xabariga (yoki rasmga) 'Reply' qilib javob yozing."
        )

def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio),
                CommandHandler("start", start),
            ],
            PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
                CommandHandler("start", start),
            ],
            DISTRICT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_district),
                CommandHandler("start", start),
            ],
            TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_text),
                CommandHandler("start", start),
            ],
            FILE: [
                MessageHandler(filters.ALL & ~filters.COMMAND, get_file),
                CommandHandler("skip", skip_file),
                CommandHandler("start", start),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv)
    
    # Admin xabarlarini tutuvchi handler har doim ConversationHandler'dan pastda bo'lishi shart
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_reply_handler))

    print("✅ Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
