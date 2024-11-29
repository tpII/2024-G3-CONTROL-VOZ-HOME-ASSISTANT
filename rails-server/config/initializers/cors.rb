Rails.application.config.middleware.insert_before 0, Rack::Cors do
  allow do
    origins 'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://0.0.0.0:3000',
            'http://localhost:12345',
            'http://127.0.0.1:12345',
            'http://0.0.0.0:12345'

    resource '*',
             headers:     :any,
             methods:     [:get, :post, :put, :patch, :delete, :options, :head],
             credentials: true,
             max_age:     86_400
  end
end
