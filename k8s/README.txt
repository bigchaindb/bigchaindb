===============================
!!!!!! BDB on KUBERNETES !!!!!!
===============================
Basic Kubernetes objects: Pod, Service, Volume, Namespace
Controllers are built using basic objects: ReplicaSet, Deployment, StatefulSet, DaemonSet, Job

----

Create an Azure Resource Group:
  az group create \
  --name bdb_res_grp \
  --location westeurope \
  --debug --output json


Create a managed k8s cluster:
  az acs create \
  --name bdb_acs_cluster \
  --resource-group bdb_res_grp \
  --admin-username azureuser \
  --agent-count 3 \
  --agent-vm-size Standard_D2_v2 \
  --dns-prefix bdbacs \
  --generate-ssh-keys \
  --location westeurope \
  --orchestrator-type kubernetes \
  --ssh-key-value ~/.ssh/id_rsa.pub \
  --debug \
  --output json


Install kubectl:
  curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
  chmod +x ./kubectl
  sudo mv ./kubectl /usr/local/bin/kubectl
  . <(kubectl completion bash) # auto-completion


Configure kubectl:
  az acs \
  kubernetes \
  get-credentials \
  --resource-group krish_res_grp \
  --name krish_acs_cluster


Delete managed k8s cluster:
  az acs delete \
  --name krish_acs_cluster \
  --resource-group krish_res_grp \
  --debug --output json


Manually attach unmanaged disks:
[
From:
https://docs.microsoft.com/en-us/azure/virtual-machines/virtual-machines-linux-add-disk?toc=%2fazure%2fvirtual-machines%2flinux%2ftoc.json
https://docs.microsoft.com/en-us/azure/virtual-machines/virtual-machines-linux-optimization?toc=%2fazure%2fvirtual-machines%2flinux%2ftoc.json
]


Create an Azure Disk:
  Attach a new/existing disk:
    New disk:
      az vm unmanaged-disk attach \
        --new \
        --name k8s-disk-2 \
        --resource-group krish_res_grp \
        --vm-name k8s-agent-2A4DB240-2 \
        --size-gb 32 \
        --debug --output json
    Existing disk:
      Find the disk id first:
        diskId=$(az disk show -g myResourceGroup -n myDataDisk --query 'id' -o tsv)
      Attach the disk:
        az vm disk attach -g myResourceGroup --vm-name myVM --disk $diskId
  Format/Mount the disk:
    dmesg | grep SCSI && lsblk
    sudo fdisk /dev/sdX => n => p => w
    sudo mkfs.ext4 /dev/sdX1
    sudo mkdir /disk
    sudo mount /dev/sdc1 /disk
  Optionally add it to /etc/fstab to persist mount across reboots
    Get UUID: sudo blkid
    Add to fstab: UUID=XXX...XXX /disk ext4 defaults,nofail 1 2
    Reboot and check if the disk is automounted to /disk
    Optional: Trim the fs to save costs: TODO manually
      sudo apt-get install util-linux
      sudo fstrim /datadrive
  Optionally enable swap:
    Modify the ResourceDisk.EnableSwap={N|Y} and ResourceDisk.SwapSizeMB={SizeInMB} params in /etc/waagent.conf and restart the waagent service: ?
    Verify using the `free -h`  command.
  Optionally change the IO scheduling algo in linux kernel. TODO from link

