from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
)
from django.contrib.auth import get_user_model


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = {
            'first_name', 'last_name', 'email'
        }


class CustomUserChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(
        label=(""),
        help_text=(
            'Пароли хранятся в зашифрованном виде, поэтому нет возможности '
            'посмотреть пароль этого пользователя, но вы можете изменить его'
            'используя <a href="/auth/password_change/">эту форму</a>.'
        ),
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = {
            'first_name', 'last_name', 'email', 'username'
        }
