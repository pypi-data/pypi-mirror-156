from typing import TypedDict, Optional


class User(TypedDict, total=False):
    id: int
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: bool
    system: bool
    mfa_enabled: bool
    banner: Optional[str]
    accent_color: Optional[str]
    locale: Optional[str]
    verified: Optional[bool]
    email: Optional[str]
    flags: int
    premium_type: str
    public_flags: int