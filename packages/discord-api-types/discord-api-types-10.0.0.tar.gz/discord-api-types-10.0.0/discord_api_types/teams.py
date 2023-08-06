from typing import TypedDict, Optional, List

from .users import User


class TeamMember(TypedDict, total=False):
    membership_state: int
    permissions: str
    team_id: int
    user: User

class Team(TypedDict, total=False):
    icon: Optional[str]
    id: int
    members: List[TeamMember]
    name: str
    owner_user_id: int