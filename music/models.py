import magic
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.core.exceptions import ValidationError


def validate_file_size(value):
    max_size_mb = 10  # для картинок
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Максимальний розмір файлу — {max_size_mb}MB.")

def validate_audio_size(value):
    max_size_mb = 50  # для аудіо
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Максимальний розмір файлу — {max_size_mb}MB.")

def validate_audio_mimetype(value):
    valid_mime_types = ['audio/mpeg', 'audio/wav', 'audio/x-wav']
    file_mime = magic.from_buffer(value.read(2048), mime=True)
    value.seek(0)  # повернути курсор на початок файлу
    if file_mime not in valid_mime_types:
        raise ValidationError("Файл не є справжнім аудіофайлом (mp3/wav).")


class CustomUser(AbstractUser):
    ARTIST_STATUS_CHOICES = [
        ('none', 'Not requested'),
        ('pending', 'Pending approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    is_artist = models.BooleanField(default=False)  # True only when approved
    is_viewer = models.BooleanField(default=True)
    artist_status = models.CharField(
        max_length=10,
        choices=ARTIST_STATUS_CHOICES,
        default='none'
    )


class ArtistProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_artist': True},
        related_name='artist_profile'
    )

    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='artist_profiles/', blank=True, null=True,
        validators=[validate_file_size]
    )

    social_media = models.URLField(blank=True, null=True)
    spotify_link = models.URLField(blank=True, null=True)
    soundcloud_link = models.URLField(blank=True, null=True)
    telegram_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Artist Profile: {self.user.username}"


class Album(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    cover = models.ImageField(upload_to='album_covers/', validators=[validate_file_size])
    release_date = models.DateField()

    def __str__(self):
        return self.title


class Track(models.Model):
    album = models.ForeignKey(
        'Album',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='tracks',
        verbose_name="Album"
    )
    title = models.CharField(max_length=255, verbose_name="Track Title")
    audio_file = models.FileField(
        upload_to='tracks/',
        storage=RawMediaCloudinaryStorage(),
        validators=[
            FileExtensionValidator(allowed_extensions=['mp3', 'wav']),
            validate_audio_size,
            validate_audio_mimetype,
        ],
        verbose_name="Audio File"
    )
    description = models.TextField(blank=True, verbose_name="Track Description")

    featuring = models.ManyToManyField(
        ArtistProfile,
        blank=True,
        related_name='featured_tracks',
        verbose_name="Featuring artists"
    )

    class Meta:
        verbose_name = "Track"
        verbose_name_plural = "Tracks"

    def __str__(self):
        return self.title


class AlbumReview(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='reviews')
    custom_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='album_reviews'
    )
    review = models.TextField()
    rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    review_date = models.DateField()


class TrackComment(models.Model):
    track = models.ForeignKey(
        'Track',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name="Track"
    )
    custom_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='track_comments'
    )
    comment = models.TextField()
    comment_date = models.DateField()