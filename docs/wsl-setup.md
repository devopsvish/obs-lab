# WSL2 setup on a 8 GB laptop

Do **not** install Docker Desktop. It runs its own VM and costs ~1.5–2 GB of
RAM before you start a single container. Install Docker Engine inside WSL.

## 1. Cap what WSL is allowed to take

Create `C:\Users\<you>\.wslconfig` **in Windows**:

```ini
[wsl2]
memory=6GB
processors=4
swap=2GB
```

Then in PowerShell:

```powershell
wsl --shutdown
```

Reopen your Ubuntu terminal.

## 2. Install Docker Engine inside Ubuntu (WSL)

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER      # run docker without sudo
sudo service docker start
```

Log out and back in (`exit`, then reopen), then verify:

```bash
docker run --rm hello-world
docker compose version
```

If Docker does not start on boot, add this to `~/.bashrc`:

```bash
sudo service docker status > /dev/null || sudo service docker start
```

## 3. Put the repo on the Linux filesystem, not /mnt/c

```bash
mkdir -p ~/projects && cd ~/projects
# unzip obs-lab here
```

Files under `/mnt/c` are 5–20x slower from inside WSL and will make Docker
builds crawl. Keep the repo in `~/projects`.

Open it in VS Code with:

```bash
cd ~/projects/obs-lab
code .
```

VS Code will install the WSL server the first time. Recommended extensions:
Python, Docker, YAML, Prometheus.

## 4. Disk hygiene (you have 25 GB free)

This lab uses roughly 2.5 GB of images plus ~1 GB of data. That is fine, but
WSL's virtual disk grows and never shrinks by itself. After the lab:

```bash
docker system prune -af --volumes
```

To reclaim the space back to Windows, in PowerShell:

```powershell
wsl --shutdown
Optimize-VHD -Path "$env:LOCALAPPDATA\Packages\<distro>\LocalState\ext4.vhdx" -Mode Full
```

(Optimize-VHD needs Hyper-V tools; if unavailable, `diskpart` → `compact vdisk`.)

## 5. Sanity check before Hour 2

```bash
free -h        # should show ~6 GB total
nproc          # should show 4
df -h ~        # should show plenty free
```
