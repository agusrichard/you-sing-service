from typing import List

from app.models.user import User
from app.common.messages import USER_NOT_FOUND
from app.repositories.user import UserRepository
from app.common.exceptions import NotFoundException


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def follow(self, from_user: User, to_id: int):
        to_user = self.repository.get_by_id(to_id)
        if to_user is None:
            raise NotFoundException(USER_NOT_FOUND)

        self.repository.follow(from_user, to_user)

    def unfollow(self, from_user: User, to_id: int):
        to_user = self.repository.get_by_id(to_id)
        if to_user is None:
            raise NotFoundException(USER_NOT_FOUND)

        self.repository.unfollow(from_user, to_user)

    def get_followers(self, user_id: int, take: int = 10, skip: int = 0) -> List[dict]:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(USER_NOT_FOUND)

        users = user.get_followers(take, skip)
        return [user.to_dict() for user in users]

    def get_followed_users(
        self, user_id: int, take: int = 10, skip: int = 0
    ) -> List[dict]:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(USER_NOT_FOUND)

        users = user.get_followed_users(take, skip)
        return [user.to_dict() for user in users]

    def get_songs(self, user_id: int, take: int = 10, skip=0) -> List[dict]:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(USER_NOT_FOUND)

        songs = user.get_songs(take, skip)
        return [song.to_dict() for song in songs]
