class Audio < ApplicationRecord
  belongs_to :user
  base64_attached? :file
end
