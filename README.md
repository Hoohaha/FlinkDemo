## How to build

- Create file `.env` and configure Proxy like below, this is optional step:

```
http_proxy="http://xxxxx:8080"
https_proxy="http://xxxxx:8080"
```

- Build Images:

docker-compose --env-file .env build

## Start services

start containers:
```
docker-compose up -d
```

enter flink job manager
```
docker exec -it flink-demo_jobmanager_1 bash
```

submit flink job:

```
cd job
./run_job.sh
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

