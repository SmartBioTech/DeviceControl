from unittest import TestCase
from unittest.mock import Mock, call, patch

from requests.exceptions import ConnectionError
from requests.models import Response as RequestResponse

from core.connection.client.flask_client import Client
from core.utils.networking import RequestTypes


class TestClient(TestCase):

    def test_get(self):
        endpoint = Mock()
        client = Client()
        client.session.get = Mock()
        request_response = RequestResponse()
        request_response.status_code = 200
        client.session.get.return_value = request_response
        self.assertEqual(client.get(endpoint).status_code, 200)
        client.session.get.side_effect = ConnectionError()
        self.assertEqual(client.get(endpoint).status_code, 404)

    def test_post(self):
        endpoint = Mock()
        client = Client()
        client.session.post = Mock()
        request_response = RequestResponse()
        request_response.status_code = 200
        client.session.post.return_value = request_response
        self.assertEqual(client.post(endpoint, []).status_code, 200)
        client.session.post.side_effect = ConnectionError()
        self.assertEqual(client.post(endpoint, []).status_code, 404)

    def test_start(self):
        client = Client()
        client.connect = Mock()
        client.sync_manager = Mock()
        client.on_error = Mock()
        mock_url = "mock_url"

        client.connect.return_value = True
        client.start(mock_url)
        client.connect.assert_called_once()
        client.on_error.assert_not_called()
        client.sync_manager.start_synchronization.assert_called_once()

        client.sync_manager.reset_mock()
        client.on_error.reset_mock()
        client.connect.reset_mock()

        client.connect.side_effect = [False, True]
        client.start(mock_url)
        self.assertEqual(client.connect.call_count, 2)
        client.on_error.assert_called_once()
        self.assertEqual(client.server_url, mock_url)

    def test_stop(self):
        client = Client()
        client.stop()
        self.assertFalse(client.sync_manager.is_active)

    def test_handle_incoming(self):
        def return_first_argument(*args, **kwargs):
            return args[0]

        mock_incoming1 = {
            "id": Mock(),
            "type": Mock(),
            "data": Mock()
        }
        mock_incoming2 = {
            "id": Mock(),
            "type": Mock(),
            "data": Mock()
        }

        RequestTypes.from_string = Mock()
        RequestTypes.from_string.side_effect = return_first_argument

        mock_incoming_list = [mock_incoming1, mock_incoming2]

        client = Client()
        client.execute_incoming = Mock()
        client.handle_incoming(mock_incoming_list)
        calls = [
            call(
                mock_incoming1.get("type"),
                mock_incoming1.get("data"),
                mock_incoming1.get("id")
            ),
            call(
                mock_incoming2.get("type"),
                mock_incoming2.get("data"),
                mock_incoming2.get("id")
            )
        ]

        client.execute_incoming.assert_has_calls(calls, any_order=True)

    def test_execute_incoming(self):
        type_ = Mock()
        config = Mock()
        request_id = Mock()

        target = Mock()
        success = Mock()
        cause = Mock()
        data = Mock()
        target.return_value = success, cause, data

        client = Client()
        client.request_types = Mock()
        client.request_types.get = Mock(side_effect=[None, target])
        client.respond = Mock()

        with patch("builtins.TypeError") as MockTypeError:
            client.execute_incoming(type_, config, request_id)
            client.respond.assert_called_with(False, MockTypeError(), None, request_id, type_)

        client.execute_incoming(type_, config, request_id)
        client.respond.assert_called_with(success, cause, data, request_id, type_)

    def test_sync(self):
        self.fail()

    def test_connect(self):
        self.fail()

    def test_respond(self):
        self.fail()
