from typing import TypedDict, Optional

from .users import User
from .teams import Team


class Application(TypedDict, total=False):
    id: int
    name: str
    icon: Optional[str]
    description: str
    rpc_origins: str
    bot_public: bool
    bot_require_code_grant: bool
    terms_of_service_url: str
    privacy_policy_url: str
    owner: User
    summary: str
    verify_key: str
    team: Team
    guild_id: int
    primary_sku_id: int
    slug: str
    cover_image: str
    flags: int
    tags: str
    install_params: str
    custom_install_url: str