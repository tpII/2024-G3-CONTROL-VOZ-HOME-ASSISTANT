module Api
  module V1
    class DashboardController < ApplicationController
      before_action :authenticate_user!

      def index
        @devices = current_user.devices
        @recent_audios = current_user.audios.order(created_at: :desc).limit(5)
        @recent_transcriptions = current_user.audios.where.not(transcription: nil).order(updated_at: :desc).limit(5)

        render json: {
          devices_count: @devices.count,
          recent_audios: @recent_audios,
          recent_transcriptions: @recent_transcriptions
        }
      end
    end
  end
end
