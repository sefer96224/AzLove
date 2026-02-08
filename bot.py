import os
import sqlite3

import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

telegram_api_key = os.environ.get("TELEGRAM_API_KEY", "PASTE_YOUR_TOKEN_HERE")

bot = telebot.TeleBot(telegram_api_key)

DB_PATH = "userdata.db"

SERVICES = [
    "Profil yarat",
    "Uyğun profillər",
    "Profilimi göstər",
    "Anketi yenilə",
    "Qaydalar",
]


def get_connection():
    return sqlite3.connect(DB_PATH)


with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            city TEXT,
            gender TEXT,
            interests TEXT,
            photo TEXT,
            liked_users TEXT
        )
        """
    )
    conn.commit()


user_data = {}


def ensure_session(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "name": None,
            "age": None,
            "city": None,
            "gender": None,
            "interests": None,
            "photo": None,
            "liked_users": [],
            "viewed_profiles": [],
        }


def save_user_data(user_id, data):
    with get_connection() as conn:
        cursor = conn.cursor()
        liked_users = ",".join(map(str, data.get("liked_users", [])))
        cursor.execute(
            """
            INSERT OR REPLACE INTO users (chat_id, name, age, city, gender, interests, photo, liked_users)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                data["name"],
                data["age"],
                data["city"],
                data["gender"],
                data.get("interests", ""),
                data.get("photo", ""),
                liked_users,
            ),
        )
        conn.commit()


def load_user_data(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE chat_id = ?", (user_id,))
        record = cursor.fetchone()

    if not record:
        return None

    liked_users = record[7].split(",") if record[7] else []
    return {
        "name": record[1],
        "age": record[2],
        "city": record[3],
        "gender": record[4],
        "interests": record[5],
        "photo": record[6],
        "liked_users": [int(item) for item in liked_users if item],
        "viewed_profiles": [],
    }


def build_services_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("Xidmətlər"),
        KeyboardButton("Uyğun profillər"),
    )
    markup.add(
        KeyboardButton("Profilim"),
        KeyboardButton("Anketimi yenilə"),
    )
    markup.add(KeyboardButton("Qaydalar"))
    return markup


def show_services(user_id):
    services_text = "\n".join([f"• {service}" for service in SERVICES])
    bot.send_message(user_id, f"Mövcud xidmətlər:\n{services_text}")


@bot.message_handler(commands=["start", "menu"])
def send_welcome(message):
    ensure_session(message.chat.id)
    bot.send_message(
        message.chat.id,
        "Mən sənə uyğun sevgi və ya dost tapmaqda kömək edəcəyəm. Bir neçə sual verim?",
        reply_markup=build_services_markup(),
    )
    bot.send_message(
        message.chat.id,
        "Başlamaq üçün 'Profil yarat' yaz və ya düymədən seç.",
    )


@bot.message_handler(commands=["services", "help"])
def services_command(message):
    show_services(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "Xidmətlər")
def services_button(message):
    show_services(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "Qaydalar")
def rules_button(message):
    bot.send_message(
        message.chat.id,
        "Qaydalar:\n"
        "• Bu xidmət 18+ istifadəçilər üçündür.\n"
        "• Profil məlumatları real olmalıdır.\n"
        "• Hörmətli ünsiyyət tələb olunur.",
    )


@bot.message_handler(func=lambda message: message.text in {"Profil yarat", "Anketimi yenilə"})
def handle_profile_start(message):
    ensure_session(message.chat.id)
    user_data[message.chat.id].update(
        {
            "name": None,
            "age": None,
            "city": None,
            "gender": None,
            "interests": None,
            "photo": None,
            "liked_users": user_data[message.chat.id].get("liked_users", []),
            "viewed_profiles": [],
        }
    )
    bot.send_message(message.chat.id, "Sənə necə müraciət edək? Adını yaz.")


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]["name"] is None)
def get_name(message):
    user_data[message.chat.id]["name"] = message.text.strip()
    bot.send_message(message.chat.id, "Neçə yaşın var?")


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]["age"] is None)
def get_age(message):
    if message.text.isdigit():
        age = int(message.text)
        if age < 18:
            bot.send_message(message.chat.id, "Bu xidmət yalnız 18+ istifadəçilər üçündür.")
            user_data.pop(message.chat.id, None)
        else:
            user_data[message.chat.id]["age"] = age
            bot.send_message(message.chat.id, "Hansı şəhərdə yaşayırsan?")
    else:
        bot.send_message(message.chat.id, "Zəhmət olmasa yaşını rəqəmlərlə yaz.")


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]["city"] is None)
def get_city(message):
    user_data[message.chat.id]["city"] = message.text.strip()
    bot.send_message(message.chat.id, "Cinsiyyətini seç 😊")

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Kişi"), KeyboardButton("Qadın"))
    bot.send_message(message.chat.id, "Zəhmət olmasa cinsiyyətini seç:", reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.chat.id in user_data
    and user_data[message.chat.id]["gender"] is None
    and message.text in ["Kişi", "Qadın"]
)
def handle_gender(message):
    user_data[message.chat.id]["gender"] = message.text
    bot.send_message(message.chat.id, "Özün və maraqların haqqında qısa məlumat yaz.")


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id]["interests"] is None)
def get_interests(message):
    user_data[message.chat.id]["interests"] = message.text
    bot.send_message(message.chat.id, "İndi mənə bir şəkil göndər.")


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    if message.chat.id not in user_data or user_data[message.chat.id]["photo"] is not None:
        return

    user_data[message.chat.id]["photo"] = message.photo[-1].file_id
    save_user_data(message.chat.id, user_data[message.chat.id])
    bot.send_message(
        message.chat.id,
        "Anketin hazırdır! İndi sənə uyğun profilləri göstərə bilərəm.",
        reply_markup=build_services_markup(),
    )


