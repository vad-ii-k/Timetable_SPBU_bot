from dataclasses import dataclass

from environs import Env


@dataclass(slots=True, frozen=True)
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass(slots=True, frozen=True)
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass(slots=True, frozen=True)
class Proxy:
    login: str
    password: str
    ips: list[str]


@dataclass(slots=True, frozen=True)
class Miscellaneous:
    other_params: str = None


@dataclass(slots=True, frozen=True)
class Config:
    tg_bot: TgBot
    db: DbConfig
    proxy: Proxy
    misc: Miscellaneous


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        proxy=Proxy(
            login=env.str('PROXY_LOGIN'),
            password=env.str('PROXY_PASSWORD'),
            ips=list(map(str, env.list("PROXY_IPS"))),
        ),
        misc=Miscellaneous()
    )


config: Config = load_config(".env")
