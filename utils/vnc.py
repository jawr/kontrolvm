from django.utils import timezone
from threading import Thread, Event
from apps.vnc.models import Session
from utils.singleton import SingletonType
from datetime import timedelta
import socket
import time

# need to wrap in mutex locks
class VNCSessions(Thread):
  __metaclass__ = SingletonType
  
  def __init__(self):
    Thread.__init__(self)
    self.setDaemon(True)
    self.sessions = {}

  def count(self):
    return len(self.sessions)
  
  def get(self, key):
    if key in self.sessions:
      return self.sessions[key]
    return None

  def set(self, key, proxy):
    self.sessions[key] = proxy

  def heartbeat(self, key):
    proxy = self.get(key)
    if proxy:
      proxy.heartbeat()

  def stop(self, key):
    proxy = self.get(key)
    if proxy:
      proxy.stop()
      del self.sessions[key]
      del proxy
      

class ProxyPipe(Thread):
  pipes = [] # static

  def __init__(self, source, sink, port, parent):
    Thread.__init__(self)
    self.setDaemon(True)
    self.source = source
    self.sink = sink
    self.port = port
    self.parent = parent
    self._heartbeat = False
    self._stop = Event()
    ProxyPipe.pipes.append(self)

  def stop(self):
    print "STOP PROXYPIPE"
    self._stop.set()

  def run(self):
    self.last_check = int(time.time())
    while not self._stop.is_set():
      if (int(time.time()) - self.last_check) > 25:
        if not self._heartbeat:
          self.parent.stop()
          break 
        self._heartbeat = False
        self.last_check = int(time.time())
      try:
        data = self.source.recv(1024)
        if not data: break
        self.sink.send(data)
      except:
        break
    self.cleanup()

  def heartbeat(self):
    self._heartbeat = True

  def cleanup(self):
    self.sink.close()
    self.source.close()
    try:
      print "CLEANUP PROXYPIPE"
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
    self.pipe1 = None
    self.pipe2 = None
    self._stop = Event()
    Proxy.listeners.append(self)

  def stop(self):
    print "STOP PROXY"
    print self.pipe1
    print self.pipe2
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
    if self.pipe1: 
      self.pipe1.heartbeat()
    if self.pipe2:
      self.pipe2.heartbeat()
