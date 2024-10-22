# app/controllers/api/v1/sessions_controller.rb

module Api
  module V1
    class SessionsController < DeviseTokenAuth::SessionsController
      respond_to :json
      def create
        byebug
        super do |resource|
          # Personaliza la respuesta después de un login exitoso
          token = resource.create_token
          expiry_date = Time.at(token.expiry).in_time_zone('Buenos Aires').strftime('%Y-%m-%d %H:%M:%S')
          @response_data = {
            status: 'success',
            data:   {
              access_token: token.token,
              token:        expiry_date
            }
          }
        end
      end

      def destroy
        # Elimina todos los tokens del usuario actual
        @resource.tokens = {}
        @resource.save

        render json: {
          status:  'success',
          message: 'Logged out successfully'
        }
      end
    end
  end
end
