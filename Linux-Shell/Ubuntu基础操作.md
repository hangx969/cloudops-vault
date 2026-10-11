---
title: Ubuntu基础操作
tags:
  - linux
  - ubuntu
  - admin
  - storage
  - network
  - kernel
  - grub
  - nvidia
  - security
  - unattended-upgrade
aliases:
  - Ubuntu基础管理操作
  - Ubuntu修改启动内核
  - Ubuntu安装NVIDIA显卡驱动
  - Ubuntu unattended-upgrade管理
---

# Ubuntu 基础操作

以下是 Ubuntu 系统管理练习，以及启动内核、显卡驱动和安全更新的操作记录。命令中的设备名、内核版本、网络地址和驱动版本均需按本机环境核对。

## 用户与软件包管理

### 用户与用户组

- Create a user with your name with uid 2001, with default config

  ~~~sh
  adduser --uid 2001 hangx
  ~~~

  > [!info] adduser vs useradd
  > - adduser和useradd都可以在ubuntu中创建新用户。但是二者还有区别：
  >
  >   - `useradd` 是一个基本的 Linux 命令，它直接创建新的用户。它不会自动创建用户的主目录，也不会复制 `/etc/skel` 目录中的文件到新用户的主目录。如果你想要这些功能，**你需要手动指定 `-m` 或 `-k` 选项。**
  >   - `adduser` 是 Debian 和 Ubuntu 系统中的一个脚本，它是 `useradd` 的一个更友好的前端。这个脚本会自动创建新用户的主目录，复制 `/etc/skel` 目录中的文件，以及进行其他一些设置。它也会提供一个交互式的界面来收集新用户的信息，如全名和密码。
  >
  > - 什么是default config：
  >
  >   - 用户的主目录（通常是 `/home/username`）
  >   - 用户的默认 shell（通常是 `/bin/bash` 或 `/bin/sh`）
  >   - 用户的用户组（通常与用户名相同）
  >   - 用户的用户 ID 和组 ID（通常由系统自动分配）
  >
  > - 在 Ubuntu 中，用户的默认配置存储在 `/etc/default/useradd` 文件中。
  >
  > - `/etc/skel` 目录包含了一些初始化文件，这些文件会在创建新用户时复制到新用户的主目录中。这些文件通常包括一些 shell 配置文件（如 `.bashrc` 和 `.profile`），以及其他一些默认的设置文件。
  >
  >   - 这样做的目的是为了提供一个统一的初始环境给所有新创建的用户。这些文件定义了用户的 shell 环境，包括命令别名、环境变量、shell 提示符等等。通过修改 `/etc/skel` 目录中的文件，系统管理员可以控制新用户的初始环境。
  >
  >   - 例如，如果你想要所有新用户都有一个特定的命令别名，你可以在 `/etc/skel/.bashrc` 文件中添加这个别名，然后所有新创建的用户都会在他们的 `.bashrc` 文件中有这个别名。

- Create group zen with gid 2002 and add user into it

  ~~~sh
  groupadd -g 2002 zen
  usermod -aG zen hangx #`-aG`（指定要添加到的组）和用户名
  ~~~

  > [!info] 用户组管理
  > - 如何在 Ubuntu 中查看用户所属的用户组？
  >
  >   ~~~sh
  >   groups newuser #这个命令将会列出用户 newuser 所属的所有用户组。
  >   id newuser #这个命令将会输出用户 newuser 的用户 ID、组 ID 以及所属的用户组。
  >   ~~~
  >
  > - -aG是将用户添加到组里。**-g 是修改用户的主用户组**。
  >
  > - 主用户组的作用主要是文件系统权限管理。每个文件和目录都有一个用户所有者和一个组所有者。用户所有者通常是创建这个文件或目录的用户，而组所有者默认是创建这个文件或目录的用户的**主用户组**。
  >
  >   - 文件和目录的权限被分为三组：用户权限、组权限和其他权限。用户权限适用于用户所有者，组权限适用于组所有者，其他权限适用于所有其他用户。
  >
  >   - 通过设置组所有权和组权限，你可以控制哪些用户可以读取、写入或执行这个文件或目录。
  >   - 例如，如果你想要让一个用户组的所有用户都可以读取和写入一个文件，你可以将这个文件的组所有权设置为这个用户组，然后设置组权限为读写权限。

