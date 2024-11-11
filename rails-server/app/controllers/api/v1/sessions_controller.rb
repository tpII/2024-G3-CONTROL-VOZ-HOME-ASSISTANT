# app/controllers/api/v1/sessions_controller.rb

module Api
  module V1
    class SessionsController < DeviseTokenAuth::SessionsController
      respond_to :json
      def create
        super do |resource|
          # Personaliza la respuesta después de un login exitoso
          token = resource.create_token
          expiry_date = token.expiry
          nice_date = Time.at(expiry_date).in_time_zone('Buenos Aires').strftime('%Y-%m-%d %H:%M:%S')
          @response_data = {
            uid:          resource.email,
            expires_at:   nice_date,
            access_token: token
          }
        end
      end

      protected

      def render_create_success
        render json: {
          status: 'success',
          data:   @response_data
        }
      end
    end
  end
end
