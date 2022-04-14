from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")

db_user = env.str("DB_USER")
db_password = env.str("DB_PASSWORD")
db_name = env.str("DB_NAME")
