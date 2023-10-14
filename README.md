# Git Backups

A collection of scripts to locally backup git repositories. The idea is that you can simply clone repositories into your backup folder, either manually or using one of the scripts, and then use the `git-backup-update` to update the repositories regularly.

## Requirements

* git
* Python3 `requests` module


## Preparations

```bash
useradd git-backup --home-dir /opt/git-backup
mkdir -p /opt/git-backup/repos
cd /opt/git-backup
git clone https://github.com/NavidSassan/git-backup.git
chown -R git-backup:git-backup /opt/git-backup
```


## Manually cloning a repo

```bash
sudo -u git-backup -i
# create the path, usually username/repo_name
mkdir -p /opt/git-backup/repos/NavidSassan/git-backup
cd /opt/git-backup/repos/NavidSassan/git-backup

# make sure that the folder ends with `.git`, so that it is automatically updated by `git-backup-update`
git clone --mirror https://github.com/NavidSassan/git-backup git-backup.git
```


## Manually cloning all repos from an GitHub organisation

```bash
ORG=neovim
mkdir -p "$ORG"
cd "$ORG"
wget -qO- "https://api.github.com/orgs/$ORG/repos" | jq ".[].ssh_url" | sed 's#:#/#; s#git@#https://#'| xargs -L 1 git clone --mirror
```


## `git-backup-update` Systemd Service and Timer

The `git-backup-update.service` searches for `.git` folders in the base directory `/opt/root/git-backup/` and pulls the latest updates from the configured remote.

Installation:
```bash
cp etc/systemd/system/git-backup-update.service /etc/systemd/system/git-backup-update.service
cp etc/systemd/system/git-backup-update.timer /etc/systemd/system/git-backup-update.timer
systemctl daemon-reload
systemctl enable --now git-backup-update.timer
```


## `github-star-downloader.py`

This script automatically downloads all the starred GitHub repositories for the given username. Optionally, install the systemd service and timer to do this regularly.

Usage:
```bash
./github-star-downloader.py --help
```

Systemd service and timer:
```bash
cp etc/systemd/system/github-star-downloader@.service /etc/systemd/system/github-star-downloader@.service
cp etc/systemd/system/github-star-downloader@.timer /etc/systemd/system/github-star-downloader@.timer

$EDITOR /etc/systemd/system/github-star-downloader@.service
systemctl daemon-reload
systemctl enable --now github-star-downloader@NavidSassan.timer
```
