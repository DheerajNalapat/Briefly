# Briefly Bot - Oracle Cloud Deployment Checklist

## ✅ Pre-Deployment Checklist

### **1. Oracle Cloud Account**

- [ ] Created Oracle Cloud account
- [ ] Verified email address
- [ ] Signed in to Oracle Cloud Console
- [ ] Familiarized with the interface

### **2. API Keys Ready**

- [ ] NewsAPI.org API key obtained
- [ ] Slack Bot Token obtained
- [ ] Slack Channel ID obtained
- [ ] OpenAI API key OR Google API key obtained

### **3. Local Preparation**

- [ ] Project files ready
- [ ] Environment variables documented
- [ ] Deployment scripts tested locally

## 🚀 Deployment Steps

### **1. Create Oracle Cloud Instance**

- [ ] Navigate to Compute → Instances
- [ ] Click "Create Instance"
- [ ] Configure instance:
  - [ ] Name: `briefly-bot-server`
  - [ ] Image: `Oracle Linux 8` or `Ubuntu 20.04`
  - [ ] Shape: `VM.Standard.E2.1.Micro` (Always Free)
  - [ ] SSH Keys: Generated/uploaded
  - [ ] Networking: Default VCN
- [ ] Click "Create"
- [ ] Wait for instance to be running
- [ ] Note the public IP address

### **2. Connect to Instance**

- [ ] SSH into instance: `ssh opc@<instance-ip>`
- [ ] Verify connection works
- [ ] Check system information

### **3. Run Deployment Script**

- [ ] Upload deployment script: `scp crons/deploy_oracle_cloud.sh opc@<instance-ip>:~/`
- [ ] Make executable: `chmod +x deploy_oracle_cloud.sh`
- [ ] Run script: `./deploy_oracle_cloud.sh`
- [ ] Wait for completion
- [ ] Verify all packages installed

### **4. Upload Project Files**

- [ ] Upload project: `scp -r . opc@<instance-ip>:~/briefly-bot/`
- [ ] Verify files uploaded correctly
- [ ] Check project structure

### **5. Configure Environment**

- [ ] Copy template: `cp .env.template .env`
- [ ] Edit environment file: `nano .env`
- [ ] Fill in all required API keys
- [ ] Verify environment variables loaded

### **6. Set Up Cron Job**

- [ ] Run setup script: `./crons/setup_cron.sh`
- [ ] Verify cron job added: `crontab -l`
- [ ] Check cron service running: `sudo systemctl status cron`

### **7. Test Functionality**

- [ ] Test cron job manually: `./crons/run_daily_news.sh`
- [ ] Check logs: `tail -f logs/briefly_cron_$(date +%Y%m%d).log`
- [ ] Verify Slack message sent
- [ ] Check for any errors

## 🔧 Post-Deployment Verification

### **1. System Health**

- [ ] Check disk space: `df -h`
- [ ] Check memory: `free -h`
- [ ] Check CPU: `htop`
- [ ] Verify internet connectivity

### **2. Cron Job Status**

- [ ] Verify cron job scheduled: `crontab -l`
- [ ] Check cron service: `sudo systemctl status cron`
- [ ] Test manual execution
- [ ] Monitor logs for errors

### **3. Security Configuration**

- [ ] Verify SSH key authentication
- [ ] Check firewall settings
- [ ] Secure .env file: `chmod 600 .env`
- [ ] Review security lists in Oracle Cloud

## 📊 Monitoring Setup

### **1. Log Monitoring**

- [ ] Set up log rotation
- [ ] Create monitoring script
- [ ] Test log access
- [ ] Verify log file permissions

### **2. System Monitoring**

- [ ] Install monitoring tools: `htop`, `iotop`
- [ ] Set up resource alerts
- [ ] Create backup script
- [ ] Test backup functionality

### **3. Performance Optimization**

- [ ] Monitor cron job execution time
- [ ] Optimize article count if needed
- [ ] Check API rate limits
- [ ] Verify memory usage

## 🚨 Troubleshooting Checklist

### **Common Issues**

- [ ] Cron job not running

  - [ ] Check cron service status
  - [ ] Verify crontab syntax
  - [ ] Check file permissions
  - [ ] Review cron logs

- [ ] Environment variables not loaded

  - [ ] Verify .env file exists
  - [ ] Check file permissions
  - [ ] Test variable loading
  - [ ] Review shell script

- [ ] Python environment issues

  - [ ] Activate conda environment
  - [ ] Check package installation
  - [ ] Verify Python version
  - [ ] Test imports

- [ ] Network connectivity
  - [ ] Test internet connection
  - [ ] Check API endpoints
  - [ ] Verify firewall rules
  - [ ] Review security lists

### **Oracle Cloud Specific**

- [ ] Instance stopped

  - [ ] Check Oracle Cloud Console
  - [ ] Restart instance if needed
  - [ ] Review billing/quotas
  - [ ] Check resource limits

- [ ] Resource limits exceeded
  - [ ] Monitor CPU usage
  - [ ] Check memory consumption
  - [ ] Review disk space
  - [ ] Consider optimization

## 📈 Maintenance Schedule

### **Daily**

- [ ] Check cron job execution
- [ ] Review error logs
- [ ] Monitor system resources

### **Weekly**

- [ ] Review all logs
- [ ] Check system performance
- [ ] Verify backup status
- [ ] Update packages if needed

### **Monthly**

- [ ] Full system health check
- [ ] Review and optimize performance
- [ ] Update dependencies
- [ ] Test disaster recovery

### **Quarterly**

- [ ] Review Oracle Cloud quotas
- [ ] Optimize resource usage
- [ ] Update security configurations
- [ ] Plan for scaling if needed

## 🎯 Success Criteria

### **Deployment Complete When:**

- [ ] Oracle Cloud instance running
- [ ] All dependencies installed
- [ ] Project files uploaded
- [ ] Environment configured
- [ ] Cron job scheduled
- [ ] Manual test successful
- [ ] Slack message sent
- [ ] Logs generated correctly
- [ ] No errors in system

### **Production Ready When:**

- [ ] Cron job runs automatically
- [ ] Daily news digest sent
- [ ] System stable for 7+ days
- [ ] Logs clean (no errors)
- [ ] Resource usage normal
- [ ] Monitoring in place
- [ ] Backup strategy working
- [ ] Security configured

## 📞 Support Resources

### **Documentation**

- [ ] Oracle Cloud Documentation
- [ ] Cron Job Setup Guide
- [ ] Troubleshooting Guide
- [ ] Monitoring Guide

### **Useful Commands**

```bash
# System status
htop
df -h
free -h
uptime

# Cron management
crontab -l
sudo systemctl status cron
sudo systemctl restart cron

# Log monitoring
tail -f logs/cron.log
tail -f logs/briefly_cron_$(date +%Y%m%d).log

# Environment
conda activate news-finder
source .env
echo $NEWSAPI_KEY
```

## 🎉 Completion

**Deployment successful when all items above are checked!**

Your Briefly Bot will now automatically send daily AI/ML news digests to your Slack channel at 8:30 AM every day, running on Oracle Cloud's Always Free tier.

