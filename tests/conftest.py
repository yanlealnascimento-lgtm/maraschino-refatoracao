import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'lib'))

import pytest
from mock import MagicMock, patch


@pytest.fixture
def client():
    from Maraschino import app
    import modules.controls
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture
def kodi():
    server = MagicMock()
    with patch('modules.controls.jsonrpclib.Server', return_value=server), \
            patch('modules.controls.server_api_address', return_value='http://kodi'), \
            patch('modules.controls.server_settings', return_value={'mac_address': None}), \
            patch('modules.controls.logger'):
        yield server
