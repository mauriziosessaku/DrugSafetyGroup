# Instructions for DSG Server Access and Setup


## 🔹 Remote Server Overview
The following setup applies to ALL projects within the Drug Safety Group (DSG) and is hosted on a dedicated Windows-based remote server, providing a stable and secure environment for data handling and model evaluation.

DSG Server Specifications:
- Public IPv4: 3.66.61.61
- Operating System: Windows Server 2022
- RAM: 16 GB
- Availability Zone: eu-central-1a
- Architecture: AMD64
- Network Speed: Up to 5 Gbps

You can access the server via Remote Desktop Connection (RDP) using the IP address provided. Mac users can access the server using the Microsoft App, available in the App Store. Upon successful login, you will arrive at a standard Windows desktop interface.


## 🔐Account Credentials
Please request your username and password directly from maurizio.sessa@sund.ku.dk prior to your first login.


## 📁 Project Directory and Folder Structure
Once logged in, navigate to the main project directory:
```bash
C:\Projects\
```
Inside the C:\Projects\directory, set up your project folder. Use only your designated folder for your work. Within your directory, you should use the following subfolder structure:

```bash
C:\Projects\YourProjectName\
├── data\       # Input data (e.g., FAERS/VAERS cases)
├── output\     # Generated results and model outputs
└── software\   # Scripts and tools for analysis and automation
```


## 🧩 Document Versioning
All scripts, tools, code etc. used in your project must be:
- Placed in the correct folder.
- Versioned explicitly using the following naming convention: **NAME_v.X.X_YYYYMMDD**.

This ensures reproducibility and simplifies tracking.


## 🌐 GitHub Repository
A related GitHub repository is required for version control of non-sensitive code.
- Ensure the repository visibility (public or private) aligns with your project’s requirements.
- Keep the repository well-organized and regularly synchronized with your local project folder on the DSG server.
- Share your repository link with maurizio.sessa@sund.ku.dk for review and traceability.

**NOTE:** Sensitive or personally identifiable information must not be uploaded to the server or GitHub repository unless explicitly approved.
