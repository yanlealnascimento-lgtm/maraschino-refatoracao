import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'lib'))

import pytest
from mock import MagicMock, patch


@pytest.fixture
def app():
    from Maraschino import app as flask_app
    import modules.controls  # registers the control routes
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def server_config():
    return {'mac_address': None}


@pytest.fixture
def kodi(server_config):
    server = MagicMock()
    with patch('modules.controls.jsonrpclib.Server', return_value=server), \
            patch('modules.controls.server_api_address', return_value='http://kodi'), \
            patch('modules.controls.server_settings', return_value=server_config), \
            patch('modules.controls.logger'):
        yield server
