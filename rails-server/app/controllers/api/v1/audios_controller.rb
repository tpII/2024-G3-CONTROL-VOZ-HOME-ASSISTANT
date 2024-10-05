module Api
  module V1
    class AudiosController < ApplicationController
      before_action :authenticate_user!
      before_action :set_audio, only: %i[show destroy transcribe]

      def index
        @audios = current_user.audios
        render json: @audios
      end

      def show
        render json: @audio
      end

      def create
        @audio = current_user.audios.new(audio_params)
        if @audio.save
          render json: @audio, status: :created
        else
          render json: @audio.errors, status: :unprocessable_entity
        end
      end

      def destroy
        @audio.destroy
        head :no_content
      end

      def transcribe
        result = WhisperService.transcribe(@audio.file)
        if result[:error]
          render json: { error: result[:error] }, status: :unprocessable_entity
        else
          @audio.update(transcription: result[:transcription])
          render json: { transcription: @audio.transcription }, status: :ok
        end
      end

      private

      def set_audio
        @audio = current_user.audios.find(params[:id])
      end

      def audio_params
        params.require(:audio).permit(:file_base64)
      end
    end
  end
end
