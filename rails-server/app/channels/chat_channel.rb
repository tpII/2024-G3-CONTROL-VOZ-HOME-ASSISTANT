require 'socket'
class ChatChannel < ApplicationCable::Channel
  UDP_SERVER_HOST = ENV["UDP_SERVER_HOST"]
  UDP_SERVER_PORT = ENV["UDP_SERVER_PORT"].to_i

  def subscribed
    stream_for 'chat_channel'

    current_state = Rails.cache.fetch("led_state", default: "OFF")
    transmit({ message: current_state })
  end

  def receive(data)
    begin
      Rails.cache.write("led_state", data["message"])
      send_udp_command(data["message"])
      ActionCable.server.broadcast("chat_channel", { message: data["message"] })
    end
  end

  private

  def send_udp_command(command)
    UDPSocket.open do |socket|
      udp_host = UDP_SERVER_HOST || "127.0.0.1"
      udp_port = UDP_SERVER_PORT || "12345"
      socket.send(command, 0, udp_host, udp_port.to_i)
    end
  rescue StandardError => e
    Rails.logger.error "Error enviando comando UDP: #{e.message}"
  end
end
