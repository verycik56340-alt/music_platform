from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ArtistProfile, Album, Track, AlbumReview, TrackComment, CustomUser


class TrackInline(admin.TabularInline):
    model = Track
    extra = 1


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'social_media', 'spotify_link')
    search_fields = ('user__username',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date')
    list_filter = ('release_date', 'artist')
    search_fields = ('title', 'artist__user__username')
    inlines = [TrackInline]


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'album')
    list_filter = ('album',)
    search_fields = ('title', 'album__title')


@admin.register(AlbumReview)
class AlbumReviewAdmin(admin.ModelAdmin):
    list_display = ('album', 'custom_user', 'rating', 'review_date')
    list_filter = ('rating', 'review_date')
    search_fields = ('album__title', 'custom_user__username')


@admin.register(TrackComment)
class TrackCommentAdmin(admin.ModelAdmin):
    list_display = ('track', 'custom_user', 'comment_date')
    list_filter = ('comment_date',)
    search_fields = ('track__title', 'custom_user__username')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # показывает ВСЕХ пользователей (viewer + artist + pending) — фильтруй справа
    list_display = ('username', 'email', 'artist_status', 'is_artist', 'is_staff', 'date_joined')
    list_filter = ('artist_status', 'is_artist', 'is_staff')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('is_artist', 'is_viewer', 'artist_status')}),
    )
    actions = ['approve_artists', 'reject_artists']

    def approve_artists(self, request, queryset):
        updated = 0
        for user in queryset:
            if user.artist_status == 'pending':
                user.is_artist = True
                user.artist_status = 'approved'
                user.save()
                ArtistProfile.objects.get_or_create(user=user)
                updated += 1
        self.message_user(request, f"{updated} user(s) approved as artist.")
    approve_artists.short_description = "Approve selected users as artists"

    def reject_artists(self, request, queryset):
        updated = queryset.filter(artist_status='pending').update(artist_status='rejected')
        self.message_user(request, f"{updated} user(s) rejected.")
    reject_artists.short_description = "Reject selected artist applications"