#!/bin/bash
set -euxo pipefail

exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y ca-certificates curl git gnupg lsb-release apt-transport-https software-properties-common

systemctl stop docker || true
snap remove docker || true
apt-get remove -y docker docker-engine docker.io containerd runc podman-docker || true
apt-get autoremove -y || true

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
DOCKER_CE_VERSION="$(apt-cache madison docker-ce | awk '/5:28\.5\./ { print $3; found=1; exit } END { if (!found) exit 0 }')"
DOCKER_CLI_VERSION="$(apt-cache madison docker-ce-cli | awk '/5:28\.5\./ { print $3; found=1; exit } END { if (!found) exit 0 }')"

echo "Resolved Docker CE version: $${DOCKER_CE_VERSION:-<none>}"
echo "Resolved Docker CLI version: $${DOCKER_CLI_VERSION:-<none>}"

if [ -z "$${DOCKER_CE_VERSION}" ] || [ -z "$${DOCKER_CLI_VERSION}" ]; then
  echo "Could not find Docker 28.5.x packages in the Docker APT repository."
  exit 1
fi

apt-get install -y \
  docker-ce="$${DOCKER_CE_VERSION}" \
  docker-ce-cli="$${DOCKER_CLI_VERSION}" \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
apt-mark hold docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

docker version
docker compose version

mkdir -p /opt
mkdir -p /opt/consulting
chown -R ubuntu:ubuntu /opt/consulting
if [ -d /opt/consulting/.git ]; then
  sudo -u ubuntu git -C /opt/consulting fetch --all
  sudo -u ubuntu git -C /opt/consulting checkout ${repo_branch}
  sudo -u ubuntu git -C /opt/consulting pull origin ${repo_branch}
else
  sudo -u ubuntu git clone --branch ${repo_branch} ${repo_url} /opt/consulting
fi
chown -R ubuntu:ubuntu /opt/consulting

cat >/opt/consulting/.env <<EOF
DOMAIN=${app_domain}
LETSENCRYPT_EMAIL=${letsencrypt_email}

POSTGRES_USER=${postgres_user}
POSTGRES_PASSWORD=${postgres_password}
POSTGRES_DB=${postgres_db}
DB_URI=postgresql+psycopg2://${postgres_user}:${postgres_password}@db:5432/${postgres_db}
DATABASE_URL=postgresql://${postgres_user}:${postgres_password}@db:5432/${postgres_db}

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379

API_KEY=${api_key}
JWT_SECRET_KEY=${jwt_secret_key}
JWT_REFRESH_SECRET_KEY=${jwt_refresh_secret_key}

AWS_REGION=${aws_region}
AWS_DEFAULT_REGION=${aws_region}
AVATARS_BUCKET_NAME=${avatars_bucket_name}
AVATARS_BASE_URL=${avatars_base_url}
USE_S3_AVATARS=${use_s3_avatars}

SEED_DEMO_DATA=${seed_demo_data}
EOF

cd /opt/consulting
docker compose -f docker-compose.prod.yml down --remove-orphans || true
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
