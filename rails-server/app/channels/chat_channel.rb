require 'socket'
class ChatChannel < ApplicationCable::Channel
  # Mapea las acciones recibidas a los mensajes UDP para la Wemos D1
  ACTION_TO_UDP = {
    'turn_on'  => { word: 'C_connect' },
    'turn_off' => { word: 'C_disconnect' }
  }.freeze
  # Configuración del servidor UDP para Wemos
  WEMOS_IP = '192.168.1.70'.freeze # IP de la Wemos D1
  WEMOS_PORT = 8080 # Puerto UDP de la Wemos D1

  def subscribed
    stream_for "chat_#{params[:room]}"
  end

  def perform_action(data)
    # Manejamos el mensaje recibido desde el frontend
    message = data['message']
    transmit(message)
    logger.add_tags 'ChatChannel', "\n #{data} RECIBIDO DESDE LA APP \n"
    action = ACTION_TO_UDP[data['action']]
    send_udp_command(action)
  end

  private

  # Método para enviar datos a la WEMOS D1 a través de UDP
  def send_udp_command(word)
    udp_socket = UDPSocket.new

    logger.add_tags 'ChatChannel', "\n Enviando #{word} mensaje a la WEMOS \n"
    udp_socket.send(word.to_json, 0, WEMOS_IP, WEMOS_PORT)
    udp_socket.close
  end
end
