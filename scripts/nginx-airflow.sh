sudo apt-get install nginx -y
sudo cp configs/default-airflow /etc/nginx/sites-enabled/default
sudo nginx -s reload
