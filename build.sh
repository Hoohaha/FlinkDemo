echo "build log_analyzer-0.2.tar.gz"
cd log_analyzer_module
python setup.py sdist
cd ..
mv log_analyzer_module/dist/log_analyzer-0.2.tar.gz ./cached

echo "build docker images..."
docker-compose --env-file .env build
