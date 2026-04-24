# PhotoShare-WebApp

## Overview
PhotoShare-WebApp is a Django-based photo sharing application that allows users to upload, share, and manage their photos in a user-friendly interface.

## Features
- User authentication (registration, login, logout)
- Photo upload and management
- Commenting on photos
- Like functionality for photos
- User profiles with their photo collections

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
- Python 3.x
- Django 3.x or higher

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/SarangiRaveesha/PhotoShare-WebApp.git
