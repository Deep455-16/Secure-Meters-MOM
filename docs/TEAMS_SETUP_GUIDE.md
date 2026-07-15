# Microsoft Teams Integration Setup Guide

## 🎯 Overview
This guide walks you through enabling Microsoft Teams integration with the MOM Generator for real-time meeting MOM generation.

## 📋 Prerequisites
- Azure AD Tenant access
- Administrator privileges to register applications
- Client machine with the MOM Generator installed and running
- Python 3.8+

---

## 🔑 Step 1: Register Azure AD Application

### 1.1 Navigate to Azure Portal
- Go to https://portal.azure.com
- Sign in with your Azure AD account
- Navigate to **Azure Active Directory** → **App registrations**
- Click **+ New registration**

### 1.2 Configure Application
- **Name**: "MOM Generator Teams Integration"
- **Supported account types**: "Accounts in this organizational directory only"
- **Redirect URI**: Leave blank for now (not needed for confidential client flow)
- Click **Register**

### 1.3 Save Credentials
After registration, you'll see:
- **Application (client) ID** - Copy this
- **Directory (tenant) ID** - Copy this

Example:
```
Client ID:  12345678-1234-1234-1234-123456789012
Tenant ID:  87654321-4321-4321-4321-210987654321
```

---

## 🔐 Step 2: Create Client Secret

### 2.1 Add Secret
- In your registered app, go to **Certificates & secrets**
- Click **+ New client secret**
- **Description**: "MOM Generator Key"
- **Expires**: Choose appropriate duration (12 months recommended)
- Click **Add**

### 2.2 Copy Secret Value
⚠️ **Important**: Copy the secret value immediately. You won't be able to see it again!

Example:
```
Secret Value: x.Y~1234567890-_ABCDEFGHIJKLMNOPQRSTUVWxyz
```

---

## 📝 Step 3: Configure API Permissions

### 3.1 Add Required Permissions
- In your app, go to **API permissions**
- Click **+ Add a permission**
- Select **Microsoft Graph**
- Choose **Application permissions**

### 3.2 Add Each Permission
Search for and add these permissions:
- `OnlineMeetings.Read.All`
- `OnlineMeetings.ReadWrite.All`
- `Calendars.Read.All`
- `User.Read.All`
- `Group.Read.All`

### 3.3 Grant Admin Consent
- Click **Grant admin consent for [Organization]**
- Confirm when prompted

---

## ⚙️ Step 4: Configure MOM Generator

### 4.1 Update config.json
Open `config.json` and add the Teams credentials:

```json
{
  "whisper_exe": "main.exe",
  "whisper_model": "models/ggml-medium.bin",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "mistral:latest",
  "output_dir": ".",
  
  "teams_client_id": "12345678-1234-1234-1234-123456789012",
  "teams_client_secret": "x.Y~1234567890-_ABCDEFGHIJKLMNOPQRSTUVWxyz",
  "teams_tenant_id": "87654321-4321-4321-4321-210987654321",
  
  "api_host": "0.0.0.0",
  "api_port": 5000,
  "api_debug": false
}
```

### 4.2 Verify Configuration
- Ensure all three Teams fields are populated
- Do NOT commit these credentials to version control
- Consider using environment variables in production

---

## ✅ Step 5: Test the Integration

### 5.1 Start the Server
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start MOM Generator
python mom_api_server.py
```

### 5.2 Test Teams Status
```bash
curl http://localhost:5000/api/v1/teams/status
```

Expected response:
```json
{
  "status": "ok",
  "teams": {
    "teams_configured": true,
    "auth_ready": true,
    "features": {
      "call_recording": true,
      "participant_detection": true,
      "real_time_transcription": true,
      "automatic_mom_generation": true
    }
  },
  "timestamp": "2026-05-13T10:30:45.123456"
}
```

### 5.3 Connect to Teams
```bash
curl -X POST http://localhost:5000/api/v1/teams/connect \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "12345678-1234-1234-1234-123456789012",
    "client_secret": "x.Y~1234567890-_ABCDEFGHIJKLMNOPQRSTUVWxyz",
    "tenant_id": "87654321-4321-4321-4321-210987654321"
  }'
