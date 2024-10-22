DeviseTokenAuth.setup do |config|
  # Removes the need for email confirmation
  config.require_client_password_reset_token = false

  # Enables the use of a single sign-on
  config.default_confirm_success_url = '/'

  # Increases token lifespan
  config.token_lifespan = 30.minutes

  # Changes to a request will not generate a new token
  config.change_headers_on_each_request = false

  # Other configurations...
end
