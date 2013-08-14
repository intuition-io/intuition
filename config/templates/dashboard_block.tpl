{% extends "panel.tpl" %}

{% block build %}
    {% for dashboard in panel %}
        d{{ dashboard.i }} = Dashboard.create!(:name => "{{ dashboard['title'] }}")

        # Create graph widgets
        d{{ dashboard.i }}.widgets.create!(:name => "Portfolio Value", :targets => target1, :size_x => 2, :size_y => 2, 
                           :source => 'http_proxy', 
                           :settings => { :graph_type => 'area',
                               :proxy_url => "http://{{ dashboard.proxy_ip }}:8080/dashboard/graph?data=PortfolioValue&table=Portfolios&field=Name&value={{ dashboard['portfolio'] }}"})
        d{{ dashboard.i }}.widgets.create!(:name => "Max Drawdown", :targets => target2, :size_x => 1, :size_y => 2, 
                           :source => 'http_proxy', 
                           :settings => { :graph_type => 'line', 
                               :proxy_url => "http://{{ dashboard.proxy_ip }}:8080/dashboard/graph?data=MaxDrawdown&table=Metrics&field=Name&value={{ dashboard.portfolio }}" })

        # Create Number widgets
        d{{ dashboard.i }}.widgets.create!(:name => "Portfolio return", :kind => 'number', :size_x => 2, :source => 'http_proxy', 
                           :settings => { :label => "Euros", :proxy_url => "http://{{ dashboard.proxy_ip }}:8080/dashboard/number?data=Returns&table=Portfolios&field=Name&value={{ dashboard.portfolio }}", 
                                          :proxy_value_path => " " })
        d{{ dashboard.i }}.widgets.create!(:name => "PNL", :kind => 'number', :source => 'http_proxy', 
                           :settings => { :label => "Whatever", :proxy_url => "http://{{ dashboard.proxy_ip }}:8080/dashboard/number?data=PNL&table=Portfolios&field=Name&value={{ dashboard.portfolio }}",
                                          :proxy_value_path => " "})
        d{{ dashboard.i }}.widgets.create!(:name => "Sortino Ratio", :kind => 'number', :source => 'http_proxy', 
                           :settings => { :label => "Whatever", :proxy_url => "http://{{ dashboard.proxy_ip }}:8080/dashboard/number?data=SortinoRatio&table=Metrics&field=Name&value={{ dashboard.portfolio }}",
                                          :proxy_value_path => " "})
        d{{ dashboard.i }}.widgets.create!(:name => "Volatility", :kind => 'number', :size_x => 1, :source => 'http_proxy', 
                           :settings => { :label => "Whatever", :proxy_url => "http://{{ dashboard.proxy_ip }}:8080/dashboard/number?data=Volatility&table=Metrics&field=Name&value={{ dashboard.portfolio }}", 
                                          :proxy_value_path => " " })
        d{{ dashboard.i }}.widgets.create!(:name => "Value", :kind => 'number', :size_x => 2, :source => 'http_proxy', 
                           :settings => { :label => "Whatever", :proxy_url => "http://{{ dashboard.proxy_ip }}:8080/dashboard/number?data=PortfolioValue&table=Portfolios&field=Name&value={{ dashboard.portfolio }}", 
                                          :proxy_value_path => " " })
        d{{ dashboard.i }}.widgets.create!(:name => "Benchmark return", :kind => 'number', :source => 'http_proxy', 
                           :settings => { :label => "Whatever", :proxy_url => "http://{{ dashboard.proxy_ip }}:8080/dashboard/number?data=BenchmarkReturns&table=Metrics&field=Name&value={{ dashboard.portfolio }}", 
                                          :proxy_value_path => " " })

        # Create Boolean widgets
        d{{ dashboard.i }}.widgets.create!(:name => "App Health", :kind => 'boolean', :source => 'shell', 
                           :settings => { :label => "Whatever", :command => "ps -a | grep deploy" })
        d{{ dashboard.i }}.widgets.create!(:name => "Portfolio Health", :kind => 'boolean', :source => 'http_proxy', 
                           :settings => { :label => "Whatever", :proxy_url => "http://{{ dashboard.proxy_ip }}:8080/dashboard/boolean?data=Returns&table=Portfolios&field=Name&value={{ dashboard.portfolio }}", 
                                          :proxy_value_path => " " })
    {% endfor %}
{% endblock %}
