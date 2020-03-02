from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import File
from api.serializers import FileSerializer
from root.settings import CONTENT_TYPES, FILE_UPLOAD_MAX_MEMORY_SIZE


class FilUploadView(APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FileSerializer

    def post(self, request, *args, **kwargs):
        """ Bruger api.models til at gemme filen. """
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            up_file = request.FILES['filepath']
            if not up_file:
                return Response('up_file', status=status.HTTP_400_BAD_REQUEST)
            if not up_file.size < FILE_UPLOAD_MAX_MEMORY_SIZE:
                return Response('Fat', status=status.HTTP_400_BAD_REQUEST)
            try:
                """ HTML Header check """
                con_type, con_ext = str(up_file.content_type).split('/')
                if con_ext in CONTENT_TYPES[con_type]:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except KeyError:
                return Response('header', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """ Viser de 5 nyeste uploads. """
        files = [file.filepath.url for file in File.objects.order_by('-upload_date')[:5]]
        return Response(files)
