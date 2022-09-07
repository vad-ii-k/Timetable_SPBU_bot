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
PROXY_IPS = ["45.15.163.149:5631", "45.137.40.120:8673", "192.153.171.90:6163", "154.85.125.74:6285"]
