from ..service import Service
from ..exception import AppwriteException

class Health(Service):

    def __init__(self, client):
        super(Health, self).__init__(client)

    def get(self):
        """Get HTTP"""

        params = {}
        path = '/health'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)

    def get_antivirus(self):
        """Get Antivirus"""

        params = {}
        path = '/health/anti-virus'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)

    def get_cache(self):
        """Get Cache"""

        params = {}
        path = '/health/cache'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)

    def get_db(self):
        """Get DB"""

        params = {}
        path = '/health/db'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)

    def get_queue_certificates(self):
        """Get Certificates Queue"""

        params = {}
        path = '/health/queue/certificates'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)

    def get_queue_functions(self):
        """Get Functions Queue"""

        params = {}
        path = '/health/queue/functions'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)

    def get_queue_logs(self):
        """Get Logs Queue"""

        params = {}
        path = '/health/queue/logs'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)

    def get_queue_webhooks(self):
        """Get Webhooks Queue"""

        params = {}
        path = '/health/queue/webhooks'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)

    def get_storage_local(self):
        """Get Local Storage"""

        params = {}
        path = '/health/storage/local'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)

    def get_time(self):
        """Get Time"""

        params = {}
        path = '/health/time'


        return self.client.call('get', path, {
            'content-type': 'application/json',
        }, params)
