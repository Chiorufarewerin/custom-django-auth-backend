from typing import Optional, Type

from .dto import UserDTO
from .exceptions import UnavailbleException, AuthException
from .settings import LOGGER_NAME, DEFAULT_USERNAME_PREFIX
from .logging import logger


class BasicAuthBackend:
    USERNAME_PREFIX = DEFAULT_USERNAME_PREFIX

    def get_user_by_login(self, username: str, password: str) -> UserDTO:
        """Тут должна быть логика получения пользователя"""

        raise NotImplementedError

    def get_user_model(self) -> Type:
        try:
            from django.contrib.auth.models import User
        except Exception:
            logger.exception('Не удалось импортировать модель User')
            raise

    def get_prefixed_username(self, username: str) -> str:
        return f'{self.USERNAME_PREFIX}{username}'

    def get_user_by_login_exists(self, username: str, password: str) -> Optional['User']:
        user = self.get_user_model().objects.filter(username=self.get_prefixed_username(username)).first() 
        if not user:
            return None
        if user.check_password(password):
            return user
        return None

    def get_and_update_user(self, username: str, password: str, user_dto: UserDTO) -> 'User':
        user, _ = self.get_user_model().objects.update_or_create(username=self.get_prefixed_username(username),
                                                defaults=user_dto.params)
        if not user.check_password(password):
            user.set_password(password)
            user.save()
        return user

    def authenticate(self, request, username: str, password: str) -> Optional['User']:
        if username is None or password is None:
            return None
        try:
            user_dto = self.get_user_by_login(username, password)
        except UnavailbleException:
            return self.get_user_by_login_exists(username, password)
        except AuthException:
            return None
        except Exception:
            logger.exception('Ошибка получения пользователя')
            return None
        return self.get_and_update_user(username, password, user_dto)
