import requests
import simplejson

def send_command(hypervisor, command, args):
  addr = '%s/cmd/' % (hypervisor.node_address)
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  payload = {'command': command, 'args': args}
  result = requests.post(addr, data=simplejson.dumps(payload), headers=headers)
  return result.text

def check_command(hypervisor, task_id):
  addr = '%s/cmd/status/%s/' % (hypervisor.node_address, task_id)
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  result = requests.get(addr)
  print result.status_code
  print result.text
  if result.status_code == 200:
    return simplejson.loads(result.text)
  return {'state': 'ERROR'}

def abort_command(hypervisor, task_id):
  addr = '%s/cmd/abort/%s/' % (hypervisor.node_address, task_id)
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  result = requests.get(addr)
  if result.status_code == 200:
    return simplejson.loads(result.text)
  return {'state': 'ERROR'}
