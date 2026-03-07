docker run -d --name redis -p 6379:6379 redis:latest


# Testing
docker exec -it redis redis-cli
docker exec my-redis redis-cli SET mykey "Hello from Docker"
docker exec my-redis redis-cli GET mykey
