require 'socket'
class ChatChannel < ApplicationCable::Channel
  UDP_SERVER_HOST = ENV.fetch('UDP_SERVER_HOST', '127.0.0.1')
  UDP_SERVER_PORT = ENV.fetch('UDP_SERVER_PORT', '12345').to_i
  WEMOS_ACTIONS = {
    ON:  '0x0501',
    OFF: '0x0500'
  }.freeze

  def subscribed
    stream_for 'chat_channel'

    current_state = Rails.cache.fetch('led_state', default: 'OFF')
    transmit(current_state)
  end

  def receive(data)
    message = data['message']
    command = WEMOS_ACTIONS[message.to_sym] # Traduce ON/OFF al comando respectivo

    if command
      Rails.cache.write('led_state', message)
      Rails.logger.info "Enviando #{command} a la Wemos"
      send_udp_command(command) # Envía el comando directamente al servidor UDP
      transmit(message) # Notifica a todos los clientes
    else
      Rails.logger.error "Comando inválido: #{message}"
    end
  end

  def update_led_state(data)
    Rails.cache.write('led_state', data['state'])
    transmit(data['state'])
  end

  def led_state
    current_state = Rails.cache.fetch('led_state')
    transmit(current_state)
  end

  private

  def send_udp_command(command)
    UDPSocket.open do |socket|
      socket.send(command, 0, UDP_SERVER_HOST, UDP_SERVER_PORT)
    end
  rescue StandardError => e
    Rails.logger.error "Error enviando comando UDP: #{e.message}"
  end

end
