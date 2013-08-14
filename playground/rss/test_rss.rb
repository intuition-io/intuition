require 'rss'
require 'open-uri'

url = 'http://www.ruby-lang.org/en/feeds/news.rss'
open(url) do |rss|
  feed = RSS::Parser.parse(rss)
  puts "Title: #{feed.channel.title}"
  feed.items.each do |item|
    puts "Item: #{item.title}"
  end
end
