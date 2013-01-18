from threading import Thread
import socket

class ProxyPipe(Thread):
  pipes = [] # static

  def __init__(self, source, sink, port):
    Thread.__init__(self)
    self.source = source
    self.sink = sink
    self.port = port
    ProxyPipe.pipes.append(self)

  def run(self):
    while 1:
      try:
        data = self.source.recv(1024)
        if not data: break
        self.sink.send(data)
      except:
        break
    self.cleanup()

  def cleanup(self):
    self.sink.close()
    self.source.close()
    try:
      ProxyPipe.pipes.remove(self)
    except ValueError:
      pass

class Proxy(Thread):
  listeners = []
  def __init__(self, listen_host, listen_port, dest_host, dest_port):
    Thread.__init__(self)
    self.listen_port = listen_port
    self.listen_host = listen_host
    self.dest_host = dest_host
    self.dest_port = dest_port

    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((self.listen_host, self.listen_port))
    self.sock.listen(5) #connection queue
    Proxy.listeners.append(self)

  """ This needs to deactivate the Model in the db """
  def cleanup(self):
    print 'deleting proxy ' + str(self.dest_port)
    vnc_gate.close_gate(self.dest_port)
    for pipe in ProxyPipe.pipes:
      if pipe.port == self.dest_port:
        pipe.cleanup()
        del pipe
    self.sock.close()
    try:
      ProxyPipe.pipes.remove(self)
    except ValueError:
      pass

  def run(self):
    print "Running, listening on %s:%d" % (self.listen_host, self.listen_port)
    print "Forwarding to: %s:%d" % (self.dest_host, self.dest_port)
    while 1:
      newsock, address = self.sock.accept()
      forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      forward.connect((self.dest_host, self.dest_port))
      print 'got new connection from'
      print address
      ProxyPipe(newsock, forward, self.dest_port).start()
      ProxyPipe(forward, newsock, self.dest_port).start()
