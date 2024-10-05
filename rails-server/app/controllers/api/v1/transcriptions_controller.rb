module Api
  module V1
    class TranscriptionsController < ApplicationController
      before_action :authenticate_user!

      def index
        @transcriptions = current_user.audios.where.not(transcription: nil).order(updated_at: :desc)
        render json: @transcriptions
      end

      def show
        @audio = current_user.audios.find(params[:id])
        if @audio.transcription
          render json: { id: @audio.id, transcription: @audio.transcription }
        else
          render json: { error: 'Transcription not found' }, status: :not_found
        end
      end
    end
  end
end
