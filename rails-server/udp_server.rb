require 'logger'
require 'socket'
require 'json'
require 'net/http'
require 'uri'
require 'websocket-client-simple'

udp_logger = Logger.new('log/udp_server.log')
udp_logger.level = Logger::DEBUG

# Configuraciones del servidor
API_URL = 'http://localhost:8080'.freeze
REGISTER_ENDPOINT = '/auth'.freeze
LOGIN_ENDPOINT = '/auth/sign_in'.freeze
WEBSOCKET_ENDPOINT = '/cable'.freeze
UDP_UID = 'udp@server.com'.freeze
UDP_PASSWORD = 123_456_789
# Mapea las acciones recibidas a los mensajes UDP para la Wemos D1
ACTION_TO_UDP = {
  turn_on:  { word: 'C_connect' },
  turn_off: { word: 'C_disconnect' }
}.freeze
# Configuración del servidor UDP para Wemos
WEMOS_IP = '192.168.1.70'.freeze # IP de la Wemos D1
WEMOS_PORT = 8080 # Puerto UDP de la Wemos D1

# Registra al usuario
def register_user
  uri = URI.parse("#{API_URL}#{REGISTER_ENDPOINT}")
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Post.new(uri.path, { 'Content-Type' => 'application/json' })
  request.body = { user: { email: UDP_UID, password: UDP_PASSWORD, password_confirmation: UDP_PASSWORD } }.to_json

  response = http.request(request)
  JSON.parse(response.body)
end

# Realiza login y obtiene los tokens
def login_user
  uri = URI.parse("#{API_URL}#{LOGIN_ENDPOINT}")
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Post.new(uri.path, { 'Content-Type' => 'application/json' })
  request.body = { email: UDP_UID, password: UDP_PASSWORD }.to_json

  response = http.request(request)
  headers = response.to_hash

  # Obtiene uid, client y access-token del header de la respuesta
  {
    uid:          headers['uid'].first,
    client:       headers['client'].first,
    access_token: headers['access-token'].first
  }
end

# Conecta al WebSocket con autenticación
def connect_websocket(auth_tokens)
  websocket_url = 'ws://localhost:8080/cable'
  access_token = auth_tokens[:access_token]
  client = auth_tokens[:client]
  uid = auth_tokens[:uid]
  websocket_params = "access-token=#{access_token}&client=#{client}&uid=#{uid}"
  ws = WebSocket::Client::Simple.connect "#{websocket_url}?#{websocket_params}"

  ws.on :message do |msg|
    udp_logger.info "Mensaje recibido en WebSocket: #{msg.data}"
    begin
      data = JSON.parse(msg.data)
      action = data['action']

      if ACTION_TO_UDP.key?(action)
        udp_message = ACTION_TO_UDP[action].to_json
        send_udp_message_to_wemos(udp_message)
        udp_logger.info "Mensaje UDP enviado a Wemos: #{udp_message}"
      else
        udp_logger.info "Acción no reconocida en WebSocket: #{action}"
      end
    rescue JSON::ParserError
      udp_logger.info "Mensaje de WebSocket no válido: #{msg.data}"
    end
  end

  ws.on :open do
    udp_logger.info 'Conexión WebSocket abierta'
  end

  ws.on :close do
    udp_logger.info 'Conexión WebSocket cerrada'
  end

  ws.on :error do |e|
    udp_logger.info "Error en WebSocket: #{e.message}"
  end

  ws
end

# Función para enviar mensaje UDP a la Wemos
def send_udp_message_to_wemos(message)
  udp_socket = UDPSocket.new
  udp_socket.send(message, 0, WEMOS_IP, WEMOS_PORT)
  udp_socket.close
end

# Inicia el registro y login para obtener el token
udp_logger.info 'Registrando y autenticando al usuario...'
register_user # Registra el usuario
auth_tokens = login_user # Realiza login y obtiene las claves

# Conexión al WebSocket
ws = connect_websocket(auth_tokens)

# Configura el socket UDP para escuchar en el puerto 12345
udp_socket = UDPSocket.new
udp_socket.bind('0.0.0.0', 12_345)

# Límite de bytes para recibir
MAX_BYTES = 65_507

udp_logger.info 'UDP Server listening on port 12345...'

# Loop infinito para recibir mensajes UDP y enviarlos por WebSocket
loop do
  # Recibir mensaje UDP
  message, sender = udp_socket.recvfrom(MAX_BYTES)
  sender_ip = sender[3]
  sender_port = sender[1]

  udp_logger.info "Mensaje recibido: '#{message.strip}' de #{sender_ip}:#{sender_port}"

  # Formatear el mensaje como JSON para enviar a través de WebSocket
  payload = {
    message: message.strip,
    ip:      sender_ip,
    port:    sender_port
  }.to_json

  # Enviar el mensaje al WebSocket
  ws.send(payload)
end
