from django.db import models
from django.contrib.auth.models import PermissionsMixin , UserManager, AbstractBaseUser

# class Books(models.Model):
#     name = models.CharField(max_length=30)
#     description = models.CharField(max_length=255)

#     class Meta:
#         managed = True
#         db_table = 'books'


class NewUserManager(UserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('User must have a username')
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    description = models.TextField(max_length=150, blank=True, null=True)
    profile_picture = models.TextField(default='')
    rating = models.IntegerField(default=0)
    registration_date = models.DateField(blank=True, null=True)

    USERNAME_FIELD = 'username'

    objects =  NewUserManager()

    class Meta:
        managed = True
        db_table = 'custom_users'

class Moments(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(default='')
    publication_date = models.DateField()
    image = models.TextField(default='')
    id_author = models.ForeignKey('CustomUser', on_delete=models.CASCADE,  db_column='id_author', related_name='author_moment', default=1)

    class Meta:
        managed = True
        db_table = 'moments'

class Comments(models.Model):
    text = models.CharField(max_length=100)
    publication_date = models.DateField()
    id_author = models.ForeignKey('CustomUser', on_delete=models.CASCADE,  db_column='id_author', related_name='author_comment', default=1)
    id_moment = models.ForeignKey('Moments', models.DO_NOTHING, db_column='id_moment', default=1)

    class Meta:
        managed = True
        db_table = 'comments'

class Subscriptions(models.Model):
    subscription_date = models.DateField()
    id_author = models.ForeignKey('CustomUser', on_delete=models.CASCADE,  db_column='id_author', related_name='author_subscription', default=1)
    id_subscriber = models.ForeignKey('CustomUser', on_delete=models.CASCADE,  db_column='id_subscriber', related_name='subscriber_subscription', default=1)

    class Meta:
        managed = True
        db_table = 'subscriptions'

class Likes(models.Model):
    creation_date = models.DateField()
    id_author = models.ForeignKey('CustomUser', on_delete=models.CASCADE,  db_column='id_author', related_name='author_like', default=1)
    id_moment = models.ForeignKey('Moments', models.DO_NOTHING, db_column='id_moment', blank=True, null=True, related_name='moment_like')
    id_comment = models.ForeignKey('Comments', models.DO_NOTHING, db_column='id_comment', blank=True, null=True, related_name='comment_like')

    class Meta:
        managed = True
        db_table = 'likes'

class Tags(models.Model):
    title = models.CharField(max_length=100)
    id_moment = models.ForeignKey('Moments', models.DO_NOTHING, db_column='id_moment', default=1)

    class Meta:
        managed = True
        db_table = 'tags'