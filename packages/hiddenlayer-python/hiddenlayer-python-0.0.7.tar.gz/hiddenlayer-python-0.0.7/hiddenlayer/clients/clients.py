import os
import requests
import numpy as np
import base64
import gzip

from typing import List, Union
from io import BytesIO

from hiddenlayer.config import config


class HiddenLayerClient(object):
    def __init__(self, token: str = None, api_host: str = None, version: int = None, proto: str = None):
        """HiddenLayer API Client

        :param token: api token for auth
        :param api_host: alternate hiddenlayer api host
        :param version: version number of api

        :return None
        """
        self.version = version or config.api_version() or 1
        self.token = token or config.api_token()
        self.api_host = api_host or config.api_host() or "api.hiddenlayer.com"
        self.proto = proto or config.api_proto() or "https"
        self.api_url = f"{self.proto}://{self.api_host}/caml/api/v{self.version}"

        if self.token is None:
            raise AttributeError("API token must be set via HL_API_TOKEN environment variable or passed to the client.")

        if self.api_url is None:
            raise AttributeError("API url must be set VIA HL_API_URL environment variable or passed to the client.")

        # setup session
        self.session = requests.Session()
        self.session.headers = {"token": self.token}

    def health(self) -> dict:
        """get endpoint health

        :return: response dictionary
        """
        resp = self.session.get(f"{self.api_url}/health")
        if resp.ok:
            return resp.json()
        else:
            raise requests.HTTPError(
                f"Failed to get endpoint health. Status code: {resp.status_code}, Detail: {resp.content}"
            )

    def get_event_count(self) -> int:
        resp = self.session.get(f"{self.api_url}/events")
        if resp.ok:
            data = resp.json()
            count = data.get("total", None)
            if count is not None:
                return count
            else:
                raise ValueError("Error retrieving event count. Key 'total' not found in response.")
        else:
            raise requests.HTTPError(
                f"Failed to get event count. Status code: {resp.status_code}, Detail: {resp.content}"
            )

    def get_alert_count(self) -> int:
        resp = self.session.get(f"{self.api_url}/alerts")
        if resp.ok:
            data = resp.json()
            count = data.get("total", None)
            if count is not None:
                return count
            else:
                raise ValueError("Error retrieving event count. Key 'total' not found in response.")
        else:
            raise requests.HTTPError(
                f"Failed to get alert count. Status code: {resp.status_code}, Detail: {resp.content}"
            )

    def get_event(self, event_id: str) -> dict:
        """get event by id

        :param event_id: event id to retrieve
        :return: response dictionary
        """
        resp = self.session.get(f"{self.api_url}/events/{event_id}")
        if resp.ok:
            return resp.json()
        else:
            raise requests.HTTPError(f"Failed to get event. Status code: {resp.status_code}, Detail: {resp.content}")

    def get_events(
        self,
        page: int = 0,
        sensor_id: str = None,
        requester_id: str = None,
        group_id: str = None,
        vector_exponent_sha256: str = None,
        vector_byte_size: int = None,
        vector_dtype: str = None,
        event_time_start: str = None,
        event_time_stop: str = None,
        max_results: int = 1000,
    ) -> List[dict]:
        """Get list of events

        :param page: page number
        :param sensor_id: filter by sensor_id
        :param requester_id: filter by requester_id
        :param group_id: filter by group_id
        :param vector_exponent_sha256: filter by vector exponent sha256
        :param vector_byte_size: filter by vector size in bytes
        :param vector_dtype: filter by vector data type
        :param event_time_start: start date for filtering by event_time
        :param event_time_stop: stop date for filtering by event_time
        :param max_results: max number of results to retrieve
        :return: list of events
        """
        params = {"page": page}
        if sensor_id is not None:
            params.update({"sensor_id": sensor_id})
        if requester_id is not None:
            params.update({"requester_id": requester_id})
        if group_id is not None:
            params.update({"group_id": group_id})
        if vector_exponent_sha256 is not None:
            params.update({"vector_exponent_sha256": vector_exponent_sha256})
        if vector_byte_size is not None:
            params.update({"vector_byte_size": vector_byte_size})
        if vector_dtype is not None:
            params.update({"vector_dtype": vector_dtype})
        if event_time_start is not None:
            params.update({"event_time_start": event_time_start})
        if event_time_stop is not None:
            params.update({"event_time_stop": event_time_stop})

        url = f"{self.api_url}/events"
        results = []
        resp = self.session.get(url, params=params)
        if resp.ok:
            content = resp.json()
            results.extend(content["results"])
            if content["next"]:
                url = content["next"]
            else:
                url = None

            if len(results) < max_results and url:
                while url:
                    resp = self.session.get(url)
                    if resp.ok:
                        content = resp.json()
                        results.extend(content["results"])

                        if content["next"]:
                            url = content["next"]
                        else:
                            url = None

                        if len(results) >= max_results:
                            break
                    else:
                        raise requests.HTTPError(
                            f"Failed to retrieve events page. "
                            f"Status code: {resp.status_code}, Page: {page}, Detail: {resp.content}"
                        )
        else:
            raise requests.HTTPError(
                f"Failed to retrieve events page. "
                f"Status code: {resp.status_code}, Page: {page}, Detail: {resp.content}"
            )

        return results[:max_results] if max_results else results

    def get_alert(self, alert_id: str) -> dict:
        """get alert by id

        :param alert_id: id of alert to retrieve
        :return: response dictionary
        """
        resp = self.session.get(f"{self.api_url}/alerts/{alert_id}")
        if resp.ok:
            return resp.json()
        else:
            raise requests.HTTPError(f"Failed to get alert. Status code: {resp.status_code}, Detail: {resp.content}")

    def get_alerts(
        self,
        page: int = 0,
        sensor_id: str = None,
        requester_id: str = None,
        group_id: str = None,
        vector_exponent_sha256: str = None,
        vector_byte_size: int = None,
        vector_dtype: str = None,
        event_time_start: str = None,
        event_time_stop: str = None,
        max_results: int = 1000,
    ) -> List[dict]:
        """Get list of events

        :param page: page number
        :param sensor_id: filter by sensor_id
        :param requester_id: filter by requester_id
        :param group_id: filter by group_id
        :param vector_exponent_sha256: filter by vector exponent sha256
        :param vector_byte_size: filter by vector size in bytes
        :param vector_dtype: filter by vector data type
        :param event_time_start: start date for filtering by event_time
        :param event_time_stop: stop date for filtering by event_time
        :param max_results: max number of results to retrieve
        :return: list of events
        """
        params = {"page": page}
        if sensor_id is not None:
            params.update({"sensor_id": sensor_id})
        if requester_id is not None:
            params.update({"requester_id": requester_id})
        if group_id is not None:
            params.update({"group_id": group_id})
        if vector_exponent_sha256 is not None:
            params.update({"vector_exponent_sha256": vector_exponent_sha256})
        if vector_byte_size is not None:
            params.update({"vector_byte_size": vector_byte_size})
        if vector_dtype is not None:
            params.update({"vector_dtype": vector_dtype})
        if event_time_start is not None:
            params.update({"event_time_start": event_time_start})
        if event_time_stop is not None:
            params.update({"event_time_stop": event_time_stop})

        url = f"{self.api_url}/alerts"
        results = []
        resp = self.session.get(url, params=params)
        if resp.ok:
            content = resp.json()
            results.extend(content["results"])
            if content["next"]:
                url = content["next"]
            else:
                url = None

            if len(results) < max_results and url:
                while url:
                    resp = self.session.get(url)
                    if resp.ok:
                        content = resp.json()
                        results.extend(content["results"])

                        if content["next"]:
                            url = content["next"]
                        else:
                            url = None

                        if len(results) >= max_results:
                            break
                    else:
                        raise requests.HTTPError(
                            f"Failed to retrieve alerts page. "
                            f"Status code: {resp.status_code}, Page: {page}, Detail: {resp.content}"
                        )
        else:
            raise requests.HTTPError(
                f"Failed to retrieve alerts page. "
                f"Status code: {resp.status_code}, Page: {page}, Detail: {resp.content}"
            )

        return results[:max_results] if max_results else results

    def get_vector(self, vector_sha256: str) -> requests.Response:
        """get vector by sha256

        :param vector_sha256: sha256 of vector to retrieve
        :return: Vector as a list
        """
        resp = self.session.get(f"{self.api_url}/vectors/{vector_sha256}")
        if resp.ok:
            return resp.json()
        else:
            raise requests.HTTPError(f"Failed to get vector. Status code: {resp.status_code}, Detail: {resp.content}")

    def submit(
        self,
        model_id: str,
        requester_id: str,
        vectors: Union[List[List[Union[int, float]]], np.ndarray],
        predictions: Union[List[Union[int, float]], np.ndarray],
        compress: bool = False,
    ):
        if isinstance(vectors, list):
            if len(vectors) != len(predictions):
                raise ValueError(
                    f"Length of vectors is not equal to length of predictions. "
                    f"Vectors: {len(vectors)}, Predictions: {len(predictions)}"
                )
        elif isinstance(vectors, np.ndarray):
            if vectors.shape[0] != len(predictions):
                raise ValueError(
                    f"Length of vectors is not equal to length of predictions. "
                    f"Vectors: {vectors.shape[0]}, Predictions: {len(predictions)}"
                )

        buffer = BytesIO()
        np.save(buffer, vectors, allow_pickle=True)

        if compress:
            encoded_vectors = base64.b64encode(gzip.compress(buffer.getvalue())).decode()
        else:
            encoded_vectors = base64.b64encode(buffer.getvalue()).decode()

        payload = {
            "model_id": model_id,
            "requester_id": requester_id,
            "vectors": encoded_vectors,
            "predictions": predictions,
        }

        resp = self.session.post(f"{self.api_url}/submit", json=payload)
        if resp.ok:
            return resp.json()
        else:
            raise requests.HTTPError(
                f"Failed to submit to api. Status code: {resp.status_code}, Detail: {resp.content}"
            )
