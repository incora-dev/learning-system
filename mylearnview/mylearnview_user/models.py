from django.db import models
from django.contrib.auth.models import AbstractUser


type_of_users = (
    ('student', 'Student'),
    ('coursemanager', 'Coursemanager'),
)
type_of_expand = (
    ('read', 'Expand read'),
    ('r/n', 'Read and notes'),
    ('notes', 'Expand notes'),
)


class User(AbstractUser):

    email = models.EmailField(unique=True)

    user_type = models.CharField(
        max_length=25,
        choices=type_of_users)

    expand_type = models.CharField(
        max_length=25,
        choices=type_of_expand,
        default='r/n')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']

    def get_manager_permission(self):
        if self.user_type == 'coursemanager' or self.is_superuser:
            return True
        else:
            return False
