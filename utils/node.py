import requests
import simplejson

def send_command(hypervisor, command, args):
  addr = '%s/cmd/' % (hypervisor.node_address)
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  payload = {'command': command, 'args': args}
  try:
    result = requests.post(addr, data=simplejson.dumps(payload), headers=headers)
    return result.text
  except Exception:
    return None

def check_command(hypervisor, task_id):
  addr = '%s/cmd/status/%s/' % (hypervisor.node_address, task_id)
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  try:
    result = requests.get(addr)
    if result.status_code == 200:
      return simplejson.loads(result.text)
  except Exception:
    pass
  return {'state': 'ERROR'}

def abort_command(hypervisor, task_id):
  addr = '%s/cmd/abort/%s/' % (hypervisor.node_address, task_id)
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  try:
    result = requests.get(addr)
    if result.status_code == 200:
      return simplejson.loads(result.text)
  except Exception:
    pass
  return {'state': 'ERROR'}
