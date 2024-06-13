[ChatGPTiddy Thread](https://chatgpt.com/share/e0ab1cc3-5eef-4743-9620-f51fccf4e6d0)

### Prometheus Auth
```
Host: http://localhost:5000  
User: prom_admin  
PW: password
```

To generate prometheus password
```bash
## Install if do not have
sudo apt-get install apache2-utils

## Generate creds (Will prompt for pw)
htpasswd -c nginx/conf.d/.htpasswd prom_admin
```

### Metrics Endpoint
Where metrics are scraped from via scheduled celery workers and inserted into promtheus.
```
Host: http://localhost:8000/metrics
User: admin  
PW: password
```

### Grafana Dashboard
Display custom dashboards from promtheus data sources.
```
Host: http://localhost:3000  
User: admin  
PW: admin
```

### Flower Dashboard (Workers)
Shows run results of worker jobs.
```
Host: http://localhost:5555
```