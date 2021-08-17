## How to build

- Create file `.env` and configure Proxy like below, this is optional step:

```
http_proxy="http://xxxxx:8080"
https_proxy="http://xxxxx:8080"
```

- Build Images:

docker-compose --env-file .env build

## Prepare logs

Unzip logs to `log-data/`:

Examples:
```
log-data/
  |_____ 197812/
  |_____ 55682/
```

## Start services

start containers:
```
docker-compose up -d
```

submit flink job:

```
docker exec -it flinkdemo_jobmanager_1 bash -c "cd job;./run_job.sh"
```


## Shutdown services
docker-compose down -v


## Restart services
docker-compose restart


## Web dashboard

- Flink Dashboard

http://localhost:8081

- Grafana Dashboard

http://localhost:3000

