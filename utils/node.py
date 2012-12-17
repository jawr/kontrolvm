import requests
import simplejson

def send_command(hypervisor, command, args):
  print hypervisor
  print hypervisor.node_address
  addr = '%s/cmd/' % (hypervisor.node_address)
  print addr
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  payload = {'command': command, 'args': args}
  result = requests.post(addr, data=simplejson.dumps(payload), headers=headers)

  return result.text

def check_command(hypervisor, task_id):
  addr = '%s/cmd/%s/' % (hypervisor.node_address, task_id)
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  result = requests.get(addr)
  print result.text
  return result.text
