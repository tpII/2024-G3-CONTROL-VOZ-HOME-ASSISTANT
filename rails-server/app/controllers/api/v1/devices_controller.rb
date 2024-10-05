module Api
  module V1
    class DevicesController < ApplicationController
      before_action :authenticate_user!
      before_action :set_device, only: %i[show update destroy]

      def index
        @devices = current_user.devices
        render json: @devices
      end

      def show
        render json: @device
      end

      def create
        @device = current_user.devices.new(device_params)
        if @device.save
          render json: @device, status: :created
        else
          render json: @device.errors, status: :unprocessable_entity
        end
      end

      def update
        if @device.update(device_params)
          render json: @device
        else
          render json: @device.errors, status: :unprocessable_entity
        end
      end

      def destroy
        @device.destroy
        head :no_content
      end

      private

      def set_device
        @device = current_user.devices.find(params[:id])
      end

      def device_params
        params.require(:device).permit(:name, :esp8266_id)
      end
    end
  end
end
