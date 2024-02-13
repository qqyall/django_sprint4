from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'location', 'category']
        widgets = {
            'text': forms.Textarea({'cols': '22', 'rows': '2'}),
            'pub_date': forms.DateTimeInput(
                format=('%Y-%m-%dT%H:%M'), attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea({'cols': '22', 'rows': '2'}),
        }
