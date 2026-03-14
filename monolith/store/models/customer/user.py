"""
User, UserProfile, UserRole, UserStatus, LoginSession models.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserRole(models.Model):
    """User role model for role-based access control."""
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_userrole'
        verbose_name = 'User Role'

    def __str__(self):
        return self.role_name

    def assign_role(self, user):
        user.role = self
        user.save()


class UserStatus(models.Model):
    """User status model for tracking account status."""
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_userstatus'
        verbose_name = 'User Status'

    def __str__(self):
        return self.status_name

    def change_status(self, user, new_status):
        user.status = new_status
        user.save()


class UserManager(BaseUserManager):
    """Custom manager for User model."""

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Base User model for authentication.
    Attributes: userId, username, password, email
    Methods: authenticate()
    """
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    groups = models.ManyToManyField(
        'auth.Group', related_name='base_user_set',
        related_query_name='base_user', blank=True,
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='base_user_set',
        related_query_name='base_user', blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(UserStatus, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'store_user'
        verbose_name = 'User'

    def __str__(self):
        return self.username

    def authenticate(self, password):
        return self.check_password(password)


class UserProfile(models.Model):
    """
    User profile model for additional user information.
    Attributes: profileId, address, avatar
    Methods: updateProfile()
    """
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True, null=True)
    avatar = models.URLField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_userprofile'
        verbose_name = 'User Profile'

    def __str__(self):
        return f"Profile of {self.user.username}"

    def update_profile(self):
        self.save()


class LoginSession(models.Model):
    """
    Login session model for tracking user sessions.
    Attributes: sessionId, loginTime
    Methods: logout()
    """
    session_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_sessions')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'store_loginsession'
        verbose_name = 'Login Session'

    def __str__(self):
        return f"Session {self.session_id} - {self.user}"

    def logout(self):
        self.is_active = False
        self.logout_time = timezone.now()
        self.save()
