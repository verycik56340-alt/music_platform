from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import ArtistProfile, Album, Track, AlbumReview, TrackComment
from .forms import ViewerCreationForm, ArtistCreationForm, AlbumReviewForm, TrackCommentForm


def home(request):
    artists = ArtistProfile.objects.select_related('user').all()
    latest_albums = Album.objects.select_related('artist__user').order_by('-release_date')[:10]
    return render(request, 'home.html', {
        'artists': artists,
        'latest_albums': latest_albums,
    })


def artist_detail(request, pk):
    artist = get_object_or_404(ArtistProfile, pk=pk)
    albums = artist.albums.order_by('-release_date')
    tracks = Track.objects.filter(
        Q(album__artist=artist) | Q(featuring=artist)
    ).distinct().select_related('album').order_by('title')

    active_tab = request.GET.get('tab', 'albums')
    if active_tab not in ('albums', 'tracks'):
        active_tab = 'albums'

    return render(request, 'artist_detail.html', {
        'artist': artist,
        'albums': albums,
        'tracks': tracks,
        'active_tab': active_tab,
    })


def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk)
    tracks = album.tracks.all()

    form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AlbumReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.album = album
                review.custom_user = request.user
                review.review_date = timezone.now().date()
                review.save()
                form = AlbumReviewForm()  # пустая форма после успешной отправки
        else:
            form = AlbumReviewForm()

    reviews = album.reviews.select_related('custom_user').order_by('-review_date')

    return render(request, 'album_detail.html', {
        'album': album,
        'tracks': tracks,
        'reviews': reviews,
        'form': form,
    })


def track_detail(request, pk):
    track = get_object_or_404(Track, pk=pk)

    form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = TrackCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.track = track
                comment.custom_user = request.user
                comment.comment_date = timezone.now().date()
                comment.save()
                form = TrackCommentForm()  # пустая форма после успешной отправки
        else:
            form = TrackCommentForm()

    comments = track.comments.select_related('custom_user').order_by('-comment_date')

    return render(request, 'track_detail.html', {
        'track': track,
        'comments': comments,
        'form': form,
    })


def register_viewer(request):
    if request.method == 'POST':
        form = ViewerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = ViewerCreationForm()
    return render(request, 'register.html', {'form': form, 'title': 'Viewer Registration'})


def register_artist(request):
    if request.method == 'POST':
        form = ArtistCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'artist_pending.html')
    else:
        form = ArtistCreationForm()
    return render(request, 'register.html', {'form': form, 'title': 'Artist Registration'})