- Verify this task if all setup correctly

  ~~~sh
  #查看用户
  cat /etc/passwd | grep hangx
  #查看用户所属的组
  groups hangx
  ~~~

### 安装 SSH 服务

~~~sh
apt install -y openssh-server
systemctl enable --now ssh
~~~

> [!info] apt vs apt-get
> `apt`和`apt-get`都是Ubuntu和其他基于Debian的系统中的包管理工具。它们都可以用来安装、更新、升级和删除软件包。
>
> 主要的区别在于：
>
> 1. **用户友好性**：`apt`被设计为更用户友好，它提供了颜色编码的输出和进度条等功能。
> 2. **命令简洁性**：`apt`的命令更简洁。例如，`apt full-upgrade`相当于`apt-get dist-upgrade`。
> 3. **输出**：`apt`提供了更简洁、更易于阅读的输出。
> 4. **脚本兼容性**：`apt` 面向交互使用，输出格式可能随版本变化；脚本中优先使用接口更稳定的 `apt-get` 和 `apt-cache`。这与是否为 LTS 版本无关。
>
> apt命令使用：
>
> - `apt-get install <package-name>=<version-number>` -- 安装特定版本的包
> - `apt-cache policy package name` -- 查看一个包的可用版本
> - `dpkg --get-selections`, `apt list --installed`可以查看已经安装的包
> - `apt remove <package-name>` -- 卸载软件包，但是不会卸载配置文件
> - `apt purge <package name>` -- 卸载软件包，包括配置文件

### 更新软件包

~~~sh
apt update
apt list --upgradable
#查看kernel header的包
apt list --installed | grep linux-header
apt-mark hold linux-headers-6.2.0-1018-azure linux-headers-azure
apt upgrade
~~~

上述 `linux-headers-6.2.0-1018-azure` 是原练习环境的包名，只有本机安装了该包且确需暂停升级时才应执行 `hold`；完成维护后用 `apt-mark unhold` 解除。

