from dataclasses import dataclass

from environs import Env


@dataclass(slots=True, frozen=True)
class DbConfig:
    host: str
    port: int
    password: str
    user: str
    database: str

    def get_connection_url(self):
        pg_uri = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        return pg_uri


@dataclass(slots=True, frozen=True)
class RedisConfig:
    host: str
    port: int
    password: str


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
    database: DbConfig
    redis: RedisConfig
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
        database=DbConfig(
            host=env.str('DB_HOST'),
            port=env.int('DB_PORT'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME'),
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
        ),
        misc=Miscellaneous()
    )


config: Config = load_config(".env")
