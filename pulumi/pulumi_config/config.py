from pydantic import BaseModel, validator
from pydantic_yaml import parse_yaml_raw_as, to_yaml_str


class HomeBridgeConfig(BaseModel):
    image: str
    redirect_host: str
    redirect_prefix: str


class Config(BaseModel):
    homebridge: HomeBridgeConfig = HomeBridgeConfig()


class HomeslicePulumiYaml(BaseModel):
    c: Config = Config()
