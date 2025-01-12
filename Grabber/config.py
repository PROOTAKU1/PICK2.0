class Config(object):
    LOGGER = True

    # Owner ID (Main Admin)
    OWNER_ID = "5909658683"

    # List of Sudo Users (Only these users can add/remove other sudo users)
    sudo_users = ["5909658683", "8019277081", "7590975069", "7430528632"]  # Only these users can add/remove sudo users

    # Telegram Bot Details
    TOKEN = "7952058734:AAGzkkbQIVFlLQMHQZ9-z6R_tyicRW5ZUis"
    GROUP_ID = -1002399822734
    SUPPORT_CHAT = "WH_SUPPORT_GC"
    UPDATE_CHAT = "iamvillain77"
    BOT_USERNAME = "bot"
    CHARA_CHANNEL_ID = "-1002339477315"

    # MongoDB Connection URL
    mongo_url = "mongodb+srv://TEAMBABY01:UTTAMRATHORE09@cluster0.vmjl9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # Photo URLs for bot profile or other use
    PHOTO_URL = ["https://files.catbox.moe/wy70cl.jpg", "https://files.catbox.moe/wy70cl.jpg"]

    # API Credentials (for additional features if any)
    api_id = "24061032"
    api_hash = "5ad029547f2eeb5a0b68b05d0db713be"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
