import json


def get(client, command):
    response = client.get('/xhr/controls/' + command)
    return json.loads(response.data)


def test_play_pause_video(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    assert get(client, 'play_pause') == {'success': True}
    kodi.Player.PlayPause.assert_called_once_with(playerid=1)


def test_play_pause_audio(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'audio'}]
    assert get(client, 'play_pause') == {'success': True}
    kodi.Player.PlayPause.assert_called_once_with(playerid=0)


def test_stop(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    assert get(client, 'stop') == {'success': True}
    kodi.Player.Stop.assert_called_once_with(playerid=1)


def test_no_player(client, kodi):
    kodi.Player.GetActivePlayers.side_effect = Exception('no connection')
    assert get(client, 'play_pause') == {'failed': True}
    assert not kodi.Player.PlayPause.called


def test_unknown_player_type(client, kodi):
    # playerid is never set for this type, so the call fails with a NameError
    kodi.Player.GetActivePlayers.return_value = [{'type': 'picture'}]
    assert get(client, 'stop') == {'failed': True}
    assert not kodi.Player.Stop.called
