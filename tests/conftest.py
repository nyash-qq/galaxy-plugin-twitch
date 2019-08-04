import pytest


@pytest.fixture()
def os_path_exists_mock(mocker):
    return mocker.patch("os.path.exists")
