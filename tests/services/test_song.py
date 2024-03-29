import pytest
from flask import Flask
from unittest import mock
from typing import Callable
from threading import Thread
from werkzeug.datastructures import FileStorage

from app.models.user import User
from app.services.song import SongService
from app.repositories.song import SongRepository
from app.common.messages import (
    UNAUTHORIZED_TO_DELETE_SONG,
    UNAUTHORIZED_TO_UPDATE_SONG,
)
from app.common.exceptions import (
    NotFoundException,
    UnauthorizedException,
    FieldRequiredException,
)


@pytest.fixture
def mocked_app():
    mocked_app_ = mock.MagicMock()
    yield mocked_app_


@pytest.fixture
def mocked_song_repository():
    with mock.patch("app.services.song.SongRepository") as MockedSongRepository:
        yield MockedSongRepository.return_value


@pytest.fixture
def mocked_upload_file():
    yield mock.MagicMock()


@pytest.fixture
def mocked_process_files_to_streams():
    with mock.patch(
        "app.services.song.process_files_to_streams"
    ) as mocked_process_files_to_streams_:
        yield mocked_process_files_to_streams_


@pytest.fixture
def mocked_thread():
    with mock.patch("app.services.song.Thread") as MockedThread_:
        yield MockedThread_.return_value


@pytest.fixture
def mocked_current_user():
    yield mock.MagicMock()


def test_positive_create_song(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_process_files_to_streams: Callable,
    mocked_upload_file: Callable,
    mocked_thread: Thread,
):
    data = {
        "title": "test",
    }
    files = {
        "song_file": mock.MagicMock(),
        "small_thumbnail_file": mock.MagicMock(),
        "large_thumbnail_file": mock.MagicMock(),
    }

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service.create(files, data)

    mocked_process_files_to_streams.assert_called_once()
    mocked_thread.start.assert_called_once()


def test_positive_create_song_skip_optional_fields(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_process_files_to_streams: Callable,
    mocked_upload_file: Callable,
    mocked_thread: Thread,
):
    data = {
        "title": "test",
    }
    files = {
        "song_file": mock.MagicMock(),
        "small_thumbnail_file": FileStorage(None, ""),
        "large_thumbnail_file": FileStorage(None, ""),
    }

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service.create(files, data)

    mocked_process_files_to_streams.assert_called_once()
    mocked_thread.start.assert_called_once()


def test_negative_create_song_title_required(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
    mocked_process_files_to_streams: Callable,
    mocked_thread: Thread,
):
    data = {}
    files = {
        "song_file": mock.MagicMock(),
        "small_thumbnail_file": mock.MagicMock(),
        "large_thumbnail_file": mock.MagicMock(),
    }

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    with pytest.raises(FieldRequiredException) as e:
        song_service.create(files, data)

    assert str(e.value) == "title is required"
    mocked_process_files_to_streams.assert_not_called()
    mocked_thread.start.assert_not_called()


def test_negative_create_song_song_file_required(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
    mocked_process_files_to_streams: Callable,
    mocked_thread: Thread,
):
    data = {
        "title": "test",
    }
    files = {}

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    with pytest.raises(FieldRequiredException) as e:
        song_service.create(files, data)

    assert str(e.value) == "song_file is required"
    mocked_process_files_to_streams.assert_not_called()
    mocked_thread.start.assert_not_called()


def test_positive_update_song(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
    mocked_process_files_to_streams: Callable,
    mocked_thread: Thread,
    mocked_current_user: User,
):
    mocked_current_user.id = 1
    mocked_song_repository.get_by_id.return_value.user_id = 1

    data = {
        "title": "test",
    }
    files = {
        "song_file": mock.MagicMock(),
        "small_thumbnail_file": mock.MagicMock(),
        "large_thumbnail_file": mock.MagicMock(),
    }

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service.update(mocked_current_user, 1, files, data)

    mocked_song_repository.get_by_id.assert_called_once_with(1)
    mocked_process_files_to_streams.assert_called_once()
    mocked_thread.start.assert_called_once()


def test_positive_update_song_skip_optional_fields(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
    mocked_process_files_to_streams: Callable,
    mocked_thread: Thread,
    mocked_current_user: User,
):
    mocked_current_user.id = 1
    mocked_song_repository.get_by_id.return_value.user_id = 1
    data = {
        "title": "test",
    }
    files = {
        "song_file": mock.MagicMock(),
        "small_thumbnail_file": FileStorage(None, ""),
        "large_thumbnail_file": FileStorage(None, ""),
    }

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service.update(mocked_current_user, 1, files, data)

    mocked_song_repository.get_by_id.assert_called_once_with(1)
    mocked_process_files_to_streams.assert_called_once()
    mocked_thread.start.assert_called_once()


