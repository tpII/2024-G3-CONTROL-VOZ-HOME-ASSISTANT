module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      self.current_user = find_verified_user
    end

    private

    def find_verified_user
      # Obtenemos el token y el client del header
      token = request.params[:'access-token'] || request.headers['access-token']
      client_id = request.params[:client] || request.headers['client']
      uid = request.params[:uid] || request.headers['uid']

      # Usamos Devise Token Auth para validar el token
      user = User.find_by(uid: uid)

      return user if user&.valid_token?(token, client_id)

      reject_unauthorized_connection
    end
  end
end
