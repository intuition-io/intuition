#!/usr/bin/ruby

#http://www.ruby-lang.org/fr/documentation/quickstart/2/
#https://github.com/nu7hatch/gmail
require 'logging'
require 'gmail'

  # here we setup a color scheme called 'bright'
  Logging.color_scheme( 'bright',
    :levels => {
      :info  => :blue,
      :warn  => :yellow,
      :error => :red,
      :fatal => :red
    },
    :date => :blue,
    :logger => :cyan,
    :message => :magenta
  )

  Logging.appenders.stdout(
    'stdout',
    :layout => Logging.layouts.pattern(
      :pattern => '[%d] %-5l %c: %m\n',
      :color_scheme => 'bright'
    )
  )

  log = Logging.logger['QuanTrade::GMail']
  log.add_appenders 'stdout'
  log.level = :debug


Gmail.connect!('xavier.bruhiere@gmail.com', '') do |gmail|
    log.info 'Connected to GMail'
    log.info gmail.inbox.count(:from => "no-reply@quantopian.com")
    log.info gmail.inbox.count
    log.info gmail.inbox.count(:unread)
    log.info gmail.inbox.count(:read)

    log.info gmail.mailbox('Trade').count(:unread)
    log.info gmail.mailbox('Dev').count(:unread)

    gmail.inbox.find(:from => 'no-reply@recordedfuture.com').each do |email|
        puts email.read!
    end

    log.info gmail.labels.all

    #gmail.deliver do
      #to "xavier.bruhiere@gmail.com"
      #subject 'A little test'
      #html_part do
        #content_type 'text/html; charset=UTF-8'
        #body 'Lets try somethin budy'
      #end
    #end
end
