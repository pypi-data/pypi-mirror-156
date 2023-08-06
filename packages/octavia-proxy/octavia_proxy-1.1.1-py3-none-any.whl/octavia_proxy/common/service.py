# Copyright 2014 Rackspace
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from pathlib import Path

from oslo_config import cfg

from octavia_proxy.common import config


def prepare_service(argv=None):
    """Sets global config from config file and sets up logging."""
    argv = argv or []
    config_file = '/etc/octavia_proxy/octavia_proxy.conf'
    kwargs = dict()
    if Path(config_file).is_file():
        kwargs['default_config_files'] = [config_file]
    config.init(
        argv[1:],
        **kwargs
    )
    config.setup_logging(cfg.CONF)
