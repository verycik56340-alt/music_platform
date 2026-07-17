from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, AlbumReview, TrackComment


class ViewerCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class ArtistCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_artist = False          # НЕ артист, пока не одобрят
        user.is_viewer = True
        user.artist_status = 'pending'  # ждёт одобрения
        if commit:
            user.save()
        return user


class AlbumReviewForm(forms.ModelForm):
    class Meta:
        model = AlbumReview
        fields = ['review', 'rating']
        widgets = {
            'review': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your review...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }


class TrackCommentForm(forms.ModelForm):
    class Meta:
        model = TrackComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Your comment...'}),
        }