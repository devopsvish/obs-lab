# Running the lab on an Ubuntu EC2 instance

## 1. Instance sizing

| Instance | RAM | Enough for | Rough cost |
|---|---|---|---|
| t3.small | 2 GB | **No** — Prometheus will be OOM-killed | — |
| t3.medium | 4 GB | Yes, if you add swap (below) | ~$0.042/hr |
| **t3.large** | 8 GB | Comfortable, all profiles at once | ~$0.083/hr |

An 8-hour lab on t3.large costs well under a dollar. Take the larger instance;
fighting the OOM killer teaches you nothing you want to learn today.

- AMI: **Ubuntu 22.04 or 24.04 LTS**
- Storage: **30 GB gp3** (free-tier limit; images + data need ~6 GB, the rest
  is headroom for Prometheus and Loki)

### Stop the instance when you finish

`docker compose down` does not stop the EC2 bill. Stop the *instance* in the
console when you're done for the day. Your EBS volume persists, so you can
start again tomorrow exactly where you left off.

## 2. Security group — the only thing protecting this lab

None of the tools here has authentication. Prometheus, Alertmanager,
node-exporter and cAdvisor ship with none by design — they assume something in
front of them does that job. Grafana is running with **anonymous admin** for
lab convenience. So your security group *is* the security.

Scope every inbound rule to your own IP:

| Type | Port | Source |
|---|---|---|
| SSH | 22 | My IP |
| Custom TCP | 3000, 9090, 9093, 8090, 8000, 8080 | My IP |

Never `0.0.0.0/0`. If your home broadband IP rotates (common on Indian ISPs),
connections will start timing out — update the SG rule, the lab is fine.

Redis publishes **no host port at all**. `chaos.sh` reaches it via
`docker compose exec`. An internet-facing unauthenticated Redis is one of the
most reliably exploited misconfigurations there is; there is no reason to
expose it.

## 3. Optional: SSH tunnel instead of open ports

If you would rather expose nothing but SSH, bind the ports to loopback:

```bash
sed -i 's/^    ports: \["/    ports: ["127.0.0.1:/' docker-compose.yml
docker compose up -d
```

Then from your laptop:

```bash
ssh -i ~/.ssh/your-key.pem \
  -L 3000:localhost:3000 -L 9090:localhost:9090 \
  -L 9093:localhost:9093 -L 8090:localhost:8090 \
  -L 8000:localhost:8000 -L 8080:localhost:8080 \
  ubuntu@<your-ec2-public-ip>
```

Leave that terminal open; `http://localhost:3000` on your laptop is now Grafana
on the instance. This survives IP changes, which the SG approach does not.

## 4. Docker Engine on Ubuntu

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl make
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
```

Log out and back in for the group change to apply. On EC2, Docker starts on
boot automatically — no `sudo service docker start` needed.

## 5. Add swap (only if you took t3.medium)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

Swap keeps a memory spike from killing Prometheus outright. It does **not**
make the box faster — a service that starts swapping gets dramatically slower,
which is itself a saturation signal you'll learn to spot in Hour 3.5.

## 6. What changes vs a laptop

- **node-exporter is now genuinely interesting.** It's reporting a real Linux
  host — EBS disk I/O, network, real CPU steal time. On a laptop under WSL
  much of this is fiction. Steal time in particular is an EC2-specific signal
  worth understanding.
- **cAdvisor works cleanly** here; no WSL cgroup quirks.
- **Editing code:** either `vim`/`nano` on the box, or VS Code with the
  **Remote - SSH** extension, which gives you the full editor against the
  instance. Recommended.

## 7. Sanity check before Hour 1

```bash
free -h          # 8 GB on t3.large
nproc            # 2
df -h /          # ~24 GB available
docker compose ps
curl -s localhost:9090/-/healthy
```
