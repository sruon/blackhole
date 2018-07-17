# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2013-2018 Kura
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# pylama:skip=1

import os

from unittest import mock

import pytest

from pyannotate_runtime import collect_types

from blackhole.daemon import Daemon, DaemonException

from ._utils import Args, cleandir, create_config, create_file, reset


@pytest.mark.usefixtures("reset", "cleandir")
def test_instantiated_but_not_daemonised():
    collect_types.init_types_collection()
    collect_types.resume()
    pid = os.path.join(os.getcwd(), "fake.pid")
    with mock.patch("os.getpid", return_value=666):
        daemon = Daemon(pid)
        assert daemon.pidfile == pid
        assert daemon.pid == 666
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_set_pid_invalid_path():
    collect_types.init_types_collection()
    collect_types.resume()
    with mock.patch("os.path.exists", return_value=False), mock.patch(
        "atexit.register"
    ), pytest.raises(DaemonException):
        Daemon("/fake/path.pid")
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_set_pid_valid_path():
    collect_types.init_types_collection()
    collect_types.resume()
    pid = os.path.join(os.getcwd(), "fake.pid")
    with mock.patch("os.getpid", return_value=666), mock.patch(
        "atexit.register"
    ):
        daemon = Daemon(pid)
        assert daemon.pidfile == pid
        assert daemon.pid == 666
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_get_pid_file_error():
    collect_types.init_types_collection()
    collect_types.resume()
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch(
            "builtins.open", side_effect=FileNotFoundError
        ), mock.patch("atexit.register"), pytest.raises(DaemonException):
            Daemon("/fake/path.pid")
        with mock.patch("builtins.open", side_effect=IOError), mock.patch(
            "atexit.register"
        ), pytest.raises(DaemonException):
            Daemon("/fake/path.pid")
        with mock.patch(
            "builtins.open", side_effect=PermissionError
        ), mock.patch("atexit.register"), pytest.raises(DaemonException):
            Daemon("/fake/path.pid")
        with mock.patch("builtins.open", side_effect=OSError), mock.patch(
            "atexit.register"
        ), pytest.raises(DaemonException):
            Daemon("/fake/path.pid")
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_get_pid():
    collect_types.init_types_collection()
    collect_types.resume()
    pfile = create_file("test.pid", 123)
    with mock.patch("os.getpid", return_value=123), mock.patch(
        "atexit.register"
    ):
        daemon = Daemon(pfile)
        assert daemon.pid is 123
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_delete_pid_no_exists():
    collect_types.init_types_collection()
    collect_types.resume()
    pfile = create_file("test.pid", 123)
    daemon = Daemon(pfile)
    with mock.patch("os.remove") as mock_rm, mock.patch(
        "atexit.register"
    ), mock.patch("os.path.exists", return_value=False):
        del daemon.pid
    assert mock_rm.called is False
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_delete_pid():
    collect_types.init_types_collection()
    collect_types.resume()
    pfile = create_file("test.pid", 123)
    with mock.patch("os.getpid", return_value=123), mock.patch(
        "atexit.register"
    ):
        daemon = Daemon(pfile)
        assert daemon.pid is 123
        del daemon.pid
        assert daemon.pid is None
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_delete_pid_exit():
    collect_types.init_types_collection()
    collect_types.resume()
    pfile = create_file("test.pid", 123)
    with mock.patch("os.getpid", return_value=123), mock.patch(
        "atexit.register"
    ):
        daemon = Daemon(pfile)
        assert daemon.pid is 123
        daemon._exit()
        assert daemon.pid is None
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_fork():
    collect_types.init_types_collection()
    collect_types.resume()
    pfile = create_file("test.pid", 123)
    with mock.patch("atexit.register"):
        daemon = Daemon(pfile)
    with mock.patch("os.fork", return_value=9999) as mock_fork, mock.patch(
        "os._exit"
    ) as mock_exit:
        daemon.fork()
    assert mock_fork.called is True
    assert mock_exit.called is True
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_fork_error():
    collect_types.init_types_collection()
    collect_types.resume()
    pfile = create_file("test.pid", 123)
    with mock.patch("atexit.register"):
        daemon = Daemon(pfile)
    with mock.patch(
        "os.fork", side_effect=OSError
    ) as mock_fork, pytest.raises(DaemonException):
        daemon.fork()
    assert mock_fork.called is True
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")


@pytest.mark.usefixtures("reset", "cleandir")
def test_daemonise():
    collect_types.init_types_collection()
    collect_types.resume()
    pfile = create_file("test.pid", 123)
    with mock.patch("blackhole.daemon.Daemon.fork") as mock_fork, mock.patch(
        "os.chdir"
    ) as mock_chdir, mock.patch("os.setsid") as mock_setsid, mock.patch(
        "os.umask"
    ) as mock_umask, mock.patch(
        "atexit.register"
    ) as mock_atexit, mock.patch(
        "os.getpid", return_value=123
    ):
        daemon = Daemon(pfile)
        daemon.daemonize()
    assert mock_fork.called is True
    assert mock_chdir.called is True
    assert mock_setsid.called is True
    assert mock_umask.called is True
    assert mock_atexit.called is True
    collect_types.pause()
    collect_types.dump_stats("/tmp/annotations")
