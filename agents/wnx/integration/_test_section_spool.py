#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset: 4 -*-
import os
import platform
import pytest
import re
from local import (actual_output, make_ini_config, local_test, src_exec_dir, wait_agent,
                   write_config)


class Globals(object):
    section = 'spool'
    alone = True
    test_message = 'Test message'
    outdated = False


@pytest.fixture
def testfile():
    return os.path.basename(__file__)


@pytest.fixture(params=['alone', 'with_systemtime'])
def testconfig(request, make_ini_config):
    Globals.alone = request.param == 'alone'
    if Globals.alone:
        make_ini_config.set('global', 'sections', Globals.section)
    else:
        make_ini_config.set('global', 'sections', '%s systemtime' % Globals.section)
    make_ini_config.set('global', 'crash_debug', 'yes')
    return make_ini_config


@pytest.fixture
def expected_output():
    expected = []
    if not Globals.outdated:
        expected += [r'%s' % Globals.test_message]
    if not Globals.alone:
        expected += [re.escape(r'<<<systemtime>>>'), r'\d+']
    return expected


@pytest.fixture(params=['yes', 'no'], ids=['outdated', 'not_outdated'], autouse=True)
def manage_spoolfile(request):
    Globals.outdated = request.param == 'yes'
    testfile = '0testfile' if request.param == 'yes' else 'testfile'
    filename = os.path.join(src_exec_dir, Globals.section, testfile)
    if platform.system() == 'Windows':
        spooldir = os.path.join(src_exec_dir, Globals.section)
        try:
            os.mkdir(spooldir)
        except OSError:
            pass  # Directory may already exist.
        with open(filename, 'w') as f:
            f.write('%s' % Globals.test_message)
        # Hack the modification time 2 s back in time
        stat = os.stat(filename)
        times = stat.st_atime, stat.st_mtime - 2
        os.utime(filename, times)

    yield

    if platform.system() == 'Windows':
        os.unlink(filename)


def test_section_spool(request, testconfig, expected_output, actual_output, testfile):
    # request.node.name gives test name
    local_test(expected_output, actual_output, testfile, request.node.name)
