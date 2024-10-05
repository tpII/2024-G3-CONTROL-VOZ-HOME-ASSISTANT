Rails.application.routes.draw do
  # Rutas para Devise Token Auth
  mount_devise_token_auth_for 'User', at: 'auth', controllers: {
    registrations: 'api/v1/registrations',
    sessions: 'api/v1/sessions'
  }

  # API versioning
  namespace :api do
    namespace :v1 do
      # Rutas para audios
      resources :audios, only: %i[create index show destroy] do
        member do
          post :transcribe
        end
      end

      # Rutas para dispositivos ESP8266
      resources :devices, only: %i[create index show update destroy]

      # Rutas para el dashboard
      get 'dashboard', to: 'dashboard#index'
      # Otras rutas que puedas necesitar
      resources :transcriptions, only: %i[index show]
    end
  end

  # Ruta de salud para verificar el estado de la API
  get '/health', to: 'application#health'
end
