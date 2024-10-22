class ApplicationController < ActionController::API
  include DeviseTokenAuth::Concerns::SetUserByToken
  include Pundit::Authorization

  def health
    render json: { status: 'OK' }, status: :ok
  end
end
