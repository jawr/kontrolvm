from threading import Thread, Event
import socket

class ProxyPipe(Thread):
  pipes = [] # static

  def __init__(self, source, sink, port):
    Thread.__init__(self)
    self.source = source
    self.sink = sink
    self.port = port
    self._stop = Event()
    ProxyPipe.pipes.append(self)

  def stop(self):
    self._stop.set()

  def run(self):
    while not self._stop.is_set():
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

  def stop(self):
    self._stop.set()

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
    self._stop = Event()
    Proxy.listeners.append(self)

  def stop(self):
    self._stop.set()

  def run(self):
    print "Running, listening on %s:%d" % (self.listen_host, self.listen_port)
    print "Forwarding to: %s:%d" % (self.dest_host, self.dest_port)
    while not self._stop.is_set():
      newsock, address = self.sock.accept()
      forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      forward.connect((self.dest_host, self.dest_port))
      self.pipe1 = ProxyPipe(newsock, forward, self.dest_port).start()
      self.pipe2 = ProxyPipe(forward, newsock, self.dest_port).start()
    if self.pipe1: self.pipe1.stop()
    if self.pipe2: self.pipe2.stop()
