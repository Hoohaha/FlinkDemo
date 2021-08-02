



## How to build

- Configure Proxy in `.env` file, optional

```
http_proxy="http://xxxxx:8080"
https_proxy="http://xxxxx:8080"
```

- Build:

docker-compose --env-file .env build

## Start services

docker-compose up -d


## Restart services
docker-compose restart


## Shutdown services
docker-compose down