@bot.message_handler(func=lambda message: message.text == "Profilim")
def profile_button(message):
    user_profile = load_user_data(message.chat.id)
    if not user_profile:
        bot.send_message(message.chat.id, "Profil tapılmadı. Profil yaratmaq üçün 'Profil yarat' yaz.")
        return

    info = format_profile(user_profile)
    bot.send_message(message.chat.id, info, reply_markup=build_services_markup())
    if user_profile["photo"]:
        bot.send_photo(message.chat.id, user_profile["photo"])


@bot.message_handler(commands=["search"])
@bot.message_handler(func=lambda message: message.text == "Uyğun profillər")
def search_profiles(message):
    ensure_session(message.chat.id)
    if not load_user_data(message.chat.id):
        bot.send_message(message.chat.id, "Əvvəlcə profil yaratmalısan.", reply_markup=build_services_markup())
        return

    send_profiles_to_user(message.chat.id)


def format_profile(user):
    info = f"{user['name']}, {user['age']} yaş, {user['city']}, {user['gender']}"
    if user.get("interests"):
        info += f"\nMaraqlar: {user['interests']}"
    return info


def send_profiles_to_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT gender FROM users WHERE chat_id = ?", (user_id,))
        result = cursor.fetchone()
        if not result:
            bot.send_message(user_id, "Sistemdə profiliniz tapılmadı.")
            return

        user_gender = result[0]
        target_gender = "Qadın" if user_gender == "Kişi" else "Kişi"

        cursor.execute("SELECT * FROM users WHERE chat_id != ? AND gender = ?", (user_id, target_gender))
        all_users = cursor.fetchall()

    viewed_profiles = user_data[user_id].get("viewed_profiles", [])
    new_profiles = [user for user in all_users if user[0] not in viewed_profiles]

    if new_profiles:
        user = new_profiles[0]
        user_data[user_id]["viewed_profiles"].append(user[0])

        info = format_profile(
            {
                "name": user[1],
                "age": user[2],
                "city": user[3],
                "gender": user[4],
                "interests": user[5],
            }
        )

        bot.send_message(user_id, info)
        if user[6]:
            bot.send_photo(user_id, user[6])

        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("👍"), KeyboardButton("👎"))
        bot.send_message(user_id, "Bu profili bəyəndinmi?", reply_markup=markup)

        bot.register_next_step_handler_by_chat_id(user_id, handle_like_dislike, user[0])
    else:
        bot.send_message(user_id, "Anketlər bitdi. Daha sonra yenə yoxlaya bilərsən.")


def handle_like_dislike(message, liked_user_id):
    if message.text == "👍":
        user_data[message.chat.id]["liked_users"].append(liked_user_id)
        save_user_data(message.chat.id, user_data[message.chat.id])
        check_if_mutual_like(message.chat.id, liked_user_id)

    send_profiles_to_user(message.chat.id)


def check_if_mutual_like(user_id, liked_user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT liked_users FROM users WHERE chat_id = ?", (liked_user_id,))
        result = cursor.fetchone()

    if result and result[0]:
        liked_users = result[0].split(",")
        if str(user_id) in liked_users:
            bot.send_message(user_id, "🎉 Siz bir-birinizi bəyəndiniz! İndi danışa bilərsiniz.")
            bot.send_message(liked_user_id, "🎉 Siz bir-birinizi bəyəndiniz! İndi danışa bilərsiniz.")
            send_profile_to_user(user_id, liked_user_id)
            send_profile_to_user(liked_user_id, user_id)


def send_profile_to_user(user_id, profile_user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE chat_id = ?", (profile_user_id,))
        user = cursor.fetchone()

    if user:
        info = format_profile(
            {
                "name": user[1],
                "age": user[2],
                "city": user[3],
                "gender": user[4],
                "interests": user[5],
            }
        )
        bot.send_message(user_id, info)
        if user[6]:
            bot.send_photo(user_id, user[6])


@bot.message_handler(func=lambda message: message.text == "Profil yarat")
def profile_shortcut(message):
    handle_profile_start(message)


@bot.message_handler(func=lambda message: message.text == "Anketimi yenilə")
def refresh_shortcut(message):
    handle_profile_start(message)


@bot.message_handler(commands=["reset"])
def reset_profile(message):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE chat_id = ?", (message.chat.id,))
        conn.commit()
    user_data.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "Profil silindi. Yenidən başlamaq üçün 'Profil yarat' yaz.",
        reply_markup=ReplyKeyboardRemove(),
    )


bot.polling(non_stop=True)
