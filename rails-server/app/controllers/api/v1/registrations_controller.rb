# app/controllers/api/v1/registrations_controller.rb

module Api
  module V1
    class RegistrationsController < DeviseTokenAuth::RegistrationsController
      # Sobreescribe el método create para personalizar la respuesta
      def create
        build_resource

        if @resource.save
          # Si el usuario se guarda correctamente, inicia sesión automáticamente
          # sign_in(@resource, store: false, bypass: false)

          # Crea un token de acceso para el usuario
          token = @resource.create_token
          @resource.save
          nice_date = Time.at(token.expiry).in_time_zone('Buenos Aires').strftime('%Y-%m-%d %H:%M:%S')

          render json: {
            status: 'success',
            data:   {
              status:       :ok,
              access_token: token,
              uid:          @resource.uid,
              expiry:       nice_date
            }
          }, status: :created
        else
          # Si hay errores, devuelve los mensajes de error
          render json: {
            status: 'error',
            errors: @resource.errors.full_messages
          }, status: :unprocessable_entity
        end
      end

      private

      # Sobreescribe el método sign_up_params para permitir el parámetro 'name'
      def sign_up_params
        params.require(:user).permit(:email, :password, :name)
      end

      protected

      # Sobreescribe el método para que no se envíe un correo de confirmación
      def render_create_success
        # No hace nada, evitando el envío de correo
      end
    end
  end
end
