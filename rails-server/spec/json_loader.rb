class JsonLoader
  def self.call(file_name, to_hash: false)
    json_file = file_read(file_name)
    if to_hash
      JSON.parse(json_file)
    else
      json_file
    end
  end

  class << self
    private

    def file_path(file_name)
      Rails.root.join 'spec', 'data', file_name
    end

    def file_read(file_name)
      File.new(file_path(file_name)).read
    end
  end
end
