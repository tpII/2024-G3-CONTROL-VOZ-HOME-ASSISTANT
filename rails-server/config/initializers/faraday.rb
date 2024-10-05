require 'faraday'

URL = ENV.fetch('WHISPER_URL', 'http://localhost:8080')

WHISPER_CONNECTION = Faraday.new(url: URL) do |faraday|
  faraday.request  :url_encoded
  faraday.response :logger
  faraday.adapter  Faraday.default_adapter
end
