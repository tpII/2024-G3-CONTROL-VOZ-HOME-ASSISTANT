class User < ApplicationRecord
  # Include default devise modules. Others available are:
  # :confirmable, :lockable, :timeoutable, :trackable and :omniauthable
  devise :database_authenticatable, :registerable,
         :trackable, :validatable

  extend Devise::Models
  include DeviseTokenAuth::Concerns::User

  validates :name, presence: true
  validates :email, presence: true, uniqueness: true

  # Associations
  has_many :audios, dependent: :destroy
  has_many :devices, dependent: :destroy

  # Override to skip email confirmation
  def confirmation_required?
    false
  end
end
