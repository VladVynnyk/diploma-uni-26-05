#!/bin/bash
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y ca-certificates curl git gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable docker
systemctl start docker

mkdir -p /opt
if [ -d /opt/consulting/.git ]; then
  git -C /opt/consulting fetch --all
  git -C /opt/consulting checkout ${repo_branch}
  git -C /opt/consulting pull origin ${repo_branch}
else
  git clone --branch ${repo_branch} ${repo_url} /opt/consulting
fi

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
docker compose -f docker-compose.prod.yml up -d --build
