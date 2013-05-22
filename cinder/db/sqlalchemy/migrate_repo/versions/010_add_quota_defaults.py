# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
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

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import MetaData, Integer, String, Table, ForeignKey

from cinder.openstack.common import log as logging


LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    # New table
    quota_defaults = Table('quota_defaults', meta,
                           Column('created_at', DateTime(timezone=False)),
                           Column('updated_at', DateTime(timezone=False)),
                           Column('deleted_at', DateTime(timezone=False)),
                           Column('deleted', Boolean(create_constraint=True,
                                                     name=None)),
                           Column('id', Integer(), primary_key=True),
                           Column('resource',
                                  String(length=255,
                                         convert_unicode=True,
                                         unicode_error=None,
                                         _warn_on_bytestring=False)),
                           Column('hard_limit', Integer(), nullable=True),
                           mysql_engine='InnoDB',
                           mysql_charset='utf8',
                           )

    try:
        quota_defaults.create()
    except Exception:
        LOG.error(_("Table |%s| not created!"), repr(quota_defaults))
        raise


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    quota_defaults = Table('quota_defaults', meta, autoload=True)
    try:
        quota_defaults.drop()
    except Exception:
        LOG.error(_("quota_defaults table not dropped"))
        raise
