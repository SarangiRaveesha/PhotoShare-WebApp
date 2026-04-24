import re

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .models import Photo, PhotoTag, Comment, Like, Reaction
from users.models import Notification

#create_notification
def create_notification(recipient, actor, message, url=''):
    if recipient and actor == recipient:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        message=message,
        url=url
    )


def photo_feed_url(photo):
    return f"/#photo-{photo.id}"

#render_mentions
def render_mentions_html(text):
    escaped_text = escape(text or "")

    def replace_mention(match):
        username = match.group(1)
        if User.objects.filter(username=username).exists():
            return f'<a href="/users/{username}/" class="mention-link">@{username}</a>'
        return f'@{username}'

    rendered = re.sub(r'@([A-Za-z0-9_]+)', replace_mention, escaped_text)
    return mark_safe(rendered)


def notify_mentions(text, actor, photo):
    usernames = set(re.findall(r'@([A-Za-z0-9_]+)', text or ""))
    for username in usernames:
        try:
            mentioned_user = User.objects.get(username=username)
            create_notification(
                recipient=mentioned_user,
                actor=actor,
                message=f"{actor.username} mentioned you in a comment.",
                url=photo_feed_url(photo)
            )
        except User.DoesNotExist:
            continue


def can_view_photo(user, photo):
    if user.is_authenticated and photo.author_id == user.id:
        return True
    if photo.visibility == 'public':
        return True
    if not user.is_authenticated:
        return False
    if photo.visibility == 'friends':
        return user.profile in photo.author.profile.friends.all()
    return False


def mention_suggestions(request):
    query = request.GET.get('q', '').strip().lstrip('@')

    if not query:
        return JsonResponse({'results': []})

    users = User.objects.filter(username__istartswith=query).order_by('username')[:8]

    friend_user_ids = set()
    if request.user.is_authenticated:
        friend_user_ids = set(
            request.user.profile.friends.values_list('user_id', flat=True)
        )

    results = []
    for user in users:
        if request.user.is_authenticated and user.id == request.user.id:
            relation = 'You'
        elif user.id in friend_user_ids:
            relation = 'Friend'
        else:
            relation = 'Registered'

        avatar_url = ''
        if hasattr(user, 'profile') and user.profile.avatar:
            avatar_url = user.profile.avatar.url

        results.append({
            'username': user.username,
            'relation': relation,
            'avatar_url': avatar_url,
        })

    return JsonResponse({'results': results})


def get_comment_relation_label(current_user, comment_author_id, friend_user_ids):
    if not current_user.is_authenticated:
        return 'Registered'
    if comment_author_id == current_user.id:
        return 'Your Comment'
    if comment_author_id in friend_user_ids:
        return 'Friend'
    return 'Registered'


def attach_comment_flags(comment, current_user, friend_user_ids):
    comment.rendered_text = render_mentions_html(comment.text)
    comment.author_user_id = comment.author_id
    comment.can_edit = current_user.is_authenticated and (comment.author_id == current_user.id)
    comment.relation_label = get_comment_relation_label(current_user, comment.author_id, friend_user_ids)

    for reply in comment.replies.all():
        reply.rendered_text = render_mentions_html(reply.text)
        reply.author_user_id = reply.author_id
        reply.can_edit = current_user.is_authenticated and (reply.author_id == current_user.id)
        reply.relation_label = get_comment_relation_label(current_user, reply.author_id, friend_user_ids)


def feed(request):
    friend_user_ids = set()

    if request.user.is_authenticated:
        friend_user_ids = set(
            request.user.profile.friends.values_list('user_id', flat=True)
        )

        photos = Photo.objects.filter(
            Q(author=request.user) |
            Q(visibility='public') |
            Q(visibility='friends', author_id__in=friend_user_ids)
        ).distinct().order_by('-created_at')
    else:
        photos = Photo.objects.filter(visibility='public').order_by('-created_at')

    for photo in photos:
        photo.is_owner_post = request.user.is_authenticated and (photo.author_id == request.user.id)
        photo.is_friend_post = request.user.is_authenticated and (photo.author_id in friend_user_ids)

        top_level_comments = photo.comments.filter(parent__isnull=True).order_by('created_at')
        for comment in top_level_comments:
            attach_comment_flags(comment, request.user, friend_user_ids)

        photo.top_level_comments = top_level_comments

    return render(request, 'photos/feed.html', {'photos': photos})


