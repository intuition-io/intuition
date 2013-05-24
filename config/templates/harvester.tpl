exports.config = {
  nodeName: "{{ nodename }}",
  logStreams: {
    quantrade: [
      {% block logs %}{% endblock %}
    ]
  },
  server: {
    host: "{{ server_ip }}",
    port: 28777
  }
}
