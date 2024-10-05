# app/controllers/api/v1/sessions_controller.rb

module Api
  module V1
    class SessionsController < DeviseTokenAuth::SessionsController
      def create
        super do |resource|
          # Personaliza la respuesta después de un login exitoso
          @response_data = {
            status: 'success',
            data: {
              id: resource.id,
              email: resource.email,
              name: resource.name
            }
          }
        end
      end

      def destroy
        # Elimina todos los tokens del usuario actual
        @resource.tokens = {}
        @resource.save

        render json: {
          status: 'success',
          message: 'Logged out successfully'
        }
      end
    end
  end
end
