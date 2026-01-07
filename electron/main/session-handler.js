const { session } = require('electron');

function setupCSPBypass() {
  const filter = { urls: ['*://*/*'] };

  session.defaultSession.webRequest.onHeadersReceived(filter, (details, callback) => {
    const newHeaders = { ...details.responseHeaders };
    
    Object.keys(newHeaders).forEach((header) => {
      const lower = header.toLowerCase();
      if (lower === 'content-security-policy' || 
          lower === 'content-security-policy-report-only' || 
          lower === 'x-frame-options') {
        delete newHeaders[header];
      }
    });

    callback({ responseHeaders: newHeaders });
  });
}

module.exports = { setupCSPBypass };