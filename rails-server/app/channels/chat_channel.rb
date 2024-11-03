class ChatChannel < ApplicationCable::Channel
  def subscribed
    stream_for current_user
  end

  def unsubscribed; end

  def speak(data)
    return if Rails.env.test?

    ActionCable.server.broadcast(current_user, message: data['message'])
  end
end
