from rest_framework.serializers import ModelSerializer

from api.models import File


class FileSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = [
            # 'id',
            'filepath',
            # 'filename',
            # 'filesize',
            # 'checksum',
        ]