@login_required
def upload_photo(request):
    friends = User.objects.filter(profile__in=request.user.profile.friends.all())

    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '').strip()
        visibility = request.POST.get('visibility', 'public')
        tag_ids = request.POST.getlist('tagged_users')

        if image:
            photo = Photo.objects.create(
                author=request.user,
                image=image,
                caption=caption,
                visibility=visibility
            )

            if visibility != 'private':
                friend_map = {str(friend.id): friend for friend in friends}
                for user_id in tag_ids:
                    if user_id in friend_map:
                        tagged_user = friend_map[user_id]
                        PhotoTag.objects.create(
                            photo=photo,
                            user=tagged_user,
                            username_snapshot=tagged_user.username
                        )
                        create_notification(
                            recipient=tagged_user,
                            actor=request.user,
                            message=f"{request.user.username} tagged you in a photo.",
                            url=photo_feed_url(photo)
                        )

            for friend in friends:
                create_notification(
                    recipient=friend,
                    actor=request.user,
                    message=f"{request.user.username} uploaded a new photo.",
                    url=photo_feed_url(photo)
                )

            return redirect('feed')

    return render(request, 'photos/upload.html', {'friends': friends})


@login_required
def edit_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id, author=request.user)
    friends = User.objects.filter(profile__in=request.user.profile.friends.all())
    tagged_ids = list(photo.tags.exclude(user=None).values_list('user_id', flat=True))

    if request.method == 'POST':
        new_image = request.FILES.get('image')
        caption = request.POST.get('caption', '').strip()
        visibility = request.POST.get('visibility', 'public')
        tag_ids = request.POST.getlist('tagged_users')

        if new_image:
            photo.image = new_image

        photo.caption = caption
        photo.visibility = visibility
        photo.save()

        photo.tags.all().delete()

        if visibility != 'private':
            friend_map = {str(friend.id): friend for friend in friends}
            for user_id in tag_ids:
                if user_id in friend_map:
                    tagged_user = friend_map[user_id]
                    PhotoTag.objects.create(
                        photo=photo,
                        user=tagged_user,
                        username_snapshot=tagged_user.username
                    )

        messages.success(request, 'Post updated successfully.')
        return redirect('feed')

    return render(request, 'photos/edit_photo.html', {
        'photo': photo,
        'friends': friends,
        'tagged_ids': tagged_ids
    })


@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id, author=request.user)

    if request.method == 'POST':
        photo.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('feed')

    return render(request, 'photos/delete_photo.html', {'photo': photo})


@login_required
def toggle_like(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if not can_view_photo(request.user, photo):
        messages.error(request, 'You cannot like this photo.')
        return redirect('feed')

    like = Like.objects.filter(photo=photo, user=request.user)

    if like.exists():
        like.delete()
    else:
        Like.objects.create(photo=photo, user=request.user)
        create_notification(
            recipient=photo.author,
            actor=request.user,
            message=f"{request.user.username} liked your photo.",
            url=photo_feed_url(photo)
        )

    return redirect(photo_feed_url(photo))


@login_required
def add_comment(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if not can_view_photo(request.user, photo):
        messages.error(request, 'You cannot comment on this photo.')
        return redirect('feed')

    text = request.POST.get("text", '').strip()
    parent_id = request.POST.get("parent_id")

    parent = None
    if parent_id:
        parent = get_object_or_404(Comment, id=parent_id)

    if text:
        Comment.objects.create(
            photo=photo,
            author=request.user,
            text=text,
            parent=parent
        )

        notify_mentions(text, request.user, photo)

        if parent and parent.author:
            create_notification(
                recipient=parent.author,
                actor=request.user,
                message=f"{request.user.username} replied to your comment.",
                url=photo_feed_url(photo)
            )
        else:
            create_notification(
                recipient=photo.author,
                actor=request.user,
                message=f"{request.user.username} commented on your photo.",
                url=photo_feed_url(photo)
            )

    return redirect(photo_feed_url(photo))


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            comment.text = text
            comment.save()
            messages.success(request, 'Comment updated successfully.')

    return redirect(photo_feed_url(comment.photo))


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    photo_url = photo_feed_url(comment.photo)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')

    return redirect(photo_url)


@login_required
def react_comment(request, comment_id, emoji):
    comment = get_object_or_404(Comment, id=comment_id)

    reaction, created = Reaction.objects.get_or_create(
        comment=comment,
        user=request.user,
        emoji=emoji
    )

    if not created:
        reaction.delete()

    return redirect(photo_feed_url(comment.photo))


def user_logout(request):
    logout(request)
    return redirect('login')
