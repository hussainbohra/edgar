# daizika

## Github configuration
Follow these instructions to setup your environment

1. Create an Ec2 instance
2. Mounting a new volume, following the below steps
    ```
    ubuntu@ip-10-0-0-169:~$ lsblk
    NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
    xvda    202:0    0   30G  0 disk
    └─xvda1 202:1    0   30G  0 part /
    xvdb    202:16   0  500G  0 disk
    ubuntu@ip-10-0-0-169:~$ sudo file -s /dev/xvdb
    /dev/xvdb: data
    ubuntu@ip-10-0-0-169:~$ sudo mkfs -t ext4 /dev/xvdb
    mke2fs 1.42.13 (17-May-2015)
    Creating filesystem with 131072000 4k blocks and 32768000 inodes
    Filesystem UUID: dbd7674a-e183-4316-b111-ef92a90ce70c
    Superblock backups stored on blocks:
            32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208,
            4096000, 7962624, 11239424, 20480000, 23887872, 71663616, 78675968,
            102400000

    Allocating group tables: done
    Writing inode tables: done
    Creating journal (32768 blocks): done
    Writing superblocks and filesystem accounting information: done

    ubuntu@ip-10-0-0-169:~$ sudo file -s /dev/xvdb
    /dev/xvdb: Linux rev 1.0 ext4 filesystem data, UUID=dbd7674a-e183-4316-b111-ef92a90ce70c (extents) (large files) (huge files)
    ubuntu@ip-10-0-0-169:~$ sudo mount /dev/xvdb /development
    mount: mount point /development does not exist
    ubuntu@ip-10-0-0-169:~$ sudo mkdir /development
    ubuntu@ip-10-0-0-169:~$ sudo mount /dev/xvdb /development
    ubuntu@ip-10-0-0-169:~$ sudo chmod 777 /development
    ubuntu@ip-10-0-0-169:~$
    ```
3. Github configuration
   * Add the github public key to the `~/.ssh/authorized_keys` file
   * You can also copy the github private key to file `~/.ssh/github`
   * Fix the permissions `chmod 600 ~/.ssh/github`
   * Add the following to the `~/.ssh/config` file
      ```
      Host github.com
          User git
          IdentityFile ~/.ssh/github
      ```
   * Clone the repository
      ```
      cd /development/
       git clone git@github.com:daizika/edgar.git
      ```
4. Install docker from `/development/edgar/scripts/docker_setup.sh`
5. Build docker image using the following commands
    ```
    sudo chown -R 1000 /development/edgar
    sudo chmod -R 777 /development/edgar/
    cd /development/edgar/docker
    docker build -t daizika.com/tensorflow:1.0 .
    docker run -d -p 8888:8888 -u root -e GRANT_SUDO=yes -v /development/edgar:/development <image_id> start-notebook.sh
    export TS_CONTAINER=<CONTAINER_ID>
    ```
6. Connect to the jupyter notebook server `http://<DOCKER-IP>:8888/?token=<TOKEN_FROM_LOGS>`


