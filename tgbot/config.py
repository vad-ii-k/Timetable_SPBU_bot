from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")

PG_USER = env.str("PG_USER")
PG_PASSWORD = env.str("PG_PASSWORD")
PG_HOST = env.str("PG_HOST")
PG_PORT = env.str("PG_PORT")
PG_NAME = env.str("PG_NAME")

REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.int("REDIS_PORT")
REDIS_PASSWORD = env.str("REDIS_PASSWORD")

PROXY_LOGIN = env.str("PROXY_LOGIN")
PROXY_PASSWORD = env.str("PROXY_PASSWORD")
PROXY_IPS = ['154.16.150.112:45785', '194.233.150.56:45785', '185.33.85.246:45785']
