from urllib import request
from django import forms
from .models import Post
from django.core.exceptions import ValidationError

class PostCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(PostCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ["title", "content"]

    # Note: self.instance is according to model fields? 
    def clean(self):
        if not self.request.user.is_authenticated:
            raise ValidationError("You must be signed in to create a post")
        self.instance.author = self.request.user
        return self.cleaned_data

class PostDeleteForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance")
        super(PostDeleteForm, self).__init__(*args, **kwargs)

    def save(self):
        print(self.instance, "hell")
        self.instance.delete()

class PostUpdateForm(forms.ModelForm):

    class Meta:
        model= Post
        fields = ["title", "content"]

   
    
