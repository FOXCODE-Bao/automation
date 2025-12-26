# n8n Workflows Directory

## 📌 Purpose

This directory contains n8n workflow JSON files that should be imported into your n8n instance during deployment.

---

## 📂 Expected File

Place your exported n8n workflow here:

-   **`smart_city_workflow.json`** - Main Smart City automation workflow

---

## 🔧 How to Export Your Workflow

1. Open your n8n instance (usually at `http://localhost:5678`)
2. Go to your **Smart City Workflow**
3. Click the **"..."** menu in the top right
4. Select **"Export"**
5. Choose **"Export to File"**
6. Save the file as `smart_city_workflow.json` in this directory

---

## 🚀 For DevOps Team

### Importing the Workflow

1. Access your n8n instance on the VPS
2. Click **"+"** → **"Import from File"**
3. Select `smart_city_workflow.json` from this directory
4. Click **"Import"**

### ⚠️ Important Post-Import Steps

After importing, you MUST:

1. **Add Credentials** (not included in JSON for security):

    - Google Gemini PaLM API Key
    - Telegram Bot Token
    - TomTom API Key
    - Mailjet API Key & Secret

2. **Verify HTTP Request Nodes**:

    - All URLs should point to `http://backend:8000/api/...`
    - NOT `localhost` or external IPs

3. **Activate the Workflow**:

    - Toggle the switch at the top right to "Active"

4. **Update Backend .env**:
    - Copy webhook URLs from n8n
    - Add to `.env` as `N8N_TRAFFIC_WEBHOOK` and `N8N_REPORT_WEBHOOK`

---

## 📝 Workflow Components

The Smart City workflow typically includes:

-   **Webhook Triggers**: Receive data from Django backend
-   **AI Analysis**: Process data with Google Gemini
-   **Notifications**: Send alerts via Telegram
-   **Email**: Send newsletters via Mailjet
-   **External APIs**: TomTom for traffic data

---

## 🔗 References

-   Full deployment guide: See `README_FOR_DEVOPS.md`
-   n8n Documentation: https://docs.n8n.io/
