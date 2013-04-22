#https://github.com/peter-murach/github
#https://github.com/mojombo/grit
#https://github.com/schacon/ruby-git

github = Github.new do |opts|
  opts.user = 'peter-murach'
  opts.repo = 'github-api'
end

github = Github.new :basic_auth => 'login:password'
