class Audio < ApplicationRecord
  has_base64_attached :file
end
