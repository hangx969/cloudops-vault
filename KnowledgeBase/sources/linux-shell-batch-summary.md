---
title: Linux-Shell 来源批量摘要
tags:
  - knowledgebase/source
  - linux-shell
date: 2026-09-26
sources:
  - "[[Linux-Shell/LVM-RAID]]"
  - "[[Linux-Shell/MacBook开发环境配置]]"
  - "[[Linux-Shell/Ubuntu基础操作]]"
  - "[[Linux-Shell/Ubuntu部署vftpd]]"
  - "[[Linux-Shell/Linux-learning-notes]]"
  - "[[Linux-Shell/shell-scripts]]"
  - "[[Linux-Shell/ansible安装-rockylinux8]]"
  - "[[Linux-Shell/开源堡垒机jumpserver部署]]"
  - "[[Linux-Shell/Ubuntu安装Wechat]]"
  - "[[Linux-Shell/VMWare-using-notes]]"
  - "[[Linux-Shell/vscode]]"
aliases:
  - "Linux-Shell 批量摘要"
---

## 元信息

- **原始目录**: `Linux-Shell/`
- **文档数量**: 11 篇（统计日期：2026-09-26）
- **领域**: Linux 系统管理、Shell 脚本、网络配置、存储管理、开发环境配置、安全运维
- **摄入日期**: 2026-04-17

---

## 摘要

本目录是一套实战导向的 Linux 与 Shell 运维知识库，覆盖从 Linux 基础概念到高级系统管理的完整链路。内容以 Ubuntu 和 CentOS/Rocky Linux 为主要操作系统，涉及用户与权限管理、存储（LVM/RAID）、网络配置（nmcli/proxy/SSH）、自动化运维（Ansible/Shell 脚本）、安全加固（unattended-upgrade/JumpServer）、终端美化（zsh/oh-my-zsh）、开发工具（VSCode/direnv/VMWare）以及文件同步监控（inotifywait/rsync）等多个子领域。笔记风格统一为"概念介绍 + 操作命令 + 配置示例"，适合作为日常运维和开发环境搭建的速查手册。

---

## 关键知识点

1. LVM 由物理卷（PV）、卷组（VG）、逻辑卷（LV）三层组成，按 `pvcreate` → `vgcreate` → `lvcreate` 顺序创建，逻辑卷分线性（Linear）与条带（Striped）两类。
2. FTP 使用 TCP 21 端口建立控制连接、20 端口建立数据连接，分主动与被动模式；vsftpd 支持匿名、本地、虚拟用户三种认证，以 `pasv_min_port`/`pasv_max_port` 限定被动端口范围，并用 chroot 禁锢家目录。
3. SSH 密钥登录流程为 `ssh-keygen` 生成密钥、`ssh-copy-id` 上传公钥；`~/.ssh/config` 可配置主机别名，here document 配合循环可在多台服务器上远程执行命令。
4. direnv 基于目录自动装载/卸载 `.envrc` 中的环境变量，按 Shell 配置 `direnv hook bash` 或 `direnv hook zsh` 后执行 `direnv allow`，适合管理 PYTHONPATH、API 密钥等项目级变量。
5. 终端代理通过 `http_proxy`/`https_proxy` 环境变量设置，可封装 `proxy_on`/`proxy_off` 函数写入 `~/.bashrc` 或 `~/.zshrc`，并用 `curl cip.cc` 验证是否生效。
6. screen 会话管理：`screen -S` 创建、`Ctrl-A D` 分离、`screen -r` 恢复、`screen -D -r` 强制分离并重新附加、`screen -L -S` 保存会话日志。
7. inotifywait 以 `-m`（持续监控）、`-r`（递归）、`-e`（事件过滤）监控文件变化，结合 rsync 可实现变更自动同步，并交由 systemd 管理同步任务。
8. nmcli 可查看网卡、删除/添加连接配置、修改 IP/网关/DNS，适用于由 NetworkManager 管理的 CentOS、RHEL、Rocky Linux 和 Ubuntu 连接。

