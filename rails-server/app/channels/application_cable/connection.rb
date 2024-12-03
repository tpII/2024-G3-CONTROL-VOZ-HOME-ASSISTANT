module ApplicationCable
  class Connection < ActionCable::Connection::Base
    identified_by :current_user

    def connect
      params = request.query_parameters

      token = params['access-token']
      uid = params['uid']
      client = params['client']

      self.current_user = find_verified_user token, uid, client
      logger.add_tags 'ActionCable', current_user.email
    end

    protected

    # this checks whether a user is authenticated with devise
    def find_verified_user(token, uid, client_id)
      user = User.find_by email: uid
      return user

      reject_unauthorized_connection
    end
  end
end
