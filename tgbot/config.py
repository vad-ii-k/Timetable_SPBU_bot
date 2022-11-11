""" Setting configs for the bot from environment variables """
from dataclasses import dataclass

from aiogram import Bot
from environs import Env


@dataclass(slots=True, frozen=True)
class DbConfig:
    """ Postgres database config """
    host: str
    """ Host """
    port: int
    """ Port """
    password: str
    """ User password """
    user: str
    """ User name """
    database: str
    """ Database name """
    are_groups_collected: bool
    """
    If false, then groups will be collected for the search function by group name
    
    **Need to set to True after the first run in ./../.env**
    """

    @property
    def connection_url(self) -> str:
        """
        Postgresql db url
        :return: url for connecting to the database
        """
        pg_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        return pg_url


@dataclass(slots=True, frozen=True)
class RedisConfig:
    """ Redis data store config """
    host: str
    """ Host """
    port: int
    """ Port """
    password: str
    """ Password """


@dataclass(slots=True, frozen=True)
class TgBot:
    """ Telegram bot config """
    token: str
    """ The token for bot from BotFather """
    admin_ids: list[int]
    """ Telegram admin IDs """


@dataclass(slots=True, frozen=True)
class Proxy:
    """ Proxy config """
    login: str
    """ Login for proxies """
    password: str
    """ Password for proxies """
    ips: list[str]
    """ List of IP addresses for proxies """


@dataclass(slots=True, frozen=True)
class Config:
    """ Combining config for the program """
    tg_bot: TgBot
    """ Telegram bot config """
    database: DbConfig
    """ Postgres database config """
    redis: RedisConfig
    """ Redis data store config """
    proxy: Proxy
    """ Proxy config """


def load_config(path: str = None) -> Config:
    """ Loading and installing configs from environment variables
    :param path: path to .env
    :return: Config object
    """
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS")))
        ),
        database=DbConfig(
            host=env.str('DB_HOST'),
            port=env.int('DB_PORT'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME'),
            are_groups_collected=env.bool('ARE_GROUPS_COLLECTED'),
        ),
        redis=RedisConfig(
            host=env.str('REDIS_HOST'),
            port=env.int('REDIS_PORT'),
            password=env.str('REDIS_PASSWORD'),
        ),
        proxy=Proxy(
            login=env.str('PROXY_LOGIN'),
            password=env.str('PROXY_PASSWORD'),
            ips=list(map(str, env.list("PROXY_IPS"))),
        )
    )


app_config = load_config(".env")
bot = Bot(token=app_config.tg_bot.token, parse_mode='HTML')
