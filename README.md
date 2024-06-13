[ChatGPTiddy Thread](https://chatgpt.com/share/e0ab1cc3-5eef-4743-9620-f51fccf4e6d0)

### Prometheus Auth
User: prom_admin  
PW: password

To generate prometheus password
```bash
## Install if do not have
sudo apt-get install apache2-utils

## Generate creds (Will prompt for pw)
htpasswd -c nginx/conf.d/.htpasswd prom_admin
```

### Metrics Endpoint
User: admin  
PW: password

### Grafana Dashboard
User: admin  
PW: admin