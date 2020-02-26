import uuid
import os
import hashlib
from django.db import models
from root.settings import BASE_DIR


# Create your models here.
class File(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    filepath = models.FileField(
        upload_to='%Y/%m/%d'
    )
    filename = models.CharField(
        max_length=255,
        blank=True,
    )
    filesize = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    checksum = models.CharField(
        max_length=255,
        blank=True,
    )
    upload_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    def __str__(self):
        return str(self.id)

    def absolute_url(self):
        return os.path.join(BASE_DIR, self.filepath.url)

    def save(self, *args, **kwargs):
        """ Fyld data ud. """
        super().save()

        if not self.checksum:
            self.checksum = hashlib.md5(open(self.absolute_url(), 'rb').read()).hexdigest()
        if not self.filesize:
            self.filesize = os.path.getsize(self.absolute_url())
        if not self.filename:
            self.filename = os.path.basename(self.absolute_url())
        super().save()

    def delete(self, *args, **kwargs):
        os.remove(self.absolute_url())
        super().delete()

