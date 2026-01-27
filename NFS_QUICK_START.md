# 🖧 NFS Quick Start - 5 Minute Setup

## What You Need

1. **NFS Server** (Synology, QNAP, Linux box, etc.)
   - Example: `192.168.1.100` with share `/data`

2. **Your Computer** (Windows or Linux)

3. **Network connection** between them

---

## Windows Quick Setup (Admin PowerShell)

```powershell
# Step 1: Enable NFS
Enable-WindowsOptionalFeature -FeatureName NFS-Client -Online

# Step 2: Mount the share (replace with your details)
mount -o anon \\192.168.1.100\data Z:

# Step 3: Verify it worked
dir Z:\
```

### 3 fields you need to find:
- **Server IP**: Ask your IT or check your NAS device → `192.168.1.100`
- **Share name**: Check NAS settings → `/data` or `/volume1/data`
- **Drive letter**: Pick any unused letter → `Z:`

---

## Linux Quick Setup (Terminal)

```bash
# Step 1: Install NFS utils (if needed)
sudo apt-get install nfs-common

# Step 2: Create mount point
sudo mkdir -p /mnt/nfs

# Step 3: Mount (replace with your details)
sudo mount -t nfs 192.168.1.100:/data /mnt/nfs

# Step 4: Verify it worked
ls -la /mnt/nfs
```

---

## Using with Scanner (Same for Both)

1. Go to http://localhost:8000
2. Click "🖧 NFS Share"
3. Fill in:
   ```
   NFS Mount Path: Z:\          (Windows) or /mnt/nfs (Linux)
   NFS Share Name: MyNAS        (any name)
   Scan Name: (optional)        (any name)
   ```
4. Click "Scan NFS Share"
5. Done! 📊

---

## Common Paths

| Device | Server IP | Share Path | Mount To |
|--------|-----------|-----------|----------|
| Synology | 192.168.1.50 | /volume1 | Z:\ |
| QNAP | 192.168.1.60 | /share | Z:\ |
| Linux | 192.168.1.200 | /home/data | /mnt/nfs |
| Windows Server | 192.168.1.100 | /exports | Z:\ |

**Don't know your details?**
- Check your NAS web interface (admin login)
- Ask your IT department
- Look in your network settings/File Explorer

---

## If It Doesn't Work

### "NFS not found on Windows"
→ Need Windows Pro/Enterprise (not Home)

### "Permission denied"
→ Check NAS has read permissions for your user

### "Connection refused"
→ Is NFS server turned on? Can you ping it?
```powershell
ping 192.168.1.100
```

### Path doesn't work
→ Try these variations:
```powershell
\\192.168.1.100\volume1\data  (add full path)
mount -o anon,sec=sys ...     (add security option)
```

---

**That's it! 🎉 You're ready to scan NFS!**
