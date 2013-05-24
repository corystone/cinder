import shutil
import tempfile
import webob

from cinder import context
from cinder import db
from cinder import exception
from cinder.openstack.common import jsonutils
from cinder import test
from cinder.tests.api import fakes
from cinder.tests.api.v2 import stubs


def app():
    # no auth, just let environ['cinder.context'] pass through
    api = fakes.router.APIRouter()
    mapper = fakes.urlmap.URLMap()
    mapper['/v2'] = api
    return mapper


class QuotaDefaultsTest(test.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        super(QuotaDefaultsTest, self).setUp()
        self.flags(rpc_backend='cinder.openstack.common.rpc.impl_fake')
        self.flags(lock_path=self.tempdir)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_show_non_admin(self):
        # admin context
        admin_ctx = context.RequestContext('admin', 'fake', True)
        nonadmin_ctx = context.RequestContext('nonadmin', 'fake2', False)
        quota_default = db.quota_default_create(admin_ctx, 'volumes', 1)
        req = webob.Request.blank('/v2/fake2/os-quota-defauts/volumes')
        req.method = 'POST'
        req.headers['content-type'] = 'application/json'
        req.environ['cinder.context'] = nonadmin_ctx
        resp = req.get_response(app())
        self.assertEquals(resp.status_int, 202)
        body = jsonutils.loads(resp.body)
        self.assertEquals(body['quota_default'],
                          {'resource': 'volumes', 'limit': 1})
