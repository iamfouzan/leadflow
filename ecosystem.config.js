// PM2 Ecosystem Configuration for LeadFlow
// Documentation: https://pm2.keymetrics.io/docs/usage/application-declaration/

module.exports = {
  apps: [
    {
      name: 'leadflow-api',
      script: 'gunicorn',
      args: 'app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --access-logfile - --error-logfile - --log-level info',
      cwd: '/opt/leadflow',
      interpreter: '/opt/leadflow/venv/bin/python',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1',
        PYTHONDONTWRITEBYTECODE: '1'
      },
      env_production: {
        ENVIRONMENT: 'production'
      },
      error_file: '/var/log/leadflow/error.log',
      out_file: '/var/log/leadflow/out.log',
      log_file: '/var/log/leadflow/combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 10000,
      shutdown_with_message: true,
      max_restarts: 10,
      min_uptime: '10s',
      // Health check
      health_check: {
        enable: true,
        interval: 30000,
        threshold: 3,
        url: 'http://localhost:8000/health'
      }
    }
  ],

  // Deployment configuration for AWS EC2
  deploy: {
    production: {
      user: 'ubuntu',
      host: 'YOUR_AWS_EC2_IP',
      ref: 'origin/main',
      repo: 'YOUR_GIT_REPOSITORY',
      path: '/opt/leadflow',
      'post-deploy': 'source venv/bin/activate && uv pip install -r requirements.txt && alembic upgrade head && pm2 reload ecosystem.config.js --env production',
      'pre-setup': 'echo "Setting up deployment directory"',
      env: {
        NODE_ENV: 'production'
      }
    }
  }
};
