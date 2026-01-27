# 🖧 NFS (Network File System) Connector - Setup Guide

## What is NFS?

NFS is a protocol that lets you access files on remote servers over a network, as if they were on your local machine. The key difference from Azure is:
- **Azure**: Cloud storage (remote, requires credentials)
- **NFS**: Network-attached storage (local network, requires mounting)

The scanner works the same way for both - it just reads files and collects metadata.

---

## How the NFS Scanner Works

```
NFS Server (e.g., Linux, NAS device)
        ↓
    Network (TCP/IP)
        ↓
Your Computer (mounted via NFS)
        ↓
Scanner reads files locally
```

Once an NFS share is **mounted**, your computer treats it like a local folder. Our scanner just reads it like `C:\MyFolder`.

---

## Setup Steps

### **Step 1: Identify Your NFS Server**

You need:
- **Server IP/Hostname**: Example `192.168.1.100` or `nfs.company.com`
- **Share Path**: Example `/home/data` or `/exports/documents`
- **Access Permissions**: Read access to the share

### **Step 2: Mount NFS on Windows**

#### Option A: Using Windows File Explorer (Easiest)

1. **Enable NFS on Windows:**
   ```powershell
   # Run as Administrator
   Enable-WindowsOptionalFeature -FeatureName NFS-Client -Online
   ```

2. **Mount via Command Line:**
   ```powershell
   # Map network drive to NFS share
   mount -o anon \\192.168.1.100\data Z:
   
   # Replace:
   # 192.168.1.100 = Your NFS server IP
   # /data = NFS share path
   # Z: = Drive letter you want
   ```

3. **Verify Mount:**
   ```powershell
   # List mounted drives
   Get-Volume
   
   # Or explore in File Explorer - should see Z: drive
   ```

#### Option B: Using PowerShell Script

Create a file `mount-nfs.ps1`:
```powershell
# Mount NFS share
$serverIP = "192.168.1.100"
$nfsPath = "/data"
$driveLetter = "Z"

# Mount the share
mount -o anon \\$serverIP\$nfsPath ${driveLetter}:

Write-Host "NFS Share mounted to ${driveLetter}:\"
Write-Host "Path: \\$serverIP\$nfsPath"
```

Run it:
```powershell
powershell -ExecutionPolicy Bypass -File mount-nfs.ps1
```

### **Step 3: Mount NFS on Linux**

```bash
# Install NFS utilities (if not already installed)
sudo apt-get install nfs-common

# Create mount point
sudo mkdir -p /mnt/nfs

# Mount the NFS share
sudo mount -t nfs 192.168.1.100:/data /mnt/nfs

# Make it permanent (optional) - add to /etc/fstab:
# 192.168.1.100:/data /mnt/nfs nfs defaults 0 0

# Verify
ls -la /mnt/nfs
```

### **Step 4: Use Scanner with NFS**

1. **Open http://localhost:8000**

2. **Select "🖧 NFS Share"**

3. **Fill in the fields:**
   - **NFS Mount Path**: 
     - Windows: `Z:\` (after mounting to Z:)
     - Linux: `/mnt/nfs`
   - **NFS Share Name**: Any name you want (e.g., "DataServer", "CompanyNAS")
   - **Scan Name**: Optional (e.g., "Weekly Audit")

4. **Click "Scan NFS Share"**

---

## Real-World Examples

### **Example 1: Windows with NAS Device**

```
NAS Device (Synology, QNAP, etc.)
IP: 192.168.1.50
Share: /volume1/data
```

**Setup:**
```powershell
# As Administrator
Enable-WindowsOptionalFeature -FeatureName NFS-Client -Online

# Mount to N: drive
mount -o anon \\192.168.1.50\volume1\data N:
```

**In Scanner:**
- NFS Mount Path: `N:\`
- NFS Share Name: `Synology-Data`

---

### **Example 2: Linux with Linux Server**

```
Linux NFS Server (192.168.1.200)
Exported path: /home/shared
```

**Setup:**
```bash
# Mount NFS
sudo mount -t nfs 192.168.1.200:/home/shared /mnt/nfs

