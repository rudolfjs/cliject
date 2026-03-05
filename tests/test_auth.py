import subprocess

import pytest

from cliject.auth import get_token, get_viewer_login


def test_get_token_success(mocker):
    mock_run = mocker.patch("cliject.auth.subprocess.run")
    mock_run.return_value = mocker.Mock(stdout="gho_TOKEN123\n")
    assert get_token() == "gho_TOKEN123"
    mock_run.assert_called_once_with(["gh", "auth", "token"], capture_output=True, text=True, check=True)


def test_get_token_strips_whitespace(mocker):
    mock_run = mocker.patch("cliject.auth.subprocess.run")
    mock_run.return_value = mocker.Mock(stdout="  gho_TOKEN123  \n")
    assert get_token() == "gho_TOKEN123"


def test_get_token_gh_not_found(mocker):
    mocker.patch("cliject.auth.subprocess.run", side_effect=FileNotFoundError)
    with pytest.raises(FileNotFoundError):
        get_token()


def test_get_token_auth_failure(mocker):
    mocker.patch(
        "cliject.auth.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "gh"),
    )
    with pytest.raises(subprocess.CalledProcessError):
        get_token()


def test_get_viewer_login_success(mocker):
    mock_run = mocker.patch("cliject.auth.subprocess.run")
    mock_run.return_value = mocker.Mock(stdout="alice\n")
    assert get_viewer_login() == "alice"
    mock_run.assert_called_once_with(
        ["gh", "api", "user", "--jq", ".login"],
        capture_output=True,
        text=True,
        check=True,
    )


def test_get_viewer_login_strips_whitespace(mocker):
    mock_run = mocker.patch("cliject.auth.subprocess.run")
    mock_run.return_value = mocker.Mock(stdout="  bob  \n")
    assert get_viewer_login() == "bob"
