# setup-api

## Deployment

Run these commands to set up the api

```
cd /root/
```

```
git clone https://github.com/dragonflyminipc/setup-api.git
```

```
cd setup-api
```

```
sudo apt-get update
```

```
sudo apt-get install -y python3-venv
```

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
pip3 install -r requirements.txt
```

```
cp docs/config.example.py config.py
```

Now create .service file in order to run the api:

```
sudo nano /etc/systemd/system/setup_api.service
```

```
[Unit]
Description=Uvicorn instance for the setup api
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/setup-api
Environment="PATH=/root/setup-api/venv/bin"
ExecStart=/root/setup-api/venv/bin/uvicorn app:app --reload --host=0.0.0.0 --port=8866
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Run:

```
sudo systemctl start setup_api
```

```
sudo systemctl enable setup_api
```

```
sudo systemctl status setup_api
```

After the last command you should see "Active: active (running)" in green. You might need to press Ctrl+C if the command line is unavailable.

