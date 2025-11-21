/**
 * WhatsApp Web Bridge Server
 *
 * This Node.js server provides an HTTP API to interact with WhatsApp Web
 * using the whatsapp-web.js library. It's designed to be called from Python.
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');
const qrcode = require('qrcode-terminal');

// Configuration
const PORT = process.env.BRIDGE_PORT || 3123;
const SESSION_PATH = process.env.WHATSAPP_SESSION_PATH || './whatsapp_session';

// Initialize Express app
const app = express();
app.use(express.json());

// WhatsApp client state
let client = null;
let qrCodeData = null;
let isAuthenticated = false;
let isReady = false;

// Initialize WhatsApp client
function initializeClient() {
    client = new Client({
        authStrategy: new LocalAuth({
            clientId: "whatsapp-agent",
            dataPath: SESSION_PATH
        }),
        puppeteer: {
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        }
    });

    // QR Code event
    client.on('qr', (qr) => {
        console.log('[WhatsApp] QR Code received');
        qrCodeData = qr;
        qrcode.generate(qr, { small: true });
    });

    // Authenticated event
    client.on('authenticated', () => {
        console.log('[WhatsApp] Authenticated successfully');
        isAuthenticated = true;
        qrCodeData = null;
    });

    // Ready event
    client.on('ready', () => {
        console.log('[WhatsApp] Client is ready');
        isReady = true;
    });

    // Authentication failure
    client.on('auth_failure', (msg) => {
        console.error('[WhatsApp] Authentication failure:', msg);
        isAuthenticated = false;
    });

    // Disconnected
    client.on('disconnected', (reason) => {
        console.log('[WhatsApp] Client disconnected:', reason);
        isReady = false;
        isAuthenticated = false;
    });

    // Initialize client
    client.initialize();
}

// API Routes

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        ready: isReady,
        authenticated: isAuthenticated
    });
});

// Get status
app.get('/status', (req, res) => {
    res.json({
        ready: isReady,
        authenticated: isAuthenticated,
        hasQR: qrCodeData !== null
    });
});

// Get QR code
app.get('/qr', (req, res) => {
    if (qrCodeData) {
        res.json({
            qr: qrCodeData,
            message: 'Scan this QR code with WhatsApp'
        });
    } else if (isAuthenticated) {
        res.json({
            qr: null,
            message: 'Already authenticated'
        });
    } else {
        res.json({
            qr: null,
            message: 'Waiting for QR code...'
        });
    }
});

// Send message
app.post('/send', async (req, res) => {
    try {
        if (!isReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp client not ready'
            });
        }

        const { to, message } = req.body;

        if (!to || !message) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: to, message'
            });
        }

        // Send message
        const result = await client.sendMessage(to, message);

        res.json({
            success: true,
            id: result.id.id,
            timestamp: result.timestamp,
            to: to
        });

    } catch (error) {
        console.error('[WhatsApp] Send error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Read messages
app.post('/messages', async (req, res) => {
    try {
        if (!isReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp client not ready'
            });
        }

        const { limit = 10, unreadOnly = false } = req.body;

        // Get all chats
        const chats = await client.getChats();

        // Collect messages from chats
        const allMessages = [];

        for (const chat of chats.slice(0, 20)) {  // Limit to first 20 chats
            try {
                const messages = await chat.fetchMessages({ limit: 5 });

                for (const msg of messages) {
                    if (unreadOnly && msg.fromMe) continue;

                    allMessages.push({
                        id: msg.id,
                        from: msg.from,
                        to: msg.to,
                        body: msg.body,
                        timestamp: msg.timestamp,
                        isGroupMsg: msg.isGroupMsg,
                        sender: msg.author || msg.from,
                        chatId: chat.id._serialized,
                        isRead: msg.fromMe || true  // Simplified
                    });

                    if (allMessages.length >= limit) break;
                }

                if (allMessages.length >= limit) break;

            } catch (err) {
                console.error('Error fetching messages from chat:', err);
            }
        }

        // Sort by timestamp descending
        allMessages.sort((a, b) => b.timestamp - a.timestamp);

        res.json({
            success: true,
            messages: allMessages.slice(0, limit)
        });

    } catch (error) {
        console.error('[WhatsApp] Read messages error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            messages: []
        });
    }
});

// Search messages
app.post('/search', async (req, res) => {
    try {
        if (!isReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp client not ready'
            });
        }

        const { query, limit = 20 } = req.body;

        if (!query) {
            return res.status(400).json({
                success: false,
                error: 'Missing required field: query'
            });
        }

        // Search in chats (simplified implementation)
        const chats = await client.getChats();
        const matchingMessages = [];

        for (const chat of chats.slice(0, 20)) {
            try {
                const messages = await chat.fetchMessages({ limit: 10 });

                for (const msg of messages) {
                    if (msg.body && msg.body.toLowerCase().includes(query.toLowerCase())) {
                        matchingMessages.push({
                            id: msg.id,
                            from: msg.from,
                            to: msg.to,
                            body: msg.body,
                            timestamp: msg.timestamp,
                            isGroupMsg: msg.isGroupMsg,
                            sender: msg.author || msg.from,
                            chatId: chat.id._serialized
                        });

                        if (matchingMessages.length >= limit) break;
                    }
                }

                if (matchingMessages.length >= limit) break;

            } catch (err) {
                console.error('Error searching chat:', err);
            }
        }

        res.json({
            success: true,
            messages: matchingMessages
        });

    } catch (error) {
        console.error('[WhatsApp] Search error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            messages: []
        });
    }
});

// Get chats
app.post('/chats', async (req, res) => {
    try {
        if (!isReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp client not ready'
            });
        }

        const { limit = 20 } = req.body;

        const chats = await client.getChats();

        const chatList = chats.slice(0, limit).map(chat => ({
            id: chat.id._serialized,
            name: chat.name,
            isGroup: chat.isGroup,
            unreadCount: chat.unreadCount,
            timestamp: chat.timestamp
        }));

        res.json({
            success: true,
            chats: chatList
        });

    } catch (error) {
        console.error('[WhatsApp] Get chats error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            chats: []
        });
    }
});

// Shutdown endpoint
app.post('/shutdown', (req, res) => {
    res.json({ success: true, message: 'Shutting down...' });
    setTimeout(() => {
        if (client) {
            client.destroy();
        }
        process.exit(0);
    }, 1000);
});

// Start server
const server = app.listen(PORT, () => {
    console.log(`[Bridge] WhatsApp bridge server running on port ${PORT}`);
    console.log(`[Bridge] Session path: ${SESSION_PATH}`);
    initializeClient();
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('[Bridge] SIGTERM received, shutting down...');
    if (client) {
        client.destroy();
    }
    server.close();
});

process.on('SIGINT', () => {
    console.log('[Bridge] SIGINT received, shutting down...');
    if (client) {
        client.destroy();
    }
    server.close();
    process.exit(0);
});
