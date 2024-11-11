# app/controllers/api/v1/users_controller.rb

module Api
  module V1
    class UsersController < ApplicationController
      # before_action :authenticate_user!
      before_action :set_user, only: [:show, :update, :destroy]
      # before_action :ensure_current_user, only: [:update, :destroy]

      # GET /api/v1/users/:email
      def show
        render json: @user
      end

      # PATCH/PUT /api/v1/users/:email
      def update
        if @user.update(user_params)
          render json: @user
        else
          render json: @user.errors, status: :unprocessable_entity
        end
      end

      # DELETE /api/v1/users/:email
      def destroy
        if @user.destroy
          render json: { message: 'Usuario eliminado exitosamente' }, status: :ok
        else
          render json: { error: 'No se pudo eliminar el usuario' }, status: :unprocessable_entity
        end
      end

      private

      def set_user
        @user = User.find_by(email: params[:email])
      rescue ActiveRecord::RecordNotFound
        render json: { error: 'Usuario no encontrado' }, status: :not_found
      end

      def user_params
        params.require(:user).permit(:name, :email)
      end

      def ensure_current_user
        return if @user == current_user

        render json: { error: 'No autorizado para realizar esta acción' }, status: :unauthorized
      end
    end
  end
end
