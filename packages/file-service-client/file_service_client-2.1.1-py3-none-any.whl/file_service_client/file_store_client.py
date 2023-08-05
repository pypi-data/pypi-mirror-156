import pathlib
from typing import Dict, Any, List, Union, Generator
from clients_core.service_clients import E360ServiceClient
from pydantic import parse_obj_as
from requests.models import Response

from .models import FileResourceModel


class FileStoreServiceClient(E360ServiceClient):
    """
    Subclasses dataclass `clients_core.service_clients.E360ServiceClient`.

    Args:
        client (clients_core.rest_client.RestClient): an instance of a rest client
        user_id (str): the user_id guid

    """

    service_endpoint = ""
    extra_headers: Dict[str, str] = {"Accept": "application/octet-stream"}

    def create(self, file_path: pathlib.Path, **kwargs: Any) -> FileResourceModel:
        """
        Create a new file to be stored.

        Args:
            file_path: Path object to which file to upload.

        Raises:
            FileNotFoundError: when ``file_path`` is not found.

        """

        if not file_path.is_file():
            raise FileNotFoundError(f"File specified is not found: {file_path}")

        with file_path.open("rb") as file_handle:
            file_upload = {"file": (file_path.name, file_handle)}
            response = self.client.post(
                "",
                files=file_upload,
                headers=self.service_headers,
                raises=True,
                **kwargs,
            )
            return self._get_response_result(response)

    def update(
        self, file_id: str, file_path: pathlib.Path, **kwargs: Any
    ) -> FileResourceModel:
        """
        Update existing file store
        Args:
            file_id: the file id for FileResourceModel
            file_path: Path object to which file to upload.

        Raises:
            FileNotFoundError: when ``file_path`` is not found.

        Returns:
            FileResourceModel: the updated model returned from request
        """

        if not file_path.is_file():
            raise FileNotFoundError(f"File specified is not found: {file_path}")

        headers = {
            "Content-Type": "application/octet-stream",
            **self.service_headers,
        }

        with file_path.open("rb") as file_handle:
            response = self.client.put(
                file_id, data=file_handle, headers=headers, raises=True, **kwargs
            )
            return self._get_response_result(response)

    def get_by_id(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        """This client does not support object retrieval"""
        raise NotImplementedError(
            "This method is not supported, use `self.get_file_bytes` instead."
        )

    def get_file_bytes(
        self, file_id: str, stream_chunk: int = 0, **kwargs: Any
    ) -> Union[bytes, Generator[bytes, None, None]]:
        """
        Returns file bytes by ``file_id``.
        """
        response = self.client.get(
            file_id, headers=self.service_headers.copy(), raises=True, **kwargs
        )
        if stream_chunk:
            return response.iter_content(stream_chunk)
        return response.content

    def delete_by_id(self, file_id: str, **kwargs: Any) -> bool:
        """
        Delete the file object by its id. Returns True when deleted successfully.
        """
        response = self.client.delete(file_id, headers=self.service_headers, **kwargs)
        return response.ok

    @staticmethod
    def _get_response_result(response: Response) -> FileResourceModel:
        response_json: List[Dict] = response.json()
        # Patch location value from headers
        if response_json and isinstance(response_json, list):
            response_json[0]["location"] = response.headers.get("Location")
            return parse_obj_as(List[FileResourceModel], response_json)[0]
        return parse_obj_as(FileResourceModel, response_json)
