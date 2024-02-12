from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'description': forms.Textarea({'cols': '22', 'rows': '5'}),
            'comment': forms.Textarea({'cols': '22', 'rows': '5'}),
        }