> [!info] apt update vs apt upgrade
> - apt update和apt upgrade的区别
>
> 1. **apt update**：此命令用于更新系统的包列表。它会从你在系统中配置的软件源获取最新的包信息，包括新的软件包和现有软件包的更新。这个命令不会实际安装或升级任何软件包，只是更新了系统知道的可用软件包的信息。
> 2. **apt upgrade**：此命令用于实际升级系统中的软件包。它会查看你已经安装的软件包，并检查是否有可用的更新。如果有，它会下载并安装这些更新。这个命令需要在运行`apt update`之后运行，以确保你的系统知道所有可用的更新。
>
> - 如何在apt upgrade时排除掉特定的包
>   - `apt-mark hold`排除掉特定的包
>   - `apt-mark showhold`可以查看标记为hold的包
>   - `apt-mark unhold`可以取消hold
>
> - 如何辨别哪些包是kernel header
>   - 在Ubuntu和其他基于Debian的系统中，内核头文件通常包含在以下几个包中：
>     - `linux-headers-generic`：这个包包含了通用内核的头文件。这些头文件对于编译大多数内核模块是必需的。
>     - `linux-headers-$(uname -r)`：这个包包含了当前运行的特定版本内核的头文件。这些头文件对于编译针对当前内核版本的模块是必需的。
>
>   - 检查是否安装kernel header
>
>     ~~~bash
>     dpkg-query -s linux-headers-$(uname -r)
>     ~~~
>
> - 更多关于Ubuntu linux kernel的信息：[linux - ubuntu22.04 的内核版本为什么有多个？ - SegmentFault 思否](https://segmentfault.com/q/1010000044156233)
>
>   - ubuntu kernel：[https://ubuntu.com/kernel](https://link.segmentfault.com/?enc=wiXbkZbHsoC%2F8N1euDgGvg%3D%3D.zeyQNXTuqhLTzd3p%2B0TxOBlG%2F%2B4RYIn4VkzZz28pWhI%3D)说明，最新的LTS镜像会安装`-hwe`内核，这个是高版本的内核，通常应该是下个LTS版本使用的内核，每个版本的内核支持时间可以在上述链接找到图文说明。[https://ubuntu.com/kernel/lifecycle](https://link.segmentfault.com/?enc=N1Nt3jzKquIbBccUe3MvzA%3D%3D.B6HQsmVKJP4l21kBfysTFzGpNuij9%2BDYjvkNZtC46Fn3DcwRmjeoZiWxOuYOAUer)
>   - 此外，ubuntu还有其他可用备选内核，参考: [https://ubuntu.com/kernel/variants#current-variant-kernels](https://link.segmentfault.com/?enc=2meiVWW6SxS0FtZ0j%2BCsHw%3D%3D.xroP7rO%2FKNQsvIjnmDu%2BE7C9%2FuRsiH4bmjz46aG%2B%2BOYbx5s933QjhuolCLSwyQeHqTPGf3%2ByrshKb5zpr8NXpw%3D%3D)
>   - 简单来说，就是Ubuntu认为硬件更新迭代可能比较快，而LTS版本支持时间比较长(已经从20.04版本之前的5年延长到目前的10年支持)，所以旧的LTS版本可能无法跟上新硬件的适配，因此Ubuntu搞了个`HWE`包，让旧的LTS版本用上新的LTS版本的内核以便可以在不升级整个OS版本(`do-release-upgrade`)的情况下使用新版本的内核，以支持新的硬件。

### 配置 fdisk 的 sudo 权限

~~~sh
visudo #visudo提供锁定和语法检查，比直接vim /etc/sudoers更有用
#末尾添加一行：
hangx ALL=(ALL:ALL) NOPASSWD: /usr/bin/fdisk
#ctrkl+O 保存，ctrl+X退出
~~~

> [!info] sudoers配置语法
> username ALL=(ALL:ALL) NOPASSWD: /path/to/command命令解释：
>
> - `username`：这是用户名，表示这条规则适用于哪个用户。
> - `ALL=`：这是主机名部分，表示这条规则适用于哪些主机。在这里，`ALL`表示这条规则适用于所有主机。
> - `(ALL:ALL)`：这是运行命令的用户和组。第一个`ALL`表示命令可以以任何其他用户的身份运行，第二个`ALL`表示命令可以以任何组的身份运行。
> - `NOPASSWD:`：这表示用户在执行这条命令时不需要输入密码。
> - `/path/to/command`：这是用户可以执行的命令的完整路径。
>
> 如何查看一个用户的sudo权限：
>
> ```sh
> su - username
> su -l
> ```

### 用户登录与 SSH 密钥

1. 在发起连接的用户账户下生成密钥，并将该用户的公钥复制到 VM 上的 `hangx` 账户：

   ~~~sh
   ssh-keygen -t ed25519
   ssh-copy-id -i ~/.ssh/id_ed25519.pub hangx@<VM IP>
   ~~~

2. 登录后检查磁盘：

   ~~~sh
   sudo fdisk -l
   ~~~

## 存储管理

1. Check current LVM setup

   ~~~sh
   lsblk -f #看一下disk情况
   pvdisplay
   vgdisplay
   lvdisplay
   ~~~

2. Create a partition volume_zen of 2GB

   ~~~sh
   fdisk /dev/sda
   #使用fdisk命令启动磁盘分区工具。假设你想在/dev/sda磁盘上创建分区，你可以使用以下命令：
   #在fdisk命令提示符下，按n来创建一个新的分区。
   #接下来，它会询问你要创建主分区还是扩展分区。对于大多数情况，你应该选择创建主分区，所以按p。
   #然后，它会询问你分区的编号。如果这是磁盘上的第一个分区，那么应该输入1。
   #接下来，它会询问分区的第一个和最后一个扇区。你可以接受默认值来创建一个使用所有可用空间的分区。（+10G创建10G大小的分区）
   #最后，按w来写入分区信息并退出。
   #创建文件系统
   mkfs.ext4 /dev/sda1
   #挂载一个分区实际上就是让操作系统识别该分区的文件系统，从而可以在该分区上读写文件。如果一个分区没有文件系统，那么操作系统就无法识别和使用它。因此，通常在挂载一个分区之前，你需要先对其进行格式化，创建一个文件系统。在Linux中，常见的文件系统类型有ext4、ext3、xfs等。

   #给磁盘打一个标签
   e2label /dev/sda1 volume_zen
   #lsblk -f 查看标签
   ~~~

3. Mount this partition

   ~~~sh
   mkdir /mnt/datadisk1
   mount LABEL=volume_zen /mnt/datadisk1/ #通过分区的标签挂载目录
   ~~~

4. Extend this partition by 1GB

   - 思路是删除旧分区，重新创建更大的新分区

   ~~~sh
   fdisk /dev/sda
   p #查看磁盘分区情况，记住需要扩容的磁盘的起始sector号
   d #删除之前的分区
   n #建立新分区
   p #主分区
   1 #第一个分区
   2048 #起始扇区号 （这是数据不丢失的关键）
   +11G #输入新的分区大小
   #如果有提示是否删除原来的filesystem signature，选择不需要
   w #保存退出
   ~~~

   ~~~sh
   e2fsck -f /dev/sda1 #检查修复文件系统错误
   resize2fs /dev/sda1 #扩容文件系统，让文件系统识别这些新的空间。
   ~~~

   > [!tip] Device busy处理
   > umount之后，执行fdisk/e2fsck/resize2fs的时候仍会有提示device busy，可以用`fuser -um`或者`lsof`查看使用分区的进程，可以用`fuser -km`杀掉占用的进程。然后再去执行resize2fs等操作。

## 文件系统与 NFS

- Create a mount for a directory / volume_zen and export it

  ~~~sh
  mount LABEL=volume_zen /mnt/datadisk1
  #安装nfs
  apt install -y nfs-kernel-server
  #配置nfs共享
  vim /etc/exports
  /mnt/datadisk1 *(rw,no_root_squash)
  #rw 该主机对该共享目录有读写权限
  # no_root_squash 登入 NFS 主机使用分享目录的使用者，如果是 root 的话，那么对于这个分享的目录来说，他就具有 root 的权限。根用户在 NFS 客户端上拥有和服务器上相同的权限。
  #使NFS配置生效
  exportfs -arv
  service nfs-kernel-server restart
  systemctl enable nfs-kernel-server && systemctl status nfs-kernel-server
  ~~~

  > [!warning] NFS no_root_squash安全提示
  > Ubuntu中配置NFS教程参考：[Ubuntu最新版本(Ubuntu22.04LTS)安装nfs服务器及使用教程_ubuntu22.04 nfs-CSDN博客](https://blog.csdn.net/wkd_007/article/details/129092820)
  >
  > - no_root_squash的含义：
  >
  >   - 默认情况下，NFS使用`root_squash`选项，这意味着来自客户端的root用户的请求将被NFS服务器视为来自匿名（或”nobody”）用户。这是一种安全措施，以防止远程root用户在NFS共享上拥有完全的root权限。
  >
  >   - 然而，如果你设置了`no_root_squash`选项，那么远程root用户的请求将被视为本地root用户。这意味着远程root用户将在NFS共享上拥有完全的root权限，就像在本地系统上一样。

- Configure Sticky bit on this folder

  ~~~sh
  chmod +t /mnt/datadisk1
  ls -ld /mnt/datadisk1
  ~~~

  > [!info] 特殊标志位
  > 特殊标志位分为三种：
  >
  > - sticky
  >   - 只有文件的所有者、目录的所有者或root用户才能删除或重命名该目录中的文件。某个普通用户不能删除/改名/移动所有者不是自己的文件。
  >   - drwxrwxrwt；置于o的x位置 1777
  > - SUID
  >   - **只对有x权限的文件有效。**如果一个程序的所有者是root并且具有SUID属性；那么普通用户执行，如同是root在执行。
  >   - -rwsr-xr-x；置于u的x位置，s表示SUID位被设置。也可以用 4755 表示
  > - SGID
  >   - 一般应用在目录上，目录设置sgid，任何用户在其中创建的文件的属组都会继承该目录的属组，而不是用户的属组。
  >   - drwxrwsr-x; 置于g的x位置，s表示SGID位被设置，也可以用 2775 表示

## 网络管理

Ubuntu 20.04 静态 IP 配置参考：[教程](https://cloud.tencent.com/developer/article/1933335)。

- Add a new interface and assign IP, gateway, DNS servers.

  ~~~yaml
  vim /etc/netplan/01-netcfg.yaml

  network:
    version: 2
    renderer: networkd
    ethernets:
      enp0s3:
        dhcp4: no
        addresses: [192.168.1.100/24]
        gateway4: 192.168.1.1
        nameservers:
          addresses: [8.8.8.8,8.8.4.4]

  netplan apply

  #也可以用nmcli来改
  nmcli con show --active #查看当前的网络连接，其中的name就是网络连接名
  sudo nmcli con mod <网络连接名> ipv4.addresses "192.168.1.100/24"
  sudo nmcli con mod <网络连接名> ipv4.gateway "192.168.1.1"
  sudo nmcli con mod <网络连接名> ipv4.method manual #手动指定IP，而非dhcp获取IP
  #重启网络以应用更改
  sudo nmcli con down <网络连接名> && sudo nmcli con up <网络连接名>
  ~~~

- Test Connectivity

  ~~~sh
  nc -vz <NIC IP> <port>
  ~~~

- Nslookup, A record CNAME

  ~~~sh

  ~~~

  > [!info] DNS记录类型
  > **A记录**：A记录是将域名映射到对应的IPv4地址。例如，如果你有一个服务器的IP地址是`192.0.2.1`，并且你希望`www.example.com`指向这个IP地址，你可以设置一个A记录，将`www.example.com`映射到`192.0.2.1`。
  >
  > **CNAME**：CNAME记录（Canonical Name record）是将一个域名映射到另一个域名。它允许你将多个域名解析到同一个IP地址。例如，你可能有一个主域名`www.example.com`，并且你希望`blog.example.com`和`store.example.com`都指向同一个地方。在这种情况下，你可以为`blog`和`store`设置CNAME记录，将它们都映射到`www.example.com`。

- Configure nameserver to google DNS

  ~~~sh
  vim /etc/resolv.conf #修改nameserver

  #也可以用nmcli修改
  nmcli con show --active #查看当前的网络连接，其中的name就是网络连接名
  nmcli con mod <网络连接名> ipv4.dns "8.8.8.8" #google dns是8.8.8.8,8.8.4.4
  sudo nmcli con down <网络连接名> && sudo nmcli con up <网络连接名>

  #查看dns
  systemd-resolve --status #显示系统的DNS解析器状态，包括每个网络接口的DNS服务器。你可以在"DNS Servers"或"DNSSEC NTA"部分找到当前使用的DNS服务器地址。
  ~~~

- Check all open/listen port on local server

  ~~~sh
  ss -tulnp
  ~~~

---

## 启动内核与 GRUB

### 查看已安装内核

```sh
dpkg --list | grep linux-image
```

原记录中的 Ubuntu 22.04 示例输出：

```text
ii  linux-image-5.15.0-102-generic          5.15.0-102.112                          amd64        Signed kernel image generic
ii  linux-image-5.15.0-78-generic           5.15.0-78.85                            amd64        Signed kernel image generic
ii  linux-image-5.15.0-88-generic           5.15.0-88.98                            amd64        Signed kernel image generic
ii  linux-image-generic                     5.15.0.102.99                           amd64        Generic Linux kernel image
```

### 查看启动菜单

```sh
grep -E '^[[:space:]]*(menuentry|submenu) ' /boot/grub/grub.cfg
```

原记录中的菜单节选：

```text
menuentry 'Ubuntu' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-simple-685552fd-4f93-41d4-9337-29b88e63493a' {
submenu 'Advanced options for Ubuntu' $menuentry_id_option 'gnulinux-advanced-685552fd-4f93-41d4-9337-29b88e63493a' {
        menuentry 'Ubuntu, with Linux 5.15.0-102-generic' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-102-generic-advanced-685552fd-4f93-41d4-9337-29b88e63493a' {
        menuentry 'Ubuntu, with Linux 5.15.0-102-generic (recovery mode)' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-102-generic-recovery-685552fd-4f93-41d4-9337-29b88e63493a' {
        menuentry 'Ubuntu, with Linux 5.15.0-88-generic' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-88-generic-advanced-685552fd-4f93-41d4-9337-29b88e63493a' {
        menuentry 'Ubuntu, with Linux 5.15.0-88-generic (recovery mode)' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-88-generic-recovery-685552fd-4f93-41d4-9337-29b88e63493a' {
        menuentry 'Ubuntu, with Linux 5.15.0-78-generic' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-78-generic-advanced-685552fd-4f93-41d4-9337-29b88e63493a' {
        menuentry 'Ubuntu, with Linux 5.15.0-78-generic (recovery mode)' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-78-generic-recovery-685552fd-4f93-41d4-9337-29b88e63493a' {
```

### 指定默认启动项

以下示例使用 `5.15.0-88-generic`。先核对本机实际菜单项，再编辑 `/etc/default/grub`：

```sh
sudo vim /etc/default/grub
```

将原来的 `GRUB_DEFAULT=0` 改为：

```sh
GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux 5.15.0-88-generic"
```

```sh
sudo update-grub
```

菜单标题会随内核版本、语言和配置变化；重启后用 `uname -r` 确认实际运行的内核。GRUB 也支持用菜单项 ID 指定默认项，ID 比标题更不容易受显示文字变化影响。

### 可选：暂缓内核包升级

`apt-mark hold` 可固定内核包；这会阻止相关内核更新，只有确实需要暂缓升级时才执行，并安排解除时间：

```sh
sudo apt-mark hold linux-headers-generic linux-image-generic linux-generic
apt-mark showhold
# 结束暂缓时：
sudo apt-mark unhold linux-headers-generic linux-image-generic linux-generic
```

选择旧内核启动本身不要求执行 `hold`。

## NVIDIA 显卡驱动

### 检查驱动与候选版本

```sh
nvidia-smi
ubuntu-drivers devices
```

`nvidia-smi` 失败表示当前驱动不可用或未正常工作，不能单凭该结果判断驱动包完全没有安装。`ubuntu-drivers devices` 中的 `recommended` 是候选推荐，安装前仍应核对 Ubuntu 版本、GPU 型号和用途。

### 安装驱动

Ubuntu 推荐使用 `ubuntu-drivers` 自动选择适配的驱动。桌面与通用用途：

```sh
sudo ubuntu-drivers install
```

服务器或计算任务可以查看并选择 `-server` 驱动：

```sh
sudo ubuntu-drivers list --gpgpu
sudo ubuntu-drivers install --gpgpu
```

固定版本的示例可在该包仍列于本机候选驱动、且明确需要 535 版本时使用：

```sh
sudo apt install -y nvidia-driver-535
```

`-open` 和 `-server` 是不同的驱动变体，不能一律排除；是否选择它们取决于硬件、用途和 Ubuntu 提供的候选包。

### 可选：处理 Nouveau 冲突

只有在 Nouveau 与目标 NVIDIA 驱动冲突、且安装流程未自动处理时，再禁用 Nouveau。以下两条配置应分行写入：

```sh
sudo vim /etc/modprobe.d/blacklist-nouveau.conf
```

```text
blacklist nouveau
options nouveau modeset=0
```

```sh
sudo update-initramfs -u
sudo reboot
```

重启后检查模块是否仍被加载：

```sh
lsmod | grep nouveau
```

无输出表示当前未加载 Nouveau 模块；如仍有驱动问题，再结合日志排查。

### 可选：应用依赖与库路径

以下是应用构建依赖，**不是安装 NVIDIA 驱动的必需步骤**：

```sh
sudo apt-get install libprotobuf-dev libleveldb-dev libsnappy-dev libopencv-dev libhdf5-serial-dev protobuf-compiler
sudo apt-get install --no-install-recommends libboost-all-dev
sudo apt-get install libopenblas-dev liblapack-dev libatlas-base-dev
sudo apt-get install libgflags-dev libgoogle-glog-dev liblmdb-dev
```

应用可通过共享库搜索路径查找依赖。仅在应用确实需要这些路径时，编辑当前用户的 `~/.bashrc`；两条 `export` 不应连在一起：

```sh
vim ~/.bashrc
```

```sh
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
```

```sh
source ~/.bashrc
```

### 验证

安装并按需重启后，再运行：

```sh
nvidia-smi
```

## 安全补丁管理

参考[安全更新说明](https://zhuanlan.zhihu.com/p/74768044#%E6%96%B9%E6%B3%95%E4%B8%80%EF%BC%9A%E5%A6%82%E4%BD%95%E6%A3%80%E6%9F%A5%20Debian/Ubuntu%20%E4%B8%AD%E6%98%AF%E5%90%A6%E6%9C%89%E4%BB%BB%E4%BD%95%E5%8F%AF%E7%94%A8%E7%9A%84%E5%AE%89%E5%85%A8%E6%9B%B4%E6%96%B0%EF%BC%9F)。

### 查看与手动安装

```sh
sudo unattended-upgrade --dry-run -v  # 预览可安装更新，不实际安装
sudo unattended-upgrade -d             # 安装并输出调试信息
sudo unattended-upgrade                # 直接安装
```

### 自动更新配置

- `/etc/apt/apt.conf.d/50unattended-upgrades`：允许的更新来源和自动更新行为。安全来源配置示例：

  ```text
  Unattended-Upgrade::Allowed-Origins {
      "${distro_id}:${distro_codename}-security";
      // ESM 来源只有在相应版本和服务可用时才会生效。
      "${distro_id}ESMApps:${distro_codename}-apps-security";
      "${distro_id}ESM:${distro_codename}-infra-security";
  };
  ```

  ESM Apps 提供应用包的扩展安全维护，ESM Infra 提供基础设施包的扩展安全维护。允许哪些来源取决于 Ubuntu 版本和本机配置；检查现有配置后再调整。Ubuntu 建议通过 `/etc/apt/apt.conf.d/` 中编号更靠后的独立配置文件覆盖设置，避免直接改发行版提供的 `50unattended-upgrades`。

- `/etc/apt/apt.conf.d/20auto-upgrades`：周期性刷新包列表与运行自动更新。每日配置示例：

  ```text
  APT::Periodic::Update-Package-Lists "1";
  APT::Periodic::Unattended-Upgrade "1";
  ```

  `1` 表示每天运行，`0` 表示关闭对应的周期任务。修改后用 `sudo unattended-upgrade --dry-run -v` 检查可安装更新；无须为了编辑配置而重启 `unattended-upgrades` 服务。

### 按周或按季度运行

如果改用 root 的 cron 定时安装，先关闭周期性自动安装，同时保留包列表刷新：

```sh
sudo vim /etc/apt/apt.conf.d/20auto-upgrades
```

```text
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "0";
```

然后编辑 root 的 crontab：

```sh
sudo crontab -e
```

以下两种计划**任选其一**：

1. 每周六 02:00：

   ```cron
   0 2 * * 6 unattended-upgrade
   ```

2. 每个季度最后一个月的最后一个周六 23:59（原 VM 计划）：

   ```cron
   59 23 * 3,6,9,12 6 [ "$(date +\%m -d +7days)" != "$(date +\%m)" ] && unattended-upgrade
   ```

   第二个表达式利用“七天后月份已变化”判断本周六为当月最后一个周六。`\%` 是 crontab 中必须保留的转义。`date -d` 是 GNU date 语法，适用于这里的 Ubuntu 环境。

保存 crontab 后用 `sudo crontab -l` 和 `systemctl status cron.service` 核对；通常不需要重启 cron。`sudo systemctl restart cron.service` 仅在服务异常时使用。

### 使用 APT 查看更新

```sh
sudo apt update
apt list --upgradable | grep -- '-security'
apt changelog packagename
```

`focal-security` 是 Ubuntu 20.04 LTS 的安全更新来源名称。用管道批量提取包名并调用 `apt install` 时，输出格式和来源匹配可能不完整；安装前应核对候选版本，再明确安装所需包。`apt install -s` 可预览安装计划。