# Make permanent
echo "192.168.1.200:/home/shared /mnt/nfs nfs defaults 0 0" | sudo tee -a /etc/fstab
```

**In Scanner:**
- NFS Mount Path: `/mnt/nfs`
- NFS Share Name: `Linux-Server-Shared`

---

## How the Scanner Code Works

### **Scanner reads files recursively:**

```python
def scan_nfs_share(nfs_path, nfs_share_name):
    files = []
    
    # Walk through the mounted NFS folder
    for root, dirs, filenames in os.walk(nfs_path):
        for filename in filenames:
            # Get full file path
            file_path = os.path.join(root, filename)
            
            # Read file stats (size, date, etc.)
            stat = os.stat(file_path)
            
            # Store metadata
            files.append({
                'file_name': filename,
                'file_path': file_path,
                'file_size': stat.st_size,
                'last_modified': stat.st_mtime,
                # ... more metadata
            })
    
    return files
```

**Key Points:**
1. `os.walk()` - Recursively walks folders (same as local scanner)
2. `os.stat()` - Gets file metadata (size, timestamps)
3. `os.path.join()` - Builds full paths
4. Works exactly like local folder scanning!

---

## Troubleshooting

### Issue: "NFS path not found"
**Solution:**
- Verify NFS is mounted: `Get-Volume` (Windows) or `df -h` (Linux)
- Check the path is correct: `dir Z:\` or `ls /mnt/nfs`
- Ensure server is reachable: `ping 192.168.1.100`

### Issue: "Permission denied" when scanning
**Solution:**
- Check NFS share permissions on server
- Try mounting with different options:
  ```powershell
  mount -o anon,sec=sys \\192.168.1.100\data Z:
  ```
- Verify user has read access

### Issue: Slow scanning
**Causes:**
- Network latency (NFS over slow connection)
- Large number of files (millions)
- **Solution:** Patient waiting or optimize NFS server

### Issue: "Cannot enable NFS on Windows"
**Solution:**
- Windows Home edition doesn't support NFS
- Use WSL (Windows Subsystem for Linux) and mount there
- Or upgrade to Windows Pro/Enterprise

---

## Advanced: Understanding NFS Paths

### Windows NFS Path Examples:
```
\\192.168.1.100\data       → Computer IP + share path
\\nfs.company.com\exports  → Hostname + share path
Z:\                        → Mapped drive letter
```

### Linux NFS Path Examples:
```
/mnt/nfs           → Mount point
/mnt/servers/nfs1  → Custom location
/home/nfs          → Home directory
```

### Scanner accepts both:
```
Windows:
  \\192.168.1.100\data  → Direct UNC path
  Z:\                   → Mapped drive

Linux:
  /mnt/nfs              → Mount point
  /home/shared          → Any mounted location
```

---

## Comparing with Other Connectors

| Feature | Local | Azure | NFS |
|---------|-------|-------|-----|
| Setup | None | Connection string | Mount NFS |
| Access Type | Local disk | Cloud API | Network mount |
| Authentication | OS permissions | Azure credentials | NFS permissions |
| Speed | Fast | Depends on network | Depends on network |
| Use Case | Local files | Azure storage | Office NAS/servers |

---

## Complete Workflow Example

```bash
# 1. Check your NFS server is running
ping 192.168.1.100

# 2. Mount on Windows (as Admin)
mount -o anon \\192.168.1.100\data Z:

# 3. Verify mount
Get-Volume    # Should show Z: drive

# 4. Test access
dir Z:\       # Should list files

# 5. Start scanner
cd c:\uds\backend
python app.py

# 6. Open UI
# http://localhost:8000

# 7. Select "🖧 NFS Share"

# 8. Enter:
#    - NFS Mount Path: Z:\
#    - NFS Share Name: DataServer
#    - Scan Name: Initial Audit

# 9. Click "Scan NFS Share"

# 10. Results appear in dashboard
```

---

## Security Notes

⚠️ **Important:**
1. **NFS is unencrypted** - Don't use over untrusted networks
2. **Use VPN** - If accessing NFS remotely
3. **Check permissions** - Ensure proper access controls on NFS server
4. **Firewall** - NFS uses port 111 (portmapper) and 2049 (NFS)

For secure remote access:
```bash
# Use SSH tunnel to NFS server first
# Then mount through tunnel
```

---

## Summary

1. **Mount NFS** → Makes remote storage look like local folder
2. **Scanner reads** → Same way it reads local folders
3. **Collects metadata** → File names, sizes, dates, types
4. **Shows in dashboard** → Same interface as local/Azure

**That's it!** NFS is just another storage location the scanner can access. 🎉