---

## 各文档摘要

### [[Linux-Shell/LVM-RAID|LVM 与 RAID]]

- **核心内容**: LVM 逻辑卷管理与 RAID 磁盘阵列技术
- **关键知识点**:
  - LVM 三要素：物理卷（PV）、卷组（VG）、逻辑卷（LV）的概念与创建命令（`pvcreate`、`vgcreate`、`lvcreate`）
  - 线性逻辑卷（Linear LV）与条带逻辑卷（Striped LV）的区别与适用场景
  - LVM 架构分层示意与创建顺序

### [[Linux-Shell/MacBook开发环境配置|MacBook 开发环境配置]]

- **核心内容**: macOS 上的开发终端与工具链配置
- **关键知识点**:
  - macOS 默认 Zsh 与 Oh My Zsh 配置，主题和插件步骤集中在 [[Linux-Shell/Linux-learning-notes#配置 Zsh 终端|Zsh 终端配置]]
  - Homebrew、kubectl、Obsidian 等工具的配置

### [[Linux-Shell/Ubuntu基础操作|Ubuntu 基础管理操作]]

- **核心内容**: Ubuntu 的用户、软件包、存储、网络、启动内核、NVIDIA 显卡驱动与安全更新
- **关键知识点**:
  - `adduser` vs `useradd` 的区别、用户组管理（`groupadd`、`usermod -aG`）
  - `/etc/skel` 目录与用户初始化环境
  - `apt` vs `apt-get` 的对比
  - OpenSSH 服务的安装与开机启动配置
  - [[Linux-Shell/Ubuntu基础操作#启动内核与 GRUB|启动内核与 GRUB]]：查看菜单、设置默认内核、按需暂缓升级
  - [[Linux-Shell/Ubuntu基础操作#NVIDIA 显卡驱动|NVIDIA 驱动]]：检查候选包、安装及 Nouveau 排障
  - [[Linux-Shell/Ubuntu基础操作#安全补丁管理|安全补丁管理]]：unattended-upgrades、ESM 与 cron 安排

### [[Linux-Shell/Ubuntu部署vftpd|Ubuntu 部署 vsftpd]]

- **核心内容**: vsftpd FTP 服务器的部署与配置
- **关键知识点**:
  - FTP 主动模式与被动模式的工作原理
  - TCP 控制连接（端口 21）与数据连接（端口 20）
  - 三种认证模式：匿名用户、本地用户、虚拟用户
  - 被动模式端口范围配置（`pasv_min_port`/`pasv_max_port`）
  - chroot 禁锢家目录保证安全

### [[Linux-Shell/Linux-learning-notes|Linux 学习笔记]]

- **核心内容**: Linux 基础理论与系统入门知识
- **关键知识点**:
  - Linux 学习路径：基本命令 -> 配置 -> Shell 脚本 -> 系统调优 -> 内核
  - Linux 发行版分类（Debian/Slackware/Red Hat/CentOS）
  - Unix 与 Linux 历史（GNU 计划、Linus 与 Linux 内核）
  - VMWare 虚拟机网络连接三种模式（桥接/NAT/仅主机）
  - 磁盘分区（Boot/Swap/根分区）


以下专题已并入这篇综合笔记，原操作摘要保留在这里：

#### 配置 Zsh 终端

- **核心内容**: Zsh 与 oh-my-zsh 的安装与配置（CentOS/Linux 通用）
- **关键知识点**:
  - Zsh 相比 Bash 的优势（插件、命令补全、高亮）
  - yum 安装与源码编译安装两种方式
  - oh-my-zsh 安装（墙内/墙外两种方式）
  - 修改默认 shell（`/etc/shells`）

#### 项目环境变量与 direnv

- **核心内容**: 使用 direnv 工具进行项目级环境变量隔离管理
- **关键知识点**:
  - direnv 工作原理：基于目录自动装载/卸载 `.envrc` 中的环境变量
  - 应用场景：项目依赖管理（PYTHONPATH）、保密信息管理（API 密钥）
  - 安装与使用：按 Shell 选择 `direnv hook bash` 或 `direnv hook zsh`，再执行 `direnv allow`

#### 终端代理配置

- **核心内容**: 终端 HTTP/HTTPS 代理的快速开关配置
- **关键知识点**:
  - 通过 `http_proxy`/`https_proxy` 环境变量设置代理
  - 编写 `proxy_on`/`proxy_off` 函数实现快速切换
  - 在 `~/.bashrc` 或 `~/.zshrc` 中加载函数，供新终端使用
  - `curl cip.cc` 验证代理是否生效

#### screen 后台会话

- **核心内容**: 使用 screen 命令管理后台终端会话
- **关键知识点**:
  - 创建会话（`screen -S`）、分离（`Ctrl-A D`）、恢复（`screen -r`）
  - 退出会话（`exit` 或 `-X quit`）
  - 强制分离并重新附加（`screen -D -r`）
  - 保存会话日志（`screen -L -S`）

#### 系统信息与资源监控

- **核心内容**: Linux 系统资源监控与信息查询命令
- **关键知识点**:
  - 内存查看：`/proc/meminfo`、`free -h`、`ps aux --sort -rss`、`top`（按 M 排序）、`vmstat`
  - CPU 查看：`top` 各参数含义（us/sy/ni/id/wa/hi/si）
  - 磁盘查看：`df -h`、`du -sh`、`lsblk -f`、`fdisk -l`
  - OS 信息：`cat /etc/*release`、`uname -a`

#### inotifywait 文件监控与同步

- **核心内容**: 使用 inotifywait 监控文件系统变化并触发 rsync 同步
- **关键知识点**:
  - inotify API 与 inotify-tools 工具包（inotifywait/inotifywatch）
  - inotifywait 基本用法：`-m`（持续监控）、`-r`（递归）、`-e`（事件过滤）
  - 结合 rsync 实现文件变化自动同步脚本
  - systemd 管理 rsync 同步任务

#### nmcli 网络配置

- **核心内容**: 使用 nmcli 命令管理 Linux 网络（替代传统配置文件方式）
- **关键知识点**:
  - NetworkManager 替代 network 服务的背景
  - nmcli 常用操作：查看网卡、删除/添加配置、修改 IP/网关/DNS
  - 适用于由 NetworkManager 管理的 CentOS、RHEL、Rocky Linux 和 Ubuntu 连接

#### SSH 连接与远程执行

- **核心内容**: SSH 协议原理、密钥登录与 SCP 文件传输
- **关键知识点**:
  - SSH 连接流程（公钥指纹验证、known_hosts 管理）
  - `~/.ssh/config` 客户端配置与别名使用
  - 密钥登录过程（`ssh-keygen` 生成、`ssh-copy-id` 上传公钥）
  - `scp` 命令基本语法（本地与远程间的文件复制）
  - VSCode 远程免密连接配置
  - 通过 here document 和循环在一台或多台服务器上远程执行命令

#### Samba 文件共享

- **核心内容**: Linux 与 Windows 之间的 SMB/CIFS 文件共享
- **关键知识点**:
  - SMB 协议背景与 Samba 的历史
  - smb 和 nmb 两个核心服务的作用
  - 服务端搭建流程：创建 nologin 用户、配置共享目录、编辑 `smb.conf`
  - 防火墙与 SELinux 配置（`firewall-cmd`、`chcon`）

### [[Linux-Shell/shell-scripts|Shell 脚本]]

- **核心内容**: Shell 脚本编程实例
- **关键知识点**:
  - 用户删除自动化脚本（交互式输入处理、超时控制）
  - Bash 函数定义与调用（`get_answer`、`process_answer`）
  - case 语句、while 循环、read 超时读取
  - 变量清理与脚本退出处理

### [[Linux-Shell/ansible安装-rockylinux8|Ansible 安装 - Rocky Linux 8]]

- **核心内容**: 在 Rocky Linux 8 上搭建 Ansible 自动化运维环境
- **关键知识点**:
  - 实验环境规划（controller/node 角色划分）
  - 网络配置（nmcli）、hosts 配置、SSH 互信
  - 防火墙与 SELinux 关闭、基础软件包安装
  - Ansible 安装与版本验证、环境配置

### [[Linux-Shell/开源堡垒机jumpserver部署|JumpServer 部署]]

- **核心内容**: 开源堡垒机 JumpServer 的部署参考
- **关键知识点**:
  - JumpServer 简洁版与详细版部署教程链接
  - 官方 GitHub 仓库与安装文档

### [[Linux-Shell/Ubuntu安装Wechat|Ubuntu 安装微信]]

- **核心内容**: 在 Ubuntu 22.04 上通过 Flatpak 安装微信
- **关键知识点**:
  - 安装星火商店（Flatpak）
  - 从 GitHub 下载微信 Flatpak 安装包
  - `flatpak install` 安装命令

### [[Linux-Shell/VMWare-using-notes|VMWare 共享目录]]

- **核心内容**: VMWare 虚拟机挂载宿主机共享目录
- **关键知识点**:
  - VMWare Tools 安装后共享目录不可见的解决方案
  - `mount -t fuse.vmhgfs-fuse` 手动挂载命令
  - `-o allow_other` 允许普通用户访问
  - 重启后需重新挂载的注意事项

### [[Linux-Shell/vscode|VSCode 命令行安装插件]]

- **核心内容**: 通过命令行为 VSCode 安装扩展插件
- **关键知识点**:
  - 从 VSCode 插件市场下载 `.vsix` 安装包
  - `code --install-extension` 命令行安装方式

## 涉及的概念与实体

### 概念

- [[KnowledgeBase/concepts/LVM|LVM 逻辑卷管理]]
- [[KnowledgeBase/concepts/RAID|RAID 磁盘阵列]]
- [[KnowledgeBase/concepts/SSH|SSH 安全远程连接]]
- [[KnowledgeBase/concepts/SMB-CIFS|SMB/CIFS 文件共享协议]]
- [[KnowledgeBase/concepts/FTP|FTP 文件传输协议]]
- [[KnowledgeBase/concepts/环境变量|环境变量管理]]
- [[KnowledgeBase/concepts/用户权限管理|Linux 用户与权限管理]]
- [[KnowledgeBase/concepts/包管理|Linux 包管理（apt/yum）]]
- [[KnowledgeBase/concepts/网络代理|网络代理配置]]
- [[KnowledgeBase/concepts/内核管理|Linux 内核管理]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]
- [[KnowledgeBase/concepts/文件系统监控|文件系统监控与同步]]
- [[KnowledgeBase/concepts/终端会话管理|终端会话管理]]

### 实体

- [[KnowledgeBase/entities/Ansible|Ansible]]
- [[KnowledgeBase/entities/JumpServer|JumpServer 堡垒机]]
- [[KnowledgeBase/entities/oh-my-zsh|oh-my-zsh]]
- [[KnowledgeBase/entities/direnv|direnv]]
- [[KnowledgeBase/entities/inotifywait|inotifywait]]
- [[KnowledgeBase/entities/rsync|rsync]]
- [[KnowledgeBase/entities/screen|screen]]
- [[KnowledgeBase/entities/nmcli|nmcli]]
- [[KnowledgeBase/entities/vsftpd|vsftpd]]
- [[KnowledgeBase/entities/Samba|Samba]]
- [[KnowledgeBase/entities/VMWare|VMWare]]
- [[KnowledgeBase/entities/VSCode|VSCode]]
- [[KnowledgeBase/entities/NVIDIA|NVIDIA 显卡驱动]]
- [[KnowledgeBase/entities/NetworkManager|NetworkManager]]
- [[KnowledgeBase/entities/GRUB|GRUB 引导加载器]]
- [[KnowledgeBase/entities/Flatpak|Flatpak]]
- [[KnowledgeBase/entities/SELinux|SELinux]]

---

## 交叉主题发现

1. **SSH 贯穿多个文档**: SSH 不仅在 [[Linux-Shell/Linux-learning-notes#SSH 连接与远程执行|SSH 连接]] 中作为主题详细讲解，还在 [[Linux-Shell/ansible安装-rockylinux8|Ansible 安装]]（SSH 互信）、[[Linux-Shell/Linux-learning-notes#远程执行多个命令|SSH 远程执行]]、[[Linux-Shell/Ubuntu基础操作|Ubuntu 基础操作]]（sshd 安装）、[[Linux-Shell/开源堡垒机jumpserver部署|JumpServer 部署]] 中反复出现，说明 SSH 是 Linux 远程管理的核心基础设施。

2. **网络配置的多层次覆盖**: 从底层的 [[Linux-Shell/Linux-learning-notes#nmcli 网络配置|nmcli 网络配置]] 到应用层的 [[Linux-Shell/Linux-learning-notes#终端代理配置|终端代理配置]]，再到服务层的 [[Linux-Shell/Ubuntu部署vftpd|FTP 部署]] 和 [[Linux-Shell/Linux-learning-notes#Samba 文件共享|Samba 文件共享]]，形成了完整的网络配置知识链。

3. **zsh/oh-my-zsh 重复出现**: [[Linux-Shell/Linux-learning-notes#配置 Zsh 终端|配置 zsh 终端]] 和 [[Linux-Shell/MacBook开发环境配置|MacBook 开发环境配置]] 都涉及 oh-my-zsh 的安装配置，共用的主题与插件配置现集中在前者，后者保留 macOS 开发工具链并交叉引用。

4. **Ubuntu 专题集群**: 共有 3 篇文档专注于 Ubuntu 系统（基础操作、安装微信、vsftpd 部署）；基础操作页已合并安全补丁、显卡驱动和启动内核，形成了一个 Ubuntu 系统管理的子知识体系。

5. **存储管理的纵深**: 从 [[Linux-Shell/LVM-RAID|LVM 与 RAID]] 的逻辑卷与磁盘阵列，到 [[Linux-Shell/Linux-learning-notes#系统信息与资源监控|系统信息查看]] 中的 `df`/`du`/`lsblk`/`fdisk` 磁盘监控命令，到 [[Linux-Shell/VMWare-using-notes|VMWare 共享目录]] 的虚拟化存储挂载，覆盖了存储管理的不同层面。

6. **文件同步与监控**: [[Linux-Shell/Linux-learning-notes#inotifywait 文件监控与同步|inotifywait]] 与 [[Linux-Shell/Linux-learning-notes#Samba 文件共享|Samba]] 都解决文件共享/同步问题，但前者侧重实时监控触发同步，后者侧重跨平台网络共享，两者可互补。

7. **自动化运维工具链**: [[Linux-Shell/ansible安装-rockylinux8|Ansible]]（配置管理）、[[Linux-Shell/开源堡垒机jumpserver部署|JumpServer]]（安全审计）、[[Linux-Shell/shell-scripts|Shell 脚本]]（任务自动化）、[[Linux-Shell/Linux-learning-notes#screen 后台会话|screen]]（后台任务管理）共同构成了一套运维自动化工具链。

---

## 值得注意

- 平台边界：Ansible 环境基于 Rocky Linux 8，微信安装基于 Ubuntu 22.04 + Flatpak，Zsh 配置按 CentOS/Linux 通用方式编写；原文强调使用 nmcli 前应先确认连接实际由 NetworkManager 管理，不能仅凭发行版推断。
- 安全处理不一致：Ansible 实验环境直接停用 firewalld 并关闭 SELinux，而 Samba 部分通过 `firewall-cmd` 放行服务、`chcon` 设置 SELinux 上下文；前者属于实验环境的简化做法。
- VMWare 共享目录通过 `mount -t fuse.vmhgfs-fuse` 手动挂载后，虚拟机重启需要重新挂载。
- 内容深度不均：JumpServer 笔记只收录简洁版/详细版教程、GitHub 仓库与安装文档链接，本库未保存具体部署步骤。
