import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from core.config import settings


class StorageService:
    def __init__(self):
        self.use_local = settings.USE_LOCAL_STORAGE or not settings.AWS_ACCESS_KEY_ID
        if not self.use_local:
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION,
            )
        else:
            Path(settings.LOCAL_STORAGE_PATH).mkdir(parents=True, exist_ok=True)

    def _generate_key(self, workspace_id: str, filename: str) -> str:
        ext = Path(filename).suffix
        return f"{workspace_id}/{uuid.uuid4()}{ext}"

    def upload_file(self, workspace_id: str, filename: str, content: bytes) -> str:
        key = self._generate_key(workspace_id, filename)
        if self.use_local:
            path = Path(settings.LOCAL_STORAGE_PATH) / key
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            return key
        self.s3.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=content,
        )
        return key

    def download_file(self, key: str) -> bytes:
        if self.use_local:
            path = Path(settings.LOCAL_STORAGE_PATH) / key
            return path.read_bytes()
        response = self.s3.get_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
        return response["Body"].read()

    def delete_file(self, key: str) -> bool:
        try:
            if self.use_local:
                path = Path(settings.LOCAL_STORAGE_PATH) / key
                if path.exists():
                    path.unlink()
                return True
            self.s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
            return True
        except (ClientError, OSError):
            return False

    def get_presigned_url(self, key: str, expires: int = 3600) -> str | None:
        if self.use_local:
            return f"/uploads/{key}"
        try:
            return self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_S3_BUCKET, "Key": key},
                ExpiresIn=expires,
            )
        except ClientError:
            return None
