import logging

from django.conf import settings
from rest_framework.response import Response
from rest_framework import views
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import boto3
import uuid

logger = logging.getLogger(__name__)

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

class GenerateUploadInfo(views.APIView):
    def post(self, request):
        upload_info = self.generate_upload_url(request, settings.IS_LOCAL)
        return Response(upload_info)

    # Create your views here.
    def upload_to_s3():
        logger.info("Uploading image to s3")

    def upload_locally():
        logger.debug("Uploading image locally")

    def generate_upload_url(self, request, is_local=True) -> dict:
        filename = request.data['filename']
        content_type = request.data['content_type']

        # TODO: add content type validation

        unique_name = f"{uuid.uuid4()}_{filename}"

        if is_local:
            # for local testing
            return {
                "upload_url": "/local-image-upload/",
                "image_url": request.build_absolute_uri(f"/media/{unique_name}")
            }
        
        # upload to s3 info
        s3_key = f"{settings.S3_KEY_PREFIX}/{unique_name}"
        image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        upload_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": s3_key,
                "ContentType": content_type
            },
            ExpireseIn=1800
        )

        return Response({
            "strategy": "s3",
            "upload_url": upload_url,
            "image_url": image_url,
        })


class FileLocalUpload(views.APIView):
    # upload files locally
    def post(self, request):
        file = request.FILES["file"]
        filename = request.data["filename"]

        path = f"{settings.S3_KEY_PREFIX}/{filename}"

        default_storage.save(path, ContentFile(file.read()))

        return Response({"status": "ok"})