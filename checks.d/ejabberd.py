# Datadog Agent Check Plugin for Ejabberd
# debug for:
# sudo -u dd-agent dd-agent check ejabberd
# In docker:
# /opt/datadog-agent/agent/agent.py check ejabberd

from checks import AgentCheck
from requests import post

def get_connected_users(url, auth, headers):
    res = post(url + '/connected_users', '{}', auth=auth, headers=headers)
    obj = res.json()
    return obj

def get_stats(url, name, auth, headers):
    data = '{"name":"%s"}' % (name)
    res = post(url + '/stats', data, auth=auth, headers=headers)
    obj = res.json()
    return obj['stat']

def get_incoming_s2s_number(url, auth, headers):
    res = post(url + '/incoming_s2s_number', '{}', auth=auth, headers=headers)
    obj = res.json()
    return obj['s2s_incoming']

def get_outgoing_s2s_number(url, auth, headers):
    res = post(url + '/outgoing_s2s_number', '{}', auth=auth, headers=headers)
    obj = res.json()
    return obj['s2s_outgoing']

class EjabberdCheck(AgentCheck):
    SERVICE_CHECK_NAME = 'ejabberd.is_ok'

    def __init__(self, name, init_config, agentConfig, instances=None):
        AgentCheck.__init__(self, name, init_config, agentConfig, instances)

    def check(self, instance):
        verbose = self.init_config.get('verbose', False)
        connected_users = self.init_config.get('connected_users', False)
        if 'jid' in instance and 'password' in instance:
            auth = (instance['jid'], instance['password'])
        else:
            auth = None
        try:
            headers = {'X-Admin' : 'true'}
            if connected_users:
              res = get_connected_users(instance['url'], auth, headers)
              for user in res:
                self.gauge('ejabberd.connected_' + user, 1)
            res = get_stats(instance['url'], 'registeredusers', auth, headers)
            self.gauge('ejabberd.registeredusers', res)
            res = get_stats(instance['url'], 'onlineusers', auth, headers)
            self.gauge('ejabberd.onlineusers', res)
            res = get_stats(instance['url'], 'onlineusersnode', auth, headers)
            self.gauge('ejabberd.onlineusersnode', res)
            res = get_stats(instance['url'], 'processes', auth, headers)
            self.gauge('ejabberd.processes', res)
            res = get_incoming_s2s_number(instance['url'], auth, headers)
            self.gauge('ejabberd.s2s_incoming', res)
            res = get_outgoing_s2s_number(instance['url'], auth, headers)
            self.gauge('ejabberd.s2s_outgoing', res)
            self.service_check(self.SERVICE_CHECK_NAME, AgentCheck.OK)
        except Exception as e:
            self.service_check(self.SERVICE_CHECK_NAME, AgentCheck.CRITICAL,
                               message="Unable to get ejabberd Stats: %s"
                               % str(e))
