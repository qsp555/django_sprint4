from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Post, Comment

User = get_user_model()


class UserCreateForm(UserCreationForm):
    """Форма регистрации пользователя"""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'password1', 'password2')


class UserEditForm(UserChangeForm):
    """Форма редактирования профиля"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'location', 'category', 'image']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'text': forms.Textarea(attrs={'rows': 5}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }