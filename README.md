# PhotoShare-WebApp

## Overview
PhotoShare is a full-featured Django web application that allows users to:
- Upload and share photos with privacy controls
- Connect with friends through a friend request system
- Engage with photos through likes, comments, and emoji reactions
- Tag friends in photos and mention other users
- Receive real-time notifications for all activities
- Manage personal profiles with bios and avatars

## Technology Stack
- Backend: Django 6.0.4
- Database: SQLite3
- Frontend: HTML + Bootstrap 5.3
- Language composition: 52% Python, 48% HTML

## Features
### 📷 Photo Management
- Upload photos with captions
- Edit photo details and re-upload images
- Delete photos from your profile
- Three privacy levels: Public, Friends, Private
- Photo tagging system to tag friends in images

### 💬 Social Interactions
- **Comments**: Add comments to photos with nested replies
- **Likes**: Like/unlike photos with unique constraint per user
- **Reactions**: React to comments with emoji (😊, 👍, ❤️, etc.)
- **Mentions**: Tag other users with @username in comments
- **Notifications**: Real-time notifications for all interactions

### Friend System
- Send friend requests to other users
- Accept or reject friend requests
- View friend profiles with mutual connection indicators
- Remove friends from your network
- See friends' photos based on privacy settings

### User Profiles
- Customizable profile with bio and avatar
- View personal photos and tagged photos
- Display friend connections
- Show profile statistics (friend count, post count)
- Account deletion with data cleanup

### Notifications
- Friend request notifications
- Photo upload notifications
- Photo like notifications
- Comment and reply notifications
- User mention notifications
- Read/unread notification tracking

## Models
### User
- Fields: username, email, password

### Photo
- Fields: title, image, description, uploaded_at, user (ForeignKey)

### Comment
- Fields: content, user (ForeignKey), photo (ForeignKey), created_at

### Profile
- Fields: user (OneToOneField), bio, profile_picture

## Views
- HomeView: Displays all photos
- LoginView: Handles user login
- LogoutView: Logs out user
- RegistrationView: Handles user registration
- PhotoDetailView: Displays individual photo details
- UserProfileView: Displays user profile and their photos

## URLs
- `/`: Home page
- `/login/`: Login page
- `/logout/`: Logout route
- `/register/`: Registration page
- `/photo/<id>/`: Photo detail view
- `/profile/<username>/`: User profile view

## Templates
- `home.html`: Main page layout displaying photos
- `login.html`: Login form
- `register.html`: Registration form
- `photo_detail.html`: Display photo detail and comments
- `profile.html`: User profile page

## Setup Instructions

### Prerequisites
- Python 
- Django 

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/SarangiRaveesha/PhotoShare-WebApp.git
   
2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv\Scripts\activate

3. Install dependencies
   ```bash
   pip install django
   pip install pillow

4. Run migrations
   ```bash
   python manage.py migrate

5. Run the development server
   ```bash
   python manage.py runserver

6. Access the application
   Open browser: http://127.0.0.1:8000/

   
