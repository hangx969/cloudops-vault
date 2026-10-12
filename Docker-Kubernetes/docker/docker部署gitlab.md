---
title: Docker部署GitLab
tags:
  - docker
  - container
  - gitlab
aliases:
  - GitLab部署
---

# Docker部署GitLab


## docker-compose部署gitlab

- gitlab要求至少4G内存
- 拉取镜像

~~~sh
docker pull gitlab/gitlab-ce
mkdir -p /root/gitlab
~~~

- 编写yml文件

~~~yaml
version: '3.3'

services:
  gitlab:
    image: 'gitlab/gitlab-ce'
    restart: always
    hostname: 'gitlab'
    environment:
      TZ: 'Asia/Shanghai'
      GITLAB_OMNIBUS_CONFIG: |
        # web站点访问地址
        external_url 'http://172.16.183.80:18090'
        gitlab_rails['gitlab_shell_ssh_port'] = 18222
    ports:
      - '18090:18090' # 注意宿主机和容器内部的端口要一致,否则external_url无法访问
      - '8443:443'
      - '18222:22'
    volumes:
      - /root/gitlab/config:/etc/gitlab
      - /root/gitlab/data:/var/opt/gitlab
      - /root/gitlab/logs:/var/log/gitlab
    logging:
      driver: 'json-file'
      options:
        max-size: '1g'
~~~

- 启动容器

~~~sh
docker-compose up -d
~~~

- 浏览器访问IP:18090端口 (出现502说明gitlab启动较慢,需要等)
- [可选]优化启动速度

~~~sh
#docker版本的gitlab会自动启动prometheus|grafana|alertmanager和一系列exporter,非常占用资源,且导致启动比较慢,因此我们可以通过修改 /etc/gitlab/gitlab.rb 来关闭该功能。
#查看启动的服务
ps -ef | grep -E 'prome|exporter|alert|graf'
#修改配置文件
vim /root/gitlab/config/gitlab.rb
#配置以下
alertmanager['enable'] = false
node_exporter['enable'] = false
redis_exporter['enable'] = false
postgres_exporter['enable'] = false
gitlab_exporter['enable'] = false
prometheus_monitoring['enable'] = false
#grafana['enable'] = false

#使配置生效
docker exec -it gitlab /bin/bash
gitlab-ctl reconfigure
#加载完成后会提示gitlab Reconfigured!

ps -ef | grep -E 'prome|exporter|alert|graf'
#浏览器访问172.16.183.80:18090速度加快
~~~

- 修改root密码

~~~sh
#root 密码在gitlab部署目录下gitlab下的gitlab/config/initial_root_password 这个文件中
cat /root/gitlab/config/initial_root_password
#修改默认密码
docker exec -it gitlab /bin/bash
gitlab-rails console -e production
user=User.find(1)
user.password='<password>'
user.password_confirmation='<password>'
user.send_only_admin_changed_your_password_notification!
user.save!
#退出
exit
~~~

## 配置ssh key

- 本地生成ssh-key

~~~sh
ssk-keygen
~~~

- 复制本地ssh-key(~/.ssh/id_rsa.pub)
- gitlab中user settings - ssh keys - add an ssh key添加自己本地的key
- 本地git客户端直接拉取代码即可

## gitlab备份与恢复

- GitLab 提供了简单的备份机制。可以通过以下命令创建备份

```sh
docker exec -t gitlab gitlab-backup create
```

- 要恢复 GitLab 实例,请将备份文件复制到 /data/gitlab/data/backups 目录,然后运行以下命令

```sh
docker exec -t gitlab gitlab-backup restore BACKUP=<your_backup_filename>
```
