class WhisperService
  def self.transcribe(audio_file)
    response = WHISPER_CONNECTION.post do |req|
      req.url '/transcribe'
      req.headers['Content-Type'] = 'multipart/form-data'
      req.body = { audio: Faraday::UploadIO.new(audio_file.tempfile, audio_file.content_type) }
    end

    JSON.parse(response.body)
  rescue Faraday::Error => e
    Rails.logger.error "Error en la transcripción: #{e.message}"
    { error: 'Error en la transcripción' }
  end
end
