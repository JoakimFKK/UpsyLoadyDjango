""" TODO: Lav en temp database-tabel der indeholder filer der er i gang med at bliver uploadet(?) """
# region Imports
import hashlib
import os
import uuid

from django.db import models
from magic import from_file as verify_ct
# endregion Imports

"""FIL SLETNING BASERET PÅ UPLOADS TIDSPUNKT! IKKE IMPLEMENTERET!

 from datetime import datetime, timedelta
 File.objects.filter(upload_date__lte=datetime.now(), upload_date__gte=datetime.now()-timedelta(days=30))

 Dette får fat i objekter der er imellem i dag, og 30 dage siden.
 """


class File(models.Model):
    """ Kopi af Fil tabellen fra UpsyLoady.

     Tilføjelser, og mangler:
        - Jeg har tilføjet en upload_date som bliver sat når filen bliver gemt i databasen.
        - Navngivning af kolonner er ikke de samme som i databasen, TODO.
        - NSFW er ikke tilføjet, TODO
     """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,)
    filepath = models.FileField(
        upload_to='%Y/%m/%d',)
    filename = models.CharField(
        max_length=255,
        blank=True,)
    filesize = models.PositiveIntegerField(
        blank=True,
        null=True,)
    checksum = models.CharField(
        max_length=255,
        blank=True,)
    upload_date = models.DateField(
        auto_now_add=True,
        editable=False,)
    media_type = models.CharField(
        max_length=50,
        blank=True,)

    def __str__(self):
        """ Sætter dens objekt-navn til objektets id.

         Kun for æstetiske grunde, har kun en inflydelse på Python & Django
         """
        return str(self.id)

    def absolute_url(self):
        """ Returnere filens fulde position. """
        return self.filepath.path

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
            temp_checksum = hashlib.md5(open(self.absolute_url(), 'rb').read()).hexdigest()
            if len(File.objects.filter(checksum=self.checksum)) >= 1:
                """ Hvis `self.checksum` allerede er i databasen bliver den slettet. """
                self.delete()
                return
            self.checksum = temp_checksum

        if not self.filesize:
            self.filesize = os.path.getsize(self.absolute_url())

        if not self.filename:
            self.filename = os.path.basename(self.absolute_url())
        super().save()

    def delete(self, *args, **kwargs):
        """ Sletter filen, og filens info i databasen. Override af parent-method. """
        os.remove(self.absolute_url())
        super().delete()
