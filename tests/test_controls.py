import json

import pytest


def set_playing(kodi, player_type):
    kodi.Player.GetActivePlayers.return_value = [{'type': player_type}]


def set_version(kodi, major):
    kodi.Application.GetProperties.return_value = {'version': {'major': major}}


def send_command(client, name):
    response = client.get('/xhr/controls/%s' % name)
    assert response.status_code == 200
    return json.loads(response.data)


SUCCESS = {'success': True}
FAILURE = {'failed': True}


# Player selection

def test_video_uses_player_1(client, kodi):
    set_playing(kodi, 'video')
    assert send_command(client, 'play_pause') == SUCCESS
    kodi.Player.PlayPause.assert_called_once_with(playerid=1)


def test_audio_uses_player_0(client, kodi):
    set_playing(kodi, 'audio')
    assert send_command(client, 'play_pause') == SUCCESS
    kodi.Player.PlayPause.assert_called_once_with(playerid=0)


def test_no_active_player_fails(client, kodi):
    kodi.Player.GetActivePlayers.side_effect = Exception('no connection')
    assert send_command(client, 'play_pause') == FAILURE
    assert not kodi.Player.PlayPause.called


def test_unknown_player_type_fails(client, kodi):
    # playerid is never defined
    set_playing(kodi, 'picture')
    assert send_command(client, 'stop') == FAILURE
    assert not kodi.Player.Stop.called


# Simple playback commands

@pytest.mark.parametrize('name, method, arguments', [
    ('play_pause', 'PlayPause', {}),
    ('stop', 'Stop', {}),
    ('fast_forward', 'SetSpeed', {'speed': 'increment'}),
    ('rewind', 'SetSpeed', {'speed': 'decrement'}),
])
def test_playback_commands(client, kodi, name, method, arguments):
    set_playing(kodi, 'video')
    assert send_command(client, name) == SUCCESS
    expected = dict(arguments, playerid=1)
    getattr(kodi.Player, method).assert_called_once_with(**expected)


# Volume and seek

def test_volume(client, kodi):
    set_playing(kodi, 'video')
    assert send_command(client, 'volume_75') == SUCCESS
    kodi.Application.SetVolume.assert_called_once_with(volume=75)


def test_invalid_volume_fails(client, kodi):
    set_playing(kodi, 'video')
    assert send_command(client, 'volume_high') == FAILURE
    assert not kodi.Application.SetVolume.called


def test_seek(client, kodi):
    set_playing(kodi, 'video')
    assert send_command(client, 'seek_30') == SUCCESS
    kodi.Player.Seek.assert_called_once_with(playerid=1, value=30)


# Next and previous depend on the Kodi version

@pytest.mark.parametrize('name, old_method, target', [
    ('next', 'GoNext', 'next'),
    ('previous', 'GoPrevious', 'previous'),
])
def test_navigation_old_kodi(client, kodi, name, old_method, target):
    set_playing(kodi, 'video')
    set_version(kodi, 11)
    assert send_command(client, name) == SUCCESS
    getattr(kodi.Player, old_method).assert_called_once_with(playerid=1)
    assert not kodi.Player.GoTo.called


@pytest.mark.parametrize('name, old_method, target', [
    ('next', 'GoNext', 'next'),
    ('previous', 'GoPrevious', 'previous'),
])
def test_navigation_new_kodi(client, kodi, name, old_method, target):
    set_playing(kodi, 'video')
    set_version(kodi, 12)
    assert send_command(client, name) == SUCCESS
    kodi.Player.GoTo.assert_called_once_with(playerid=1, to=target)
    assert not getattr(kodi.Player, old_method).called


# Shuffle

def test_shuffle_new_kodi(client, kodi):
    set_playing(kodi, 'video')
    set_version(kodi, 12)
    assert send_command(client, 'shuffle') == SUCCESS
    kodi.Player.SetShuffle.assert_called_once_with(playerid=1, shuffle='toggle')


@pytest.mark.parametrize('shuffled, method', [
    (True, 'UnShuffle'),
    (False, 'Shuffle'),
])
def test_shuffle_old_kodi(client, kodi, shuffled, method):
    set_playing(kodi, 'video')
    set_version(kodi, 11)
    kodi.Player.GetProperties.return_value = {'shuffled': shuffled}
    assert send_command(client, 'shuffle') == SUCCESS
    getattr(kodi.Player, method).assert_called_once_with(playerid=1)


# Repeat

def test_repeat_new_kodi(client, kodi):
    set_playing(kodi, 'video')
    set_version(kodi, 12)
    assert send_command(client, 'repeat') == SUCCESS
    kodi.Player.SetRepeat.assert_called_once_with(playerid=1, repeat='cycle')


@pytest.mark.parametrize('current, next_state', [
    ('off', 'one'),
    ('one', 'all'),
    ('all', 'off'),
])
def test_repeat_old_kodi_cycles_states(client, kodi, current, next_state):
    set_playing(kodi, 'video')
    set_version(kodi, 11)
    kodi.Player.GetProperties.return_value = {'repeat': current}
    assert send_command(client, 'repeat') == SUCCESS
    kodi.Player.Repeat.assert_called_once_with(playerid=1, state=next_state)


# Library and system

@pytest.mark.parametrize('name, group, method', [
    ('update_video', 'VideoLibrary', 'Scan'),
    ('clean_video', 'VideoLibrary', 'Clean'),
    ('update_audio', 'AudioLibrary', 'Scan'),
    ('clean_audio', 'AudioLibrary', 'Clean'),
    ('poweroff', 'System', 'Shutdown'),
    ('suspend', 'System', 'Suspend'),
    ('reboot', 'System', 'Reboot'),
    ('pvr-scan', 'PVR', 'Scan'),
])
def test_library_and_system_commands(client, kodi, name, group, method):
    set_playing(kodi, 'video')
    assert send_command(client, name) == SUCCESS
    getattr(getattr(kodi, group), method).assert_called_once_with()
