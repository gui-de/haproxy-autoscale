global
    user haproxy
    group haproxy
    daemon
    stats socket /tmp/haproxy.sock

    log 127.0.0.1 local0
    log 127.0.0.1 local1 notice

    defaults
        mode http
        timeout connect 5000ms
        timeout client 50000ms
        timeout server 50000ms

    frontend http-in
        bind *:80
        default_backend api-servers

    backend api-servers
    mode http
    balance roundrobin
    timeout connect 5s
    timeout server 86400

    server dev-api-01 10.0.0.19:80 maxconn 512 check
    % for instance in instances['sg-27ec1148']:
    server ${ instance.id } ${ instance.private_dns_name }:80 maxconn 512 check
    % endfor

listen stats :1984
    mode http
    stats enable
    stats realm stats
        # Get PID if haproxy is already running.
    stats uri /
    stats auth admin:p00k3rR00m