```

Expected response:
```json
{
  "status": "connected",
  "message": "Successfully connected to Microsoft Teams",
  "timestamp": "2026-05-13T10:30:45.123456"
}
```

---

## 🔍 Step 6: List Active Teams Calls

### 6.1 Get Active Calls
```bash
curl http://localhost:5000/api/v1/teams/list-calls
```

Expected response:
```json
{
  "status": "success",
  "calls": [
    {
      "id": "meeting-123",
      "organizer": "john@company.com",
      "subject": "Team Standup",
      "startTime": "2026-05-13T09:00:00Z",
      "participants": 5
    }
  ],
  "count": 1,
  "timestamp": "2026-05-13T10:30:45.123456"
}
```

---

## 📊 Step 7: Generate MOM from Teams Meeting

### 7.1 Get Meeting Details
From the previous call, get the meeting ID (e.g., `meeting-123`)

### 7.2 Get Participants
```bash
curl http://localhost:5000/api/v1/teams/participants/meeting-123
```

### 7.3 Generate MOM
```bash
curl -X POST http://localhost:5000/api/v1/teams/generate-mom/meeting-123 \
  -H "Content-Type: application/json" \
  -d '{"template": "standard"}'
```

Expected response:
```json
{
  "status": "success",
  "meeting_id": "meeting-123",
  "participants": [
    "John Smith",
    "Jane Doe",
    "Mike Johnson"
  ],
  "transcript": "John: Let's start the standup...",
  "mom": "**DATE:** May 13, 2026\n\n**PARTICIPANTS:**\n- John Smith\n...",
  "template": "standard",
  "timestamp": "2026-05-13T10:30:45.123456"
}
```

---

## 🐛 Troubleshooting

### Issue: "Teams not configured"
**Solution**: Verify all three fields are in `config.json`:
- `teams_client_id`
- `teams_client_secret`
- `teams_tenant_id`

### Issue: "Failed to authenticate with Teams API"
**Solution**: 
- Verify Client Secret hasn't expired
- Check credentials are correct (no extra spaces)
- Ensure API permissions are granted in Azure AD

### Issue: "No transcripts available"
**Solution**:
- Ensure Teams meeting transcription is enabled
- Wait a few moments after meeting ends for transcript processing
- Check Teams meeting has participants speaking

### Issue: "Permission denied" error
**Solution**:
- Verify admin consent was granted
- Check all required permissions are added:
  - OnlineMeetings.Read.All
  - OnlineMeetings.ReadWrite.All
  - Calendars.Read.All
  - User.Read.All

### Issue: Connection timeout
**Solution**:
- Verify Ollama is running
- Check network connectivity
- Ensure firewall isn't blocking port 5000

---

## 🔒 Security Best Practices

### 1. Protect Credentials
```bash
# DON'T do this:
export TEAMS_SECRET="your-secret-here"

# DO use environment variables:
# Create .env file (add to .gitignore):
TEAMS_CLIENT_ID=...
TEAMS_CLIENT_SECRET=...
TEAMS_TENANT_ID=...

# Load in code:
from dotenv import load_dotenv
load_dotenv()
client_id = os.getenv('TEAMS_CLIENT_ID')
```

### 2. Use Azure Key Vault (Production)
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
secret = client.get_secret("teams-client-secret")
```

### 3. Rotate Secrets Regularly
- Set expiration on client secrets (12 months max)
- Create new secret before old one expires
- Update configuration with new secret

### 4. Audit Access
- Monitor Teams activity logs
- Track MOM generation requests
- Review who has access to credentials

---

## 📈 Performance Considerations

### Optimization Tips:
1. **Cache tokens** between requests
2. **Batch process** multiple meetings
3. **Use appropriate template** (shorter templates = faster generation)
4. **Monitor token limits** (Teams API rate limits)

### Rate Limits:
- Standard: 1000 requests per minute
- Premium: Higher limits available
- Check response headers for usage

---

## 🔗 Additional Resources

- **Azure AD Documentation**: https://docs.microsoft.com/azure/active-directory/
- **Microsoft Graph API**: https://docs.microsoft.com/graph/
- **Teams API**: https://docs.microsoft.com/microsoftteams/platform/
- **Authentication Flow**: https://docs.microsoft.com/azure/active-directory/develop/

---

## 🆘 Support Contacts

For Teams API issues:
- **Microsoft Support**: https://support.microsoft.com
- **Azure Portal Support**: In Azure Portal → Help + Support
- **Documentation**: https://docs.microsoft.com

---

## ✅ Checklist

- [ ] Registered Azure AD application
- [ ] Copied Client ID and Tenant ID
- [ ] Created client secret
- [ ] Added API permissions
- [ ] Granted admin consent
- [ ] Updated config.json with credentials
- [ ] Tested /api/v1/teams/status endpoint
- [ ] Tested /api/v1/teams/connect endpoint
- [ ] Listed active Teams calls successfully
- [ ] Generated MOM from Teams meeting

---

**Version:** 1.0  
**Last Updated:** May 13, 2026  
**Status:** ✅ Ready for Production
