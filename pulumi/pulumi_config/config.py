from pydantic import BaseModel

# FIXME: add validators

class HomeBridgeConfig(BaseModel):
    image: str
    redirect_host: str
    redirect_prefix: str
