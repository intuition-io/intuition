
desc "Populate with sample data set"
task :cleanup => :environment do
    Dashboard.destroy_all
end

desc "Populate with standard finance dashboard"
task :custom_populate => :environment do
    target1 = "demo.example1"
    target2 = "demo.example2"

    d1 = Dashboard.create!(:name => "Auto generation")

    # Create graph widgets
    d1.widgets.create!(:name => "Portfolio Value", :targets => target1, :size_x => 2, :size_y => 2, 
                       :source => 'http_proxy', 
                       :settings => { :graph_type => 'area', :proxy_url => ""})
    d1.widgets.create!(:name => "Max Drawdown", :targets => target2, :size_x => 1, :size_y => 2, 
                       :source => 'http_proxy', 
                       :settings => { :graph_type => 'line', :proxy_url => "" })

    # Create Number widgets
    d1.widgets.create!(:name => "Portfolio return", :kind => 'number', :size_x => 2, :source => 'http_proxy', 
                       :settings => { :label => "Euros", :proxy_url => "", 
                                      :proxy_value_path => " " })
    d1.widgets.create!(:name => "PNL", :kind => 'number', :source => 'http_proxy', 
                       :settings => { :label => "Whatever", :proxu_url => "",
                                      :proxy_value_path => " "})
    d1.widgets.create!(:name => "Sortino Ratio", :kind => 'number', :source => 'http_proxy', 
                       :settings => { :label => "Whatever", :proxu_url => "",
                                      :proxy_value_path => " "})
    d1.widgets.create!(:name => "Volatility", :kind => 'number', :size_x => 1, :source => 'http_proxy', 
                       :settings => { :label => "Whatever", :proxy_url => "", 
                                      :proxy_value_path => " " })
    d1.widgets.create!(:name => "Number", :kind => 'number', :source => 'http_proxy', 
                       :settings => { :label => "Whatever", :proxy_url => "", 
                                      :proxy_value_path => " " })
    d1.widgets.create!(:name => "Number", :kind => 'number', :source => 'http_proxy', 
                       :settings => { :label => "Whatever", :proxy_url => "", 
                                      :proxy_value_path => " " })

    # Create Boolean widgets
    d1.widgets.create!(:name => "Boolean", :kind => 'boolean', :source => 'http_proxy', 
                       :settings => { :label => "Whatever", :proxy_url => "", 
                                      :proxy_value_path => " " })
    d1.widgets.create!(:name => "Boolean", :kind => 'boolean', :source => 'http_proxy', 
                       :settings => { :label => "Whatever", :proxy_url => "", 
                                      :proxy_value_path => " " })
end
