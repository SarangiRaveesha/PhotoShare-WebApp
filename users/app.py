from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' #(BigAutoField -> a large auto-incrementing number)
    name = 'users'
