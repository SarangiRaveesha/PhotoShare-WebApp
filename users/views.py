from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User # Built-in Django User model (username, password)
from django.contrib.auth import logout, login, authenticate # login() → log user in logout() → log user out authenticate() → check username & password
from django.contrib.auth.decorators import login_required # Only logged-in users can access certain functions
from django.contrib import messages # Show messages like Login successful, Error occurred

# Import database models
from .models import FriendRequest, Notification
from photos.models import Photo, PhotoTag, Comment

#creates a notification
def create_notification(recipient, actor, message, url=''):
    if recipient and actor == recipient:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        message=message,
        url=url
    )


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        bio = request.POST.get('bio', '').strip()
        avatar = request.FILES.get('avatar')

        if not username or not password1 or not password2:
            messages.error(request, 'All fields are required.')
            return render(request, 'users/register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'users/register.html')

        user = User.objects.create_user(username=username, password=password1)

        user.profile.bio = bio
        if avatar:
            user.profile.avatar = avatar
        user.profile.save()

        login(request, user)
        return redirect('feed')

    return render(request, 'users/register.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('feed')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('feed')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    return render(request, 'users/notifications.html', {'notifications': notifications})


@login_required
def open_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()

    if notification.url:
        return redirect(notification.url)

    return redirect('notifications')


@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    viewer = request.user

    is_own_profile = viewer == profile_user
    is_friend = False

    if not is_own_profile:
        is_friend = viewer.profile in profile_user.profile.friends.all()

    if request.method == 'POST' and is_own_profile:
        avatar = request.FILES.get('avatar')
        bio = request.POST.get('bio', '').strip()

        if avatar:
            profile_user.profile.avatar = avatar
        profile_user.profile.bio = bio
        profile_user.profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile', username=profile_user.username)

    if is_own_profile:
        photos = Photo.objects.filter(author=profile_user).order_by('-created_at')
    elif is_friend:
        photos = Photo.objects.filter(
            author=profile_user,
            visibility__in=['public', 'friends']
        ).order_by('-created_at')
    else:
        photos = Photo.objects.filter(
            author=profile_user,
            visibility='public'
        ).order_by('-created_at')

    if is_own_profile:
        tagged_photos = Photo.objects.filter(tags__user=profile_user).exclude(author=profile_user).distinct()
    elif is_friend:
        tagged_photos = Photo.objects.filter(
            tags__user=profile_user
        ).exclude(author=profile_user).filter(
            visibility__in=['public', 'friends']
        ).distinct()
    else:
        tagged_photos = Photo.objects.filter(
            tags__user=profile_user,
            visibility='public'
        ).exclude(author=profile_user).distinct()

    sent_request = FriendRequest.objects.filter(sender=viewer, receiver=profile_user).first() if not is_own_profile else None
    received_request = FriendRequest.objects.filter(sender=profile_user, receiver=viewer).first() if not is_own_profile else None

    profile_friends = profile_user.profile.friends.select_related('user').all()
    viewer_friend_ids = set(viewer.profile.friends.values_list('id', flat=True))

    friend_cards = []
    for friend_profile in profile_friends:
        if friend_profile.user == viewer:
            relation_state = 'you'
        elif friend_profile.id in viewer_friend_ids:
            relation_state = 'mutual'
        else:
            has_sent = FriendRequest.objects.filter(sender=viewer, receiver=friend_profile.user).exists()
            has_received = FriendRequest.objects.filter(sender=friend_profile.user, receiver=viewer).exists()

            if has_sent:
                relation_state = 'sent'
            elif has_received:
                relation_state = 'received'
            else:
                relation_state = 'not_friend'

        friend_cards.append({
            'profile': friend_profile,
            'relation_state': relation_state,
        })

    friends_count = len(friend_cards)

    # This is what you wanted from the screenshots:
    # 1 if viewer and profile owner are friends, otherwise 0
    connection_with_you = 0
    if is_friend:
        connection_with_you = 1

    context = {
        'profile_user': profile_user,
        'photos': photos,
        'tagged_photos': tagged_photos,
        'is_own_profile': is_own_profile,
        'is_friend': is_friend,
        'sent_request': sent_request,
        'received_request': received_request,
        'friend_cards': friend_cards,
        'friends_count': friends_count,
        'connection_with_you': connection_with_you,
    }
    return render(request, 'photos/profile.html', context)


@login_required
def send_friend_request(request, username):
    receiver = get_object_or_404(User, username=username)

    if receiver == request.user:
        messages.error(request, "You can't send a friend request to yourself.")
        return redirect('profile', username=receiver.username)

    if request.user.profile in receiver.profile.friends.all():
        messages.info(request, 'You are already friends.')
        return redirect('profile', username=receiver.username)

    existing = FriendRequest.objects.filter(sender=request.user, receiver=receiver).first()
    reverse_existing = FriendRequest.objects.filter(sender=receiver, receiver=request.user).first()

    if existing:
        messages.info(request, 'Friend request already sent.')
    elif reverse_existing:
        messages.info(request, 'This user already sent you a friend request. Accept it.')
    else:
        FriendRequest.objects.create(sender=request.user, receiver=receiver)
        create_notification(
            recipient=receiver,
            actor=request.user,
            message=f"{request.user.username} sent you a friend request.",
            url=f"/users/{request.user.username}/"
        )
        messages.success(request, 'Friend request sent.')

    return redirect('profile', username=receiver.username)


@login_required
def accept_friend_request(request, username):
    sender = get_object_or_404(User, username=username)
    friend_request = get_object_or_404(FriendRequest, sender=sender, receiver=request.user)

    request.user.profile.friends.add(sender.profile)
    sender.profile.friends.add(request.user.profile)
    friend_request.delete()

    create_notification(
        recipient=sender,
        actor=request.user,
        message=f"{request.user.username} accepted your friend request.",
        url=f"/users/{request.user.username}/"
    )

    messages.success(request, 'Friend request accepted.')
    return redirect('profile', username=sender.username)


@login_required
def remove_friend(request, username):
    other_user = get_object_or_404(User, username=username)

    request.user.profile.friends.remove(other_user.profile)
    other_user.profile.friends.remove(request.user.profile)

    FriendRequest.objects.filter(sender=request.user, receiver=other_user).delete()
    FriendRequest.objects.filter(sender=other_user, receiver=request.user).delete()

    messages.success(request, 'Friend removed.')
    return redirect('profile', username=other_user.username)


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        username = user.username
        friend_profiles = list(user.profile.friends.all())

        for friend_profile in friend_profiles:
            create_notification(
                recipient=friend_profile.user,
                actor=None,
                message=f"{username} deleted their account."
            )

        Comment.objects.filter(author=user).update(author=None)

        for tag in PhotoTag.objects.filter(user=user):
            tag.user = None
            tag.save()

        FriendRequest.objects.filter(sender=user).delete()
        FriendRequest.objects.filter(receiver=user).delete()

        for friend_profile in friend_profiles:
            friend_profile.friends.remove(user.profile)

        logout(request)
        user.delete()

        messages.success(request, 'Your account was deleted successfully.')
        return redirect('login')

    return render(request, 'users/delete_account.html')


def user_logout(request):
    logout(request)
    return redirect('login')
