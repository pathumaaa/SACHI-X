#!/bin/bash

# Install Node.js and npm
sudo apt update
sudo apt install -y nodejs npm

# Create uc-tool directory
mkdir -p /root/uc-tool
cd /root/uc-tool

# Create uc-tool.js
cat > uc-tool.js <<EOL
const express = require('express');
const axios = require('axios');
const app = express();
const port = 3001;

app.get('/:uuid', async (req, res) => {
    const { uuid } = req.params;
    if (!uuid) {
        return res.status(400).send('UUID is required');
    }
    try {
        const trafficResponse = await axios.get(\`http://localhost:54321/panel/api/inbounds/getClientTrafficsById/\${uuid}\`);
        const trafficData = trafficResponse.data;
        const inboundResponse = await axios.get(\`http://localhost:54321/panel/api/inbounds/get/\${uuid}\`);
        const inboundData = inboundResponse.data;
        res.send(\`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>UC Tool - Usage Check</title>
            </head>
            <body>
                <h1>Usage Details</h1>
                <p><strong>Upload:</strong> \${trafficData.upload} MB</p>
                <p><strong>Download:</strong> \${trafficData.download} MB</p>
                <p><strong>Expiration Date:</strong> \${inboundData.expiryDate}</p>
            </body>
            </html>
        \`);
    } catch (error) {
        res.status(500).send('Failed to fetch user data');
    }
});

app.listen(port, () => {
    console.log(\`UC Tool running on http://localhost:\${port}\`);
});
EOL

# Install dependencies
npm install express axios

# Install PM2 for process management
npm install -g pm2

# Start uc-tool with PM2
pm2 start uc-tool.js --name "uc-tool"

# Save PM2 process
pm2 save
pm2 startup

echo "UC Tool installed and running on http://<your-vps-ip>:3001/"
