# i18n/messages.py

MESSAGES = {

    # ================= AUTH / REGISTRATION =================
    "auth.already_registered": {
        "uz": "Siz allaqachon ro'yxatdan o'tgansiz.",
        "ru": "Вы уже зарегистрированы."
    },
    "auth.not_verified_resent": {
        "uz": "Profil tasdiqlanmagan. Kod qayta yuborildi.",
        "ru": "Профиль не подтверждён. Код отправлен повторно."
    },
    "auth.register_success": {
        "uz": "Ro'yxatdan o'tildi. Emailga kod yuborildi.",
        "ru": "Регистрация прошла успешно. Код отправлен на email."
    },

    "auth.first_name_mismatch": {
        "uz": "Ism noto‘g‘ri kiritilgan",
        "ru": "Имя указано неверно"
    },
    "auth.last_name_mismatch": {
        "uz": "Familiya noto‘g‘ri kiritilgan",
        "ru": "Фамилия указана неверно"
    },
    "auth.middle_name_mismatch": {
        "uz": "Otasining ismi noto‘g‘ri kiritilgan",
        "ru": "Отчество указано неверно"
    },
    "auth.phone_mismatch": {
        "uz": "Telefon raqam mos kelmayapti",
        "ru": "Номер телефона не совпадает"
    },

    # ================= AUTH / ACTIVATION =================
    "auth.activation_success": {
        "uz": "Profil muvaffaqiyatli aktivlashtirildi. Xush kelibsiz!",
        "ru": "Профиль успешно активирован. Добро пожаловать!"
    },
    "auth.activation_code_invalid": {
        "uz": "Xato kod kiritildi.",
        "ru": "Неверный код."
    },
    "auth.activation_user_not_found": {
        "uz": "Foydalanuvchi topilmadi yoki allaqachon aktiv.",
        "ru": "Пользователь не найден или уже активирован."
    },
    "auth.activation_failed": {
        "uz": "Aktivatsiyada xatolik yuz berdi. Qayta urinib ko‘ring.",
        "ru": "Ошибка активации. Попробуйте снова."
    },

    # ================= AUTH / RESEND =================
    "auth.resend_success": {
        "uz": "Yangi aktivlashtirish kodi emailga yuborildi.",
        "ru": "Новый код активации отправлен на email."
    },
    "auth.resend_not_found": {
        "uz": "Foydalanuvchi topilmadi yoki allaqachon aktiv.",
        "ru": "Пользователь не найден или уже активирован."
    },
    "auth.resend_failed": {
        "uz": "Kodni qayta yuborishda xatolik yuz berdi.",
        "ru": "Ошибка повторной отправки кода."
    },

    # ================= AUTH / LOGOUT =================
    "auth.logout_success": {
        "uz": "Tizimdan chiqildi",
        "ru": "Вы вышли из системы"
    },

    # ================= COMMON =================
    "common.required_fields": {
        "uz": "Email va kod majburiy.",
        "ru": "Email и код обязательны."
    },
}
