from abc import ABC, abstractmethod
from typing import *

from content import Post
from model import BlogModel
from customExceptions import *
from followListener import setup_follow_event
from event import Event

listener = Event()
setup_follow_event(listener)

class BaseUser(ABC):
    """Abstract class for a user

    username: str -> username of the user
    password: str -> password of the user
    email: str -> email of the user
    user_id: int -> id of the user
    """
    def __init__(self, username: str, password: str = None, email: str = None, id: int = None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


    def set_id(self, user_id) -> None:
        if type(user_id) != int:
            raise TypeError("Tipo inválido de id. Ids devem ser inteiros.")
        self.id = user_id

    def get_id(self) -> int:
        """Get the id of the user"""
        return self.id

    def get_username(self) -> str:
        """Get the username of the user"""
        return self.username

    def get_email(self) -> str:
        """Get the email of the user"""
        return self.email

    # @abstractmethod
    # def register(self, username: str, password: str, email: str) -> None:
    #     """Register a user"""
    #     pass

    # @abstractmethod
    # def login(self, username: str, password: str) -> bool:
    #     """Login a user"""      
    #     pass

class User(BaseUser):
    """A user of the system
    """
    def __init__(self,
                 username: str,
                 password: str = None,
                 email: str = None,
                 id: int = None,
                 posts: List[int] = None, 
                 followers: List[int] = None,
                 following: List[int] = None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.__posts = posts if posts is not None else []
        self.__followers = followers if followers is not None else []
        self.__following = following if following is not None else []

    def get_posts(self) -> List[int]:
        """Get the posts of the user"""
        return self.__posts

    def get_followers(self) -> List[int]:
        """Get the followers of the user"""
        id_self = self.get_id()
        follower_list = BlogModel().get_followers_user(id_self)
        self.__followers = [user for user in follower_list]
        return self.__followers

    def get_following(self) -> List[int]:
        """Get the following of the user"""
        id_self = self.get_id()
        following_list = BlogModel().get_following_user(id_self)
        self.__following = [user for user in following_list]
        return self.__following

    def get_liked_posts(self) -> List[int]:
        """Get the liked posts of the user"""
        id_self = self.get_id()
        liked_posts = BlogModel().get_all_liked_posts_by_user(id_self)
        return liked_posts

    def like(self, post_id: int) -> None:
        """Like a post"""
        if not BlogModel().check_if_post_in_db(post_id):
            raise InvalidPostException()

        elif BlogModel().check_if_post_already_liked(self.get_id(), post_id):
            raise AlreadyLiked()

        else:
            BlogModel().like(self.get_id(), post_id)

    def unlike(self, post_id: int) -> None:
        """Unlike a post"""
        if not BlogModel().check_if_post_in_db(post_id):
            raise InvalidPostException()

        elif not BlogModel().check_if_post_already_liked(self.get_id(), post_id):
            raise AlreadyNotLiked()
        else:
            BlogModel().unlike(self.get_id(), post_id)


    def follow(self, followee_id: int) -> None:
        """Follow a user"""
        if not BlogModel().check_if_user_in_db(followee_id):
            raise InvalidUserException()

        elif followee_id == self.get_id():
            raise CannotFollowSelf()

        elif followee_id in self.get_following():
            raise AlreadyFollowing()
        else:
            id_self = self.get_id()
            BlogModel().follow(id_self, followee_id)
            listener.post_event("follow")

    def unfollow(self, followee_id: int) -> None:
        """Unfollow a user"""

        if not BlogModel().check_if_user_in_db(followee_id):
            raise InvalidUserException()

        if followee_id == self.get_id():
            raise CannotUnfollowSelf()

        if followee_id not in self.get_following():
            raise AlreadyNotFollowing()

        id_self = self.get_id()
        BlogModel().unfollow(id_self, followee_id)
        pass

class Moderator(BaseUser):
    """A moderator of the system"""
    def __init__(self,
                 username: str,
                 password: str = None,
                 email: str = None,
                 id: int = None):
        self.__id = id
        self.__username = username
        self.__password = password
        self.__email = email

    def delete_post(self, post_id: int) -> None:
        """Delete a post"""
        if not BlogModel().check_if_post_in_db(post_id):
            raise InvalidPostException()
        else:
            BlogModel().delete_post(post_id)

    def ban_user(self, banned_user_id: int) -> None:
        """Ban a user"""
        if not BlogModel().check_if_user_in_db(banned_user_id):
            raise InvalidUserException()
        elif BlogModel().check_if_user_is_banned(banned_user_id):
            raise AlreadyBanned()
        else:
            BlogModel().ban_user(self.__id, banned_user_id)

    def unban_user(self, unbanned_user_id: int) -> None:
        """Unban a user"""
        if not BlogModel().check_if_user_in_db(unbanned_user_id):
            raise InvalidUserException()
        elif not BlogModel().check_if_user_is_banned(unbanned_user_id):
            raise AlreadyUnbanned()
        else:
            BlogModel().unban_user(self.__id, unbanned_user_id)

class UserFactory:
    """Factory class for users"""
    @staticmethod
    def create_user(type_: str, username: str, id:int):
        """Create a user"""
        if type_ == 'USER':
            return User(username,
                             id)
        elif type_ == 'MODERATOR':
            return Moderator(username,
                             id)
        else:
            raise ValueError(f'User type {type_} is not valid.')
