from django.utils import timezone
from threading import Thread, Event
from apps.vnc.models import Session
from datetime import timedelta
import socket
import time

class ProxyPipe(Thread):
  pipes = [] # static

  def __init__(self, source, sink, port, parent):
    Thread.__init__(self)
    self.setDaemon(True)
    self.source = source
    self.sink = sink
    self.port = port
    self.parent = parent
    self.stop = True
    self._stop = Event()
    ProxyPipe.pipes.append(self)

  def stop(self):
    self._stop.set()

  def run(self):
    self.last_check = int(time.time())
    while not self._stop.is_set():
      if (int(time.time()) - self.last_check) > 15:
        print "Checking..."
        if self.stop:
          print "GOT STOP"
          self.parent.stop()
          break
        print "BIZNISS"
        self.stop = True
        self.last_check = int(time.time())
      try:
        data = self.source.recv(1024)
        if not data: break
        self.sink.send(data)
      except:
        break
    self.cleanup()
    print "Closing ProxyPipe down..."

  def heartbeat(self):
    print "HEARTBEAT"
    self.stop = False

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
  def __init__(self, listen_host, listen_port, dest_host, dest_port, session):
    Thread.__init__(self)
    self.setDaemon(True)
    self.listen_port = listen_port
    self.listen_host = listen_host
    self.dest_host = dest_host
    self.dest_port = dest_port
    self.session = session

    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((self.listen_host, self.listen_port))
    self.sock.listen(5) #connection queue
    self._stop = Event()
    Proxy.listeners.append(self)

  def stop(self):
    if self.pipe1: self.pipe1.stop()
    if self.pipe2: self.pipe2.stop()
    self._stop.set()

  def run(self):
    print "Running, listening on %s:%d" % (self.listen_host, self.listen_port)
    print "Forwarding to: %s:%d" % (self.dest_host, self.dest_port)
    while not self._stop.is_set():
      newsock, address = self.sock.accept()
      forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      forward.connect((self.dest_host, self.dest_port))
      self.pipe1 = ProxyPipe(newsock, forward, self.dest_port, self)
      self.pipe1.start()
      self.pipe2 = ProxyPipe(forward, newsock, self.dest_port, self)
      self.pipe2.start()
    if self.pipe1:
      self.pipe1.join()
    if self.pipe2:
      self.pipe2.join()
    self.session.active = False
    self.session.save()
    print "Closing Proxy down..."

  def heartbeat(self):
    print "HELLO"
    if self.pipe1: self.pipe1.heartbeat()
    if self.pipe2: self.pipe2.heartbeat()
