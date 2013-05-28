# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
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

import webob

from cinder.api import extensions
from cinder.api.openstack import wsgi
from cinder.api import xmlutil
from cinder import db
from cinder import exception
from cinder import quota


QUOTAS = quota.QUOTAS


class QuotaDefaultTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('quota_default')
        root.set('resource')
        root.set('limit')

        return xmlutil.MasterTemplate(root, 1)


class QuotaDefaultsController(object):

    def authorize(self, context, action_name):
        action = 'quota_defaults:%s' % action_name
        extensions.extension_authorizer('volume', action)(context)

    def _validate_limit(self, limit_):
        # NOTE: -1 is a flag value for unlimited
        msg = _("Quota limit must be integer -1 or greater.")
        try:
            limit = int(limit_)
        except ValueError:
            raise webob.exc.HTTPBadRequest(explanation=msg)

        if limit < -1:
            raise webob.exc.HTTPBadRequest(explanation=msg)
        return limit

    @wsgi.serializers(xml=QuotaDefaultTemplate)
    def show(self, req, id):
        context = req.environ['cinder.context']
        self.authorize(context, 'show')
        resource = id
        try:
            default = db.quota_default_get(context, resource)
        except exception.QuotaDefaultNotFound:
            msg = _("Resource not found: %s") % resource
            raise webob.exc.HTTPNotFound(explanation=msg)
        except exception.NotAuthorized:
            raise webob.exc.HTTPForbidden()

        return {
            'quota_default': {
                'resource': resource,
                'limit': default.hard_limit
            }
        }

    @wsgi.serializers(xml=QuotaDefaultTemplate)
    def update(self, req, id, body):
        context = req.environ['cinder.context']
        self.authorize(context, 'update')
        resource = id
        try:
            print body
            quota_default = body['quota_default']
        except KeyError:
            msg = _("Incorrect request body format")
            raise webob.exc.HTTPBadRequest(explanation=msg)

        limit = self._validate_limit(quota_default.get('limit'))
        try:
            db.quota_default_update(context, resource, limit)
        except exception.QuotaDefaultNotFound:
            db.quota_default_create(context, resource, limit)
        except exception.AdminRequired:
            raise webob.exc.HTTPForbidden()

        return {
            'quota_default': {
                'resource': resource,
                'limit': limit
            }
        }


class Quota_defaults(extensions.ExtensionDescriptor):
    """Quota default management support"""

    name = "QuotaDefaults"
    alias = "os-quota-defaults"
    namespace = ("http://docs.openstack.org/volume/ext/"
                 "quota-defaults/api/v1.1")
    updated = "2012-03-12T00:00:00+00:00"

    def get_resources(self):
        resources = []

        res = extensions.ResourceExtension('os-quota-defaults',
                                           QuotaDefaultsController())
        resources.append(res)

        return resources
