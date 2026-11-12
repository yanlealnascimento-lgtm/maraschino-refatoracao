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


def test_volume(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    assert get(client, 'volume_75') == {'success': True}
    kodi.Application.SetVolume.assert_called_once_with(volume=75)


def test_volume_not_a_number(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    assert get(client, 'volume_high') == {'failed': True}
    assert not kodi.Application.SetVolume.called


def test_seek(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    assert get(client, 'seek_30') == {'success': True}
    kodi.Player.Seek.assert_called_once_with(playerid=1, value=30)


def test_next_old_kodi(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    kodi.Application.GetProperties.return_value = {'version': {'major': 11}}
    assert get(client, 'next') == {'success': True}
    kodi.Player.GoNext.assert_called_once_with(playerid=1)


def test_next_new_kodi(client, kodi):
    # from version 12 on it uses GoTo instead of GoNext
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    kodi.Application.GetProperties.return_value = {'version': {'major': 12}}
    assert get(client, 'next') == {'success': True}
    kodi.Player.GoTo.assert_called_once_with(playerid=1, to='next')


def test_previous_old_kodi(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    kodi.Application.GetProperties.return_value = {'version': {'major': 11}}
    assert get(client, 'previous') == {'success': True}
    kodi.Player.GoPrevious.assert_called_once_with(playerid=1)


def test_previous_new_kodi(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    kodi.Application.GetProperties.return_value = {'version': {'major': 12}}
    assert get(client, 'previous') == {'success': True}
    kodi.Player.GoTo.assert_called_once_with(playerid=1, to='previous')


def test_shuffle_new_kodi(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    kodi.Application.GetProperties.return_value = {'version': {'major': 12}}
    assert get(client, 'shuffle') == {'success': True}
    kodi.Player.SetShuffle.assert_called_once_with(playerid=1, shuffle='toggle')


def test_shuffle_old_kodi(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    kodi.Application.GetProperties.return_value = {'version': {'major': 11}}
    kodi.Player.GetProperties.return_value = {'shuffled': False}
    assert get(client, 'shuffle') == {'success': True}
    kodi.Player.Shuffle.assert_called_once_with(playerid=1)


def test_unshuffle_old_kodi(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    kodi.Application.GetProperties.return_value = {'version': {'major': 11}}
    kodi.Player.GetProperties.return_value = {'shuffled': True}
    assert get(client, 'shuffle') == {'success': True}
    kodi.Player.UnShuffle.assert_called_once_with(playerid=1)


def test_repeat_new_kodi(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    kodi.Application.GetProperties.return_value = {'version': {'major': 12}}
    assert get(client, 'repeat') == {'success': True}
    kodi.Player.SetRepeat.assert_called_once_with(playerid=1, repeat='cycle')


def test_repeat_old_kodi(client, kodi):
    # old versions: off -> one -> all -> off
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    kodi.Application.GetProperties.return_value = {'version': {'major': 11}}
    kodi.Player.GetProperties.return_value = {'repeat': 'off'}
    assert get(client, 'repeat') == {'success': True}
    kodi.Player.Repeat.assert_called_once_with(playerid=1, state='one')


def test_update_video_library(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    assert get(client, 'update_video') == {'success': True}
    kodi.VideoLibrary.Scan.assert_called_once_with()


def test_clean_audio_library(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    assert get(client, 'clean_audio') == {'success': True}
    kodi.AudioLibrary.Clean.assert_called_once_with()


def test_reboot(client, kodi):
    kodi.Player.GetActivePlayers.return_value = [{'type': 'video'}]
    assert get(client, 'reboot') == {'success': True}
    kodi.System.Reboot.assert_called_once_with()
