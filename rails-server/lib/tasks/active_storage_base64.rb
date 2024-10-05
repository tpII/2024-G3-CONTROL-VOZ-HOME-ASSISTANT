module ActiveStorageBase64
  extend ActiveSupport::Concern

  class_methods do
    def has_base64_attached(name)
      attribute "#{name}_base64", :string

      before_save do
        if send("#{name}_base64").present?
          data = StringIO.new(Base64.decode64(send("#{name}_base64")))
          send(name).attach(io: data, filename: "#{name}.wav")
        end
      end
    end
  end
end

ActiveRecord::Base.send :include, ActiveStorageBase64
