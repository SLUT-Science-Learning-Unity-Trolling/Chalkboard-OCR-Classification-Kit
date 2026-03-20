import io
from unittest.mock import MagicMock, patch

import pytest

from botocore.exceptions import ClientError

# важно: conftest.py уже подменил app.config/boto3/botocore до этого импорта
from app.adapters.gateways.s3 import MinioGateway


def _client_error(op_name: str):
    return ClientError({"Error": {"Code": "Boom", "Message": "boom"}}, operation_name=op_name)


def test_connect_bucket_exists():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-test"}]}

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3) as mock_boto_client:
        MinioGateway()
        mock_boto_client.assert_called_once()
        mock_s3.create_bucket.assert_not_called()


def test_connect_bucket_missing_creates_bucket():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "other"}]}

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        gateway = MinioGateway()
        mock_s3.create_bucket.assert_called_once_with(Bucket="bucket-test")
        assert gateway._client == mock_s3


def test_connect_clienterror_raises_exception():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.side_effect = _client_error("ListBuckets")

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        with pytest.raises(Exception) as exc:
            MinioGateway()
        assert "Ошибка подключения к MiniO" in str(exc.value)


def test_upload_file_success():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-test"}]}

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        gateway = MinioGateway()
        gateway.upload_file("local.txt", "remote.txt")

        mock_s3.upload_file.assert_called_once_with("local.txt", "bucket-test", "remote.txt")


def test_upload_file_clienterror():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-test"}]}
    mock_s3.upload_file.side_effect = _client_error("UploadFile")

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        gateway = MinioGateway()
        with pytest.raises(Exception) as exc:
            gateway.upload_file("local.txt", "remote.txt")
        assert "Ошибка загрузки файла" in str(exc.value)


def test_put_object_calls_put_object_with_correct_params():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-test"}]}

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        gateway = MinioGateway()

        data = io.BytesIO(b"hello")
        gateway.put_object("obj.bin", data=data, size=5, content_type="application/octet-stream")

        kwargs = mock_s3.put_object.call_args.kwargs
        assert kwargs["Bucket"] == "bucket-test"
        assert kwargs["Key"] == "obj.bin"
        assert kwargs["Body"] is data
        assert kwargs["ContentLength"] == 5
        assert kwargs["ContentType"] == "application/octet-stream"


def test_put_object_clienterror():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-test"}]}
    mock_s3.put_object.side_effect = _client_error("PutObject")

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        gateway = MinioGateway()
        with pytest.raises(Exception) as exc:
            gateway.put_object("obj.bin", data=io.BytesIO(b"x"), size=1)
        assert "Ошибка загрузки файла" in str(exc.value)


def test_download_file_success():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-test"}]}

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        gateway = MinioGateway()
        gateway.download_file("remote.txt", "local.txt")

        mock_s3.download_file.assert_called_once_with("bucket-test", "remote.txt", "local.txt")


def test_delete_file_success():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-test"}]}

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        gateway = MinioGateway()
        gateway.delete_file("remote.txt")

        mock_s3.delete_object.assert_called_once_with(Bucket="bucket-test", Key="remote.txt")


def test_generate_presigned_url_success():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-test"}]}
    mock_s3.generate_presigned_url.return_value = "http://signed-url"

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        gateway = MinioGateway()
        url = gateway.generate_presigned_url("remote.txt", expiration=3600)

        assert url == "http://signed-url"
        mock_s3.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={"Bucket": "bucket-test", "Key": "remote.txt"},
            ExpiresIn=3600,
        )


def test_generate_presigned_url_clienterror():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-test"}]}
    mock_s3.generate_presigned_url.side_effect = _client_error("Presign")

    with patch("app.adapters.gateways.s3.client", return_value=mock_s3):
        gateway = MinioGateway()
        with pytest.raises(Exception) as exc:
            gateway.generate_presigned_url("remote.txt")
        assert "Ошибка генерации ссылки" in str(exc.value)