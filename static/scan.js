document.addEventListener('DOMContentLoaded', () => {
    // Vulnerability Scan
    document.getElementById('vuln-scan-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const targetUrl = document.getElementById('target_url').value;
        const response = await fetch('/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ target_url: targetUrl })
        });
        const result = await response.json();
        document.getElementById('vuln-scan-result').textContent = result.result || result.error;
    });

    // Port Scan
    document.getElementById('port-scan-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const targetIp = document.getElementById('target_ip').value;
        const portRange = document.getElementById('port_range').value;
        const response = await fetch('/portscan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ target_ip: targetIp, port_range: portRange })
        });
        const result = await response.json();
        document.getElementById('port-scan-result').textContent = result.result || result.error;
    });

    // Web Application Testing
    document.getElementById('web-test-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const testUrl = document.getElementById('test_url').value;
        const testType = document.getElementById('test_type').value;
        const response = await fetch('/webtest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ test_url: testUrl, test_type: testType })
        });
        const result = await response.json();
        document.getElementById('web-test-result').textContent = result.result || result.error;
    });
});
