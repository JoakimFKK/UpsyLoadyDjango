import uuid
import hashlib
import os
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from root.settings import BASE_DIR

def get_expiration():
    now = timezone.now()
    return now + timedelta(days=30)

class Category(models.Model):
    category_name = models.CharField(
        max_length=255,
    )


class Tag(models.Model):
    tag_name = models.CharField(
        max_length=255,
    )


class Comment(models.Model):
    pass


class Entity(models.Model):
    entity_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user_id = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='entities',
        blank=True,
    )
    categories = models.ManyToManyField(
        'Category',
        related_name='entities',
        blank=True,
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )


class File(models.Model):
    """ Kopi af Fil tabellen fra UpsyLoady.

     Tilføjelser, og mangler:
        - Jeg har tilføjet en upload_date som bliver sat når filen bliver gemt i databasen.
        - Navngivning af kolonner er ikke de samme som i databasen, TODO.
        - NSFW er ikke tilføjet, TODO
     """
    entity_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    file_path = models.FileField(
        upload_to='%Y/%m/%d'
    )
    file_name = models.CharField(
        max_length=255,
        blank=True,
    )
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    file_checksum = models.CharField(
        max_length=255,
        blank=True,
    )
    file_type = models.CharField(
        max_length=25,
        blank=True,
    )
    nsfw = models.BooleanField(
        default=False
    )

    def __str__(self):
        """ Sætter dens objekt-navn til objektets id.

         Kun for æstetiske grunde, har kun en inflydelse på Python.
         """
        return str(self.id)

    def absolute_url(self):
        """ Returnere filens fulde position. """
        return os.path.join(BASE_DIR, self.filepath.url)

    def save(self, *args, **kwargs):
        """ Fylder data ud, override af parent-method.

         NOTE! Eftersom vi bruger MSSQL, og da der på nuværende tidspunkt (d.27/2-20)
         bruges en SQLite3 database, hvilket jo ikke stemmer overens.
         For at fikse det problem skal `super().save()` fjernes og erstattes med en
         SQL query til den reelle server.

         Denne metode overrider dens `parent-method`, og for at kalde på den skal `super()` bruges
         efterfulgt af metodens navn.
         """
        super().save()

        if not self.checksum:
            self.checksum = hashlib.md5(open(self.absolute_url(), 'rb').read()).hexdigest()
        if not self.filesize:
            self.filesize = os.path.getsize(self.absolute_url())
        if not self.filename:
            self.filename = os.path.basename(self.absolute_url())
        super().save()

    def delete(self, *args, **kwargs):
        """ Sletter filen, og filens info i databasen. Override af parent-method. """
        os.remove(self.absolute_url())
        super().delete()


class Report(models.Model):
    reported_entity = models.ForeignKey(
        'Entity',
        on_delete=models.DO_NOTHING,
    )
    user_id = models.ForeignKey(
        'User',
        on_delete=models.DO_NOTHING,
    )
    moderator_id = models.ForeignKey(
        'User',
        on_delete=models.DO_NOTHING,
    )
    reason = models.CharField(
        max_length=255,
    )
    optional_explanation = models.TextField(
        blank=True,
    )
    active = models.BooleanField(
        default=False,
    )


class Thread(models.Model):
    entity = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE,
        related_name='thread',
    )
    file = models.ForeignKey(
        'File',
        on_delete=models.SET_NULL,
        related_name='thread',
    )
    title = models.CharField(
        max_length=255,
    )
    description = models.TextField(
        max_length=1000,
        blank=True,
    )
    edited = models.BooleanField(
        default=False,
    )
    is_private = models.BooleanField(
        default=False,
    )
    allow_comments = models.BooleanField(
        default=True,
    )
    expiration_date = models.DateTimeField(
        default=get_expiration,
    )


class Vote(models.Model):
    class Meta:
        unique_together = (
            ('entity_id', 'user_id'),
        )
    entity_id = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE,
    )
    user_id = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    up_or_down = models.BooleanField()


class CustomUser(AbstractUser):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
