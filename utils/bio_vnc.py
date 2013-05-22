from threading import Thread, Event, Lock
import select
import socket
import time
import os

class ProxyConnection(Thread):
  def __init__(self, client_sock, dest_host, dest_port, server):
    Thread.__init__(self)
    self._interrupt = None
    self._client_sock = client_sock
    self._client_buffer = ""
    self._server_sock = None
    self._server_buffer = ""
    self._dest_host = dest_host
    self._dest_port = dest_port
    self._server = server
    self._last_client_recv = 0
    self._client_timeout = 30
   
  def try_join(self):
    self.join(0)
    return not self.isAlive()
   
  def start(self):
    self._interrupt = os.pipe()
    Thread.start(self)
   
  def interrupt(self):
    os.write(self._interrupt[1], ' ')
   
  def run(self):
    try:
      # create our connection to the server
      self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self._server_sock.connect((self._dest_host, self._dest_port))
     
      self._client_sock.setblocking(False)
      self._server_sock.setblocking(False)
     
      self._last_client_recv = time.time()
      read_set = [self._interrupt[0], self._client_sock, self._server_sock]
      write_set = []
      while True:
        # wait for data to read
        timeout = self._client_timeout - (time.time() - self._last_client_recv)
        readable, writeable, _ = select.select(read_set, write_set, [], timeout)
       
        # check for client timeout
        if len(readable) == 0 and len(writeable) == 0:
          break
         
        # read data from client, putting in server's write buffer
        if self._client_sock in readable:
          buf = self._client_sock.recv(4096)
          if len(buf) == 0:
            break
         
          # if buffer was empty, need to watch for wrteable socket again
          if len(self._server_buffer) == 0:
            write_set.append(self._server_sock)
           
          # push onto buffer
          self._server_buffer += buf
          self._last_client_recv = time.time()
         
        # read data from server, putting in client's write buffer
        if self._server_sock in readable:
          buf = self._server_sock.recv(4096)
          if len(buf) == 0:
            break
         
          # if buffer was empty, need to watch for wrteable socket again
          if len(self._client_buffer) == 0:
            write_set.append(self._client_sock)
         
          # push onto buffer
          self._client_buffer += buf
       
        # write data to the client, out of it's buffer
        if self._client_sock in writeable:
          bytes = self._client_sock.send(self._client_buffer)
          self._client_buffer = self._client_buffer[bytes:]
 
          # stop watching for writeable socket now buffer is empty
          if len(self._client_buffer) == 0:
            write_set.remove(self._client_sock)
       
        # write data to the server, out of it's buffer
        if self._server_sock in writeable:
          bytes = self._server_sock.send(self._server_buffer)
          self._server_buffer = self._server_buffer[bytes:]
         
          # stop watching for writeable socket now buffer is empty
          if len(self._server_buffer) == 0:
            write_set.remove(self._server_sock)
           
        # check if we've been interrupted
        if self._interrupt[0] in readable:
          # consume interrupt byte
          os.read(self._interrupt[0], 1)
          break
 
    except socket.error:
      pass
   
    # cleanup
    if self._server_sock:
      self._server_sock.close()
    self._client_sock.close()
   
    os.close(self._interrupt[0])
    os.close(self._interrupt[1])
 
    # interrupt server so it can cleanup finished connection
    self._server.interrupt()
 
class ProxyListener:
  def __init__(self, listen_host, listen_port, dest_host, dest_port):
    self._listen_host = listen_host
    self._listen_port = listen_port
    self._dest_host = dest_host
    self._dest_port = dest_port
    self._listen_sock = None
   
  def listen(self):
    self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._listen_sock.bind((self._listen_host, self._listen_port))
    self._listen_sock.listen(socket.SOMAXCONN)
   
  def accept(self, server):
    client_sock, _ = self._listen_sock.accept()
    return ProxyConnection(client_sock, self._dest_host, self._dest_port, server)
   
  def close(self):
    self._listen_sock.close()
 
  def get_listen_socket(self):
    return self._listen_sock
   
class ProxyServer(Thread):
  def __init__(self):
    Thread.__init__(self)
    self._interrupt = None
    self._listeners_by_key = {}
    self._listeners_by_socket = {}
    self._listener_lock = Lock()
    self._connections = []
    self._stop = Event()
   
  def start_proxy(self, listen_host, listen_port, dest_host, dest_port):    
    listener = ProxyListener(listen_host, listen_port, dest_host, dest_port)
    listener.listen()
   
    key = "%s:%i" % (listen_port, listen_port)
    with self._listener_lock:
      self._listeners_by_key[key] = listener
      self._listeners_by_socket[listener.get_listen_socket()] = listener
   
    # tell server thread we have a new listener
    self.interrupt()
   
  def stop_proxy(self, listen_host, listen_port):
    key = "%s:%i" % (listen_port, listen_port)
    with self._listener_lock:
      try:
        listener = self._listeners_by_key[key]
      except KeyError:
        return
      else:
        listener.close()
        del self._listeners_by_key[key]
        del self._listeners_by_socket[listener.get_listen_socket()]
   
    # tell server thread we've removed a listener
    self.interrupt()
       
  def interrupt(self):
    os.write(self._interrupt[1], ' ')
   
  def run(self):
   
    # refresh socket list
    with self._listener_lock:
      sockets = self._listeners_by_socket.keys() + [self._interrupt[0]]
     
    while True:
      # wait for new connection
      try:
        ready, _, _ = select.select(sockets, [], [])
      except:
        # prevent fast looping on error
        time.sleep(0.1)
        continue
     
      if self._interrupt[0] in ready:
        # consume interrupt byte
        os.read(self._interrupt[0], 1)
        # check if stopped
        if self._stop.is_set():
          break
        # refresh socket list
        sockets = self._listeners_by_socket.keys() + [self._interrupt[0]]
        # remove interrupt sock from read so its not iterated over below
        ready.remove(self._interrupt[0])
        # remove finished connections
        self._connections = [x for x in self._connections if not x.try_join()]
       
      for sock in ready:
        try:
          # accept and launch new connection
          connection = self._listeners_by_socket[sock].accept(self)
          connection.start()
          self._connections.append(connection)
        except socket.error:
          pass
   
    # close listeners
    with self._listener_lock:
      for listener in self._listeners_by_key.values():
        listener.close()
 
    # stop active connections
    for connection in self._connections:
      connection.interrupt()
     
    for connection in self._connections:
      connection.join()
   
    # cleanup
    os.close(self._interrupt[0])
    os.close(self._interrupt[1])
         
  def start(self):
    self._interrupt = os.pipe()
    Thread.start(self)
 
  def stop(self):
    self._stop.set()
    self.interrupt()
    self.join()
   
if __name__ == "__main__":
 
  server = ProxyServer()
  server.start()
  server.start_proxy("localhost", 5432, "localhost", 1337)
  time.sleep(30)
  server.stop_proxy("localhost", 5432)
  time.sleep(10)
  server.stop()
