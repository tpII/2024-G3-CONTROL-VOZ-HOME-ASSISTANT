# app/controllers/api/v1/sessions_controller.rb

module Api
  module V1
    class SessionsController < DeviseTokenAuth::SessionsController
      respond_to :json
      def create
        super do |resource|
          # Personaliza la respuesta después de un login exitoso
          resource.create_token
docl          resource.save
        end
      end

      private

      # Sobrescribe el método para capturar headers antes de enviar la respuesta
      def update_auth_header
        super
        # Almacena headers de autenticación en variables de instancia
        @token = response.headers['access-token']
        @uid = response.headers['uid']
        @client = response.headers['client']
      end

      def render_create_success
        render json: {
          status: :success,
          data:   {
            uid:          @uid,
            access_token: {
              client: @client,
              token:  @token
            }
          }
        }
      end
    end
  end
end