def test_negative_update_song_not_found(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
    mocked_process_files_to_streams: Callable,
    mocked_thread: Thread,
):
    mocked_song_repository.get_by_id.return_value = None
    mocked_current_user.id = 1
    data = {
        "title": "test",
    }
    files = {
        "song_file": mock.MagicMock(),
        "small_thumbnail_file": mock.MagicMock(),
        "large_thumbnail_file": mock.MagicMock(),
    }

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    with pytest.raises(NotFoundException):
        song_service.update(mocked_current_user, 1, files, data)

    mocked_song_repository.get_by_id.assert_called_once_with(1)
    mocked_process_files_to_streams.assert_not_called()
    mocked_thread.start.assert_not_called()


def test_negative_update_song_unauthorized(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
    mocked_process_files_to_streams: Callable,
    mocked_thread: Thread,
    mocked_current_user: User,
):
    mocked_current_user.id = 1
    mocked_song_repository.get_by_id.return_value.user_id = 2
    data = {
        "title": "test",
    }
    files = {
        "song_file": mock.MagicMock(),
        "small_thumbnail_file": mock.MagicMock(),
        "large_thumbnail_file": mock.MagicMock(),
    }

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    with pytest.raises(UnauthorizedException) as e:
        song_service.update(mocked_current_user, 1, files, data)

    assert str(e.value) == UNAUTHORIZED_TO_UPDATE_SONG
    mocked_song_repository.get_by_id.assert_called_once_with(1)
    mocked_process_files_to_streams.assert_not_called()
    mocked_thread.start.assert_not_called()


def test_positive_delete(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
    mocked_current_user: User,
):
    mocked_current_user.id = 1
    mocked_song_repository.get_by_id.return_value.user_id = 1
    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service.delete(mocked_current_user, 1)

    mocked_song_repository.get_by_id.assert_called_once()
    mocked_song_repository.delete.assert_called_once()


def test_negative_delete_song_not_found(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
    mocked_current_user: User,
):
    mocked_song_repository.get_by_id.return_value = None

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    with pytest.raises(NotFoundException):
        song_service.delete(mocked_current_user, 1)

    mocked_song_repository.get_by_id.assert_called_once()
    mocked_song_repository.delete.assert_not_called()


def test_negative_delete_song_unauthorized(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
    mocked_current_user: User,
):
    mocked_current_user.id = 1
    mocked_song_repository.get_by_id.return_value.user_id = 2

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    with pytest.raises(UnauthorizedException) as e:
        song_service.delete(mocked_current_user, 1)

    assert str(e.value) == UNAUTHORIZED_TO_DELETE_SONG
    mocked_song_repository.get_by_id.assert_called_once()
    mocked_song_repository.delete.assert_not_called()


def test_positive_song_get_by_id(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
):
    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service.get_by_id(1)

    mocked_song_repository.get_by_id.assert_called_once_with(1)


def test_negative_song_get_by_id_not_found(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
):
    mocked_song_repository.get_by_id.return_value = None

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    with pytest.raises(NotFoundException):
        song_service.get_by_id(1)

    mocked_song_repository.get_by_id.assert_called_once()


def test_positive_get_all(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
):
    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service.get_all()

    mocked_song_repository.get_all.assert_called_once()


def test_positive_get_all_with_take_skip(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
):
    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service.get_all(10, 10)

    mocked_song_repository.get_all.assert_called_once_with(10, 10)


def test_positive_private_create(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
):
    data = {
        "title": "test",
    }
    files = {
        "song_file": mock.MagicMock(),
        "small_thumbnail_file": mock.MagicMock(),
        "large_thumbnail_file": mock.MagicMock(),
    }

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service._create(files, data)

    mocked_app.app_context.assert_called_once()
    mocked_song_repository.create.assert_called_once()
    assert mocked_upload_file.call_count == 3


def test_positive_private_update(
    mocked_app: Flask,
    mocked_song_repository: SongRepository,
    mocked_upload_file: Callable,
):
    data = {
        "title": "test",
    }
    files = {
        "song_file": mock.MagicMock(),
        "small_thumbnail_file": mock.MagicMock(),
        "large_thumbnail_file": mock.MagicMock(),
    }

    song_service = SongService(mocked_app, mocked_song_repository, mocked_upload_file)

    song_service._update(1, files, data)

    mocked_app.app_context.assert_called_once()
    mocked_song_repository.update.assert_called_once()
    assert mocked_upload_file.call_count == 3
