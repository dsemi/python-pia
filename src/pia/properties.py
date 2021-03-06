# -*- coding: utf-8 -*-

#    Private Internet Access Configuration auto-configures VPN files for PIA
#    Copyright (C) 2016  Jesse Spangenberger <azulephoenix[at]gmail[dot]com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from configparser import ConfigParser
from pia.applications import Application


class Props(object):
    """Global properties class.

    Attributes:
        login_config: path to where VPN login credentials are stored
        progs: list of supported programs
        apps: dictionary of application objects that will be configured
    """
    _login_config = '/etc/private-internet-access/login.conf'
    _conf_file = '/etc/private-internet-access/pia.conf'
    _hosts = []

    def __init__(self):
        self._exclude_apps = None

    @property
    def conf_file(self):
        return self._conf_file

    @property
    def login_config(self):
        """path to where VPN login credentials are stored"""
        return self._login_config

    @property
    def hosts(self):
        return self._hosts

    @hosts.setter
    def hosts(self, value):
        self._hosts = value

class _Parser(object):
    """attributes may need additional manipulation"""

    def __init__(self, section):
        """section to return all options on, formatted as an object
        transforms all comma-delimited options to lists
        comma-delimited lists with colons are transformed to dicts
        dicts will have values expressed as lists, no matter the length
        """
        c = ConfigParser()
        c.read(props.conf_file)

        self.section_name = section

        self.__dict__.update({k: v for k, v in c.items(section)})

        # transform all ',' into lists, all ':' into dicts
        for key, value in self.__dict__.items():
            if value.find(':') > 0:
                # dict
                values = value.split(',')
                dicts = [{k: v} for k, v in [d.split(':') for d in values]]
                merged = {}
                for d in dicts:
                    for k, v in d.items():
                        merged.setdefault(k, []).append(v)
                self.__dict__[key] = merged
            elif value.find(',') > 0:
                # list
                self.__dict__[key] = value.split(',')
            else:
                self.__dict__[key] = [value]


def parse_conf_file():
    """Parses configure file 'pia.conf' using the Parser Class"""
    pia_section = _Parser("pia")
    configure_section = _Parser("configure")

    if getattr(pia_section, "openvpn_auto_login", None):
        Application.set_option(getattr(props, 'openvpn'), autologin=pia_section.openvpn_auto_login)

    if getattr(configure_section, "apps", None):
        for app in configure_section.apps:
            Application.set_option(getattr(props, app), configure=True)

    if getattr(configure_section, "hosts", None):
        props.hosts = configure_section.hosts


props = Props()  # creates global property object
