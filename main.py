from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.sales_agent import SalesAgent
from data.synthetic_customers import CUSTOMERS
from data.mock_services import MockProductService
from models import ChannelType
from orchestration import orchestrator
from demo_scenarios import demo_scenarios
import json
import asyncio
from typing import Dict, Any
import uuid
import random
from datetime import datetime

app = FastAPI(title="AI Sales Agent Demo", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Sales Agent
sales_agent = SalesAgent()
product_service = MockProductService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.customer_sessions: Dict[str, str] = {}  # websocket_id -> customer_id

    async def connect(self, websocket: WebSocket, customer_id: str):
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        self.customer_sessions[connection_id] = customer_id
        return connection_id

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.customer_sessions:
            del self.customer_sessions[connection_id]

    async def send_personal_message(self, message: str, connection_id: str):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get_demo_interface():
    """Serve the main demo interface"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Sales Agent Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }
        
        .demo-container {
            background: white;
            width: 100vw;
            height: 100vh;
            display: flex;
            overflow: hidden;
        }
        
        .sidebar {
            width: 300px;
            background: #f8f9fa;
            border-right: 1px solid #e9ecef;
            padding: 20px;
            overflow-y: auto;
        }
        
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding-bottom: 120px; /* Space for agent status panel */
        }
        
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #fff;
        }
        
        .chat-header {
            background: #4f46e5;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 18px;
            font-weight: 600;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.agent .message-content {
            background: white;
            border: 1px solid #e5e7eb;
            margin-right: 10px;
        }
        
        .message.user .message-content {
            background: #4f46e5;
            color: white;
            margin-left: 10px;
        }
        
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e5e7eb;
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #d1d5db;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        
        .chat-input button {
            padding: 12px 24px;
            background: #4f46e5;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }
        
        .chat-input button:hover {
            background: #4338ca;
        }
        
        .customer-card {
            background: white;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            border: 1px solid #e5e7eb;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .customer-card:hover {
            border-color: #4f46e5;
            box-shadow: 0 2px 8px rgba(79, 70, 229, 0.15);
        }
        
        .customer-card.active {
            border-color: #4f46e5;
            background: #f0f4ff;
        }
        
        .customer-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
        }
        
        .customer-info {
            flex: 1;
        }
        
        .customer-name {
            font-weight: 600;
            color: #1f2937;
            font-size: 14px;
            margin-bottom: 2px;
        }
        
        .customer-location {
            font-size: 12px;
            color: #6b7280;
        }
        
        .channel-selector {
            margin-bottom: 20px;
        }
        
        .channel-selector label {
            display: block;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }
        
        .channel-selector select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            background: white;
        }
        
        .demo-scenarios {
            margin-top: 20px;
        }
        
        .demo-scenarios h3 {
            font-size: 14px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 10px;
        }
        
        .scenario-button {
            width: 100%;
            padding: 10px;
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            margin-bottom: 8px;
            transition: all 0.2s;
        }
        
        .scenario-button:hover {
            background: #e5e7eb;
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online {
            background: #10b981;
        }
        
        .status-away {
            background: #f59e0b;
        }
        
        .typing-indicator {
            display: none;
            color: #6b7280;
            font-style: italic;
            font-size: 14px;
        }
        
        .product-suggestion {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .product-name {
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 5px;
        }
        
        .product-price {
            color: #4f46e5;
            font-weight: 600;
        }
        
        .product-price::before {
            content: "₹";
            font-size: 0.9em;
        }
        
        .product-reason {
            font-size: 12px;
            color: #6b7280;
            margin-top: 5px;
        }
        
        /* Platform-specific styling */
        .platform-indicator {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            margin-left: 10px;
        }
        
        .platform-web { background: #4f46e5; color: white; }
        .platform-mobile { background: #10b981; color: white; }
        .platform-whatsapp { background: #25d366; color: white; }
        .platform-telegram { background: #0088cc; color: white; }
        .platform-voice { background: #f59e0b; color: white; }
        .platform-store { background: #8b5cf6; color: white; }
        
        /* Enhanced channel selector */
        .channel-selector select {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
        }
        
        .channel-selector select option {
            background: white;
            color: #1f2937;
        }
        
        /* Platform integration buttons */
        .platform-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .platform-btn {
            padding: 8px 12px;
            border: 2px solid transparent;
            border-radius: 20px;
            background: white;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .platform-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .platform-btn.active {
            border-color: #4f46e5;
            background: #f0f4ff;
        }
        
        .platform-btn.web:hover { border-color: #4f46e5; }
        .platform-btn.mobile:hover { border-color: #10b981; }
        .platform-btn.whatsapp:hover { border-color: #25d366; }
        .platform-btn.telegram:hover { border-color: #0088cc; }
        .platform-btn.voice:hover { border-color: #f59e0b; }
        .platform-btn.store:hover { border-color: #8b5cf6; }
        
        /* Enhanced header with platform info */
        .chat-header {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
        }
        
        .chat-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #10b981, #3b82f6, #8b5cf6, #f59e0b);
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* Agent status with platform */
        .agent-status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .agent-status-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 12px;
            opacity: 0.9;
        }
        
        .agent-status-indicator .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .connected-agents {
            display: flex;
            gap: 8px;
            margin-top: 5px;
        }
        
        .agent-badge {
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        /* Enhanced customer cards */
        .customer-card {
            position: relative;
            overflow: hidden;
        }
        
        .customer-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .customer-card:hover::before,
        .customer-card.active::before {
            opacity: 1;
        }
        
        /* Tier badges */
        .tier-badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .tier-bronze { background: #cd7f32; color: white; }
        .tier-silver { background: #c0c0c0; color: white; }
        .tier-gold { background: #ffd700; color: #1f2937; }
        .tier-platinum { background: #e5e4e2; color: #1f2937; }
        
        /* Enhanced product suggestions */
        .product-suggestion {
            position: relative;
            overflow: hidden;
        }
        
        .product-suggestion::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .sidebar {
                width: 250px;
            }
            
            .platform-buttons {
                flex-direction: column;
            }
            
            .platform-btn {
                width: 100%;
                justify-content: center;
            }
        }
        
        /* Indian Features */
        .indian-features {
            margin-top: 20px;
            padding: 15px;
            background: linear-gradient(135deg, #ff6b6b, #ffa500);
            border-radius: 12px;
            color: white;
        }
        
        .feature-buttons {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .feature-btn {
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s;
            backdrop-filter: blur(10px);
        }
        
        .feature-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
        
        /* Indian-themed colors */
        .indian-orange { background: #ff6b6b; }
        .indian-green { background: #4ecdc4; }
        .indian-blue { background: #45b7d1; }
        .indian-purple { background: #96ceb4; }
        
        /* Enhanced animations and transitions */
        .message {
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .customer-card {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .customer-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.15);
        }
        
        .platform-btn {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .platform-btn:hover {
            transform: translateY(-2px) scale(1.05);
        }
        
        .platform-btn.active {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
        }
        
        /* Loading states */
        .loading {
            position: relative;
            overflow: hidden;
        }
        
        .loading::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        /* Enhanced product suggestions */
        .product-suggestion {
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .product-suggestion:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        /* Status indicators */
        .status-indicator {
            position: relative;
        }
        
        .status-indicator::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 12px;
            height: 12px;
            background: inherit;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            animation: statusPulse 2s infinite;
        }
        
        @keyframes statusPulse {
            0%, 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            50% { opacity: 0.7; transform: translate(-50%, -50%) scale(1.2); }
        }
        
        /* Agent Status Panel */
        .agent-status-panel {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #e5e7eb;
            padding: 16px 20px;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .agent-status-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .agent-status-header h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
        }
        
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }
        
        .agent-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        
        .agent-icon {
            font-size: 20px;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
        }
        
        .agent-details {
            flex: 1;
        }
        
        .agent-name {
            font-size: 13px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 2px;
        }
        
        .agent-status {
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .agent-status.connected {
            color: #10b981;
        }
        
        .agent-status.disconnected {
            color: #ef4444;
        }
    </style>
</head>
<body>
    <div class="demo-container">
        <div class="sidebar">
            <h2 style="margin-bottom: 20px; color: #1f2937; font-size: 18px;">Indian Customers</h2>
            
            <div id="customers-list">
                <!-- Customers will be loaded here -->
            </div>
        </div>
        
        <div class="main-content">
            <div class="chat-container">
                <div class="chat-header">
                    <div class="header-left">
                        <div class="agent-status-indicator">
                            <span class="status-dot"></span>
                            <span>AI Sales Agent</span>
                        </div>
                    </div>
                    <div class="header-right">
                        <span id="current-customer">Select a customer</span>
                    </div>
                </div>
                <div class="chat-messages" id="chat-messages">
                    <div class="message agent">
                        <div class="message-content">
                            Welcome! Please select a customer to start the demo.
                        </div>
                    </div>
                </div>
                <div class="typing-indicator" id="typing-indicator">
                    Agent is typing...
                </div>
                <div class="chat-input">
                    <input type="text" id="message-input" placeholder="Type your message..." disabled>
                    <button onclick="sendMessage()" disabled id="send-button">Send</button>
                </div>
            </div>
        </div>
        
        <!-- Agent Status Panel -->
        <div class="agent-status-panel">
            <div class="agent-status-header">
                <h3>Agent Status</h3>
                <div class="status-indicator">
                    <span class="status-dot"></span>
                    <span>All Systems Operational</span>
                </div>
            </div>
            <div class="agents-grid">
                <div class="agent-item">
                    <div class="agent-icon">🤖</div>
                    <div class="agent-details">
                        <div class="agent-name">Sales Agent</div>
                        <div class="agent-status connected">Connected</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-icon">🎯</div>
                    <div class="agent-details">
                        <div class="agent-name">Recommendation Agent</div>
                        <div class="agent-status connected">Connected</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-icon">📦</div>
                    <div class="agent-details">
                        <div class="agent-name">Inventory Agent</div>
                        <div class="agent-status connected">Connected</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-icon">💳</div>
                    <div class="agent-details">
                        <div class="agent-name">Payment Agent</div>
                        <div class="agent-status connected">Connected</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-icon">🚚</div>
                    <div class="agent-details">
                        <div class="agent-name">Fulfillment Agent</div>
                        <div class="agent-status connected">Connected</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-icon">⭐</div>
                    <div class="agent-details">
                        <div class="agent-name">Loyalty Agent</div>
                        <div class="agent-status connected">Connected</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-icon">🛠️</div>
                    <div class="agent-details">
                        <div class="agent-name">Post-Purchase Agent</div>
                        <div class="agent-status connected">Connected</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentCustomer = null;
        let currentSession = null;
        let websocket = null;
        let connectionId = null;

        // Load customers
        async function loadCustomers() {
            try {
                const response = await fetch('/api/customers');
                const customers = await response.json();
                
                const customersList = document.getElementById('customers-list');
                customersList.innerHTML = '';
                
                customers.forEach(customer => {
                    const customerCard = document.createElement('div');
                    customerCard.className = 'customer-card';
                    
                    // Get initials for avatar
                    const initials = customer.name.split(' ').map(n => n[0]).join('').toUpperCase();
                    
                    customerCard.innerHTML = `
                        <div class="customer-avatar">${initials}</div>
                        <div class="customer-info">
                            <div class="customer-name">${customer.name}</div>
                            <div class="customer-location">${customer.location}</div>
                        </div>
                    `;
                    customerCard.onclick = () => selectCustomer(customer);
                    customersList.appendChild(customerCard);
                });
            } catch (error) {
                console.error('Error loading customers:', error);
            }
        }

        // Clear chat messages
        function clearMessages() {
            const messagesContainer = document.getElementById('chat-messages');
            messagesContainer.innerHTML = '';
        }

        // Select customer
        async function selectCustomer(customer) {
            // Remove active class from all cards
            document.querySelectorAll('.customer-card').forEach(card => {
                card.classList.remove('active');
            });
            
            // Add active class to selected card
            event.target.closest('.customer-card').classList.add('active');
            
            currentCustomer = customer;
            document.getElementById('current-customer').textContent = customer.name;
            
            // Clear previous messages
            clearMessages();
            
            // Enable input
            document.getElementById('message-input').disabled = false;
            document.getElementById('send-button').disabled = false;
            
            // Connect to WebSocket
            await connectWebSocket();
            
            // Start conversation
            await startConversation();
        }

        // Connect to WebSocket
        async function connectWebSocket() {
            if (websocket) {
                websocket.close();
            }
            
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${currentCustomer.id}`;
            
            websocket = new WebSocket(wsUrl);
            
            websocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleAgentMessage(data);
            };
            
            websocket.onclose = function() {
                console.log('WebSocket connection closed');
            };
        }

        // Start conversation
        async function startConversation() {
            const channel = document.getElementById('channel').value;
            
            try {
                const response = await fetch('/api/start-conversation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        customer_id: currentCustomer.id,
                        channel: channel
                    })
                });
                
                const result = await response.json();
                currentSession = result.session_id;
                
                // Add agent message
                addMessage('agent', result.message);
                
                // Show suggested actions if available
                if (result.suggested_actions) {
                    showSuggestedActions(result.suggested_actions);
                }
            } catch (error) {
                console.error('Error starting conversation:', error);
            }
        }

        // Send message
        async function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            
            if (!message || !currentSession) return;
            
            // Add user message
            addMessage('user', message);
            input.value = '';
            
            // Show enhanced typing indicator with agent activity
            showTypingIndicator();
            showAgentActivity({agent: 'AI Sales Agent', action: 'analyzing your request'});
            
            // Simulate agent processing steps
            setTimeout(() => {
                showAgentActivity({agent: 'Recommendation Agent', action: 'finding products'});
            }, 500);
            
            setTimeout(() => {
                showAgentActivity({agent: 'Inventory Agent', action: 'checking availability'});
            }, 1000);
            
            try {
                const response = await fetch('/api/send-message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: currentSession,
                        message: message,
                        customer_id: currentCustomer.id,
                        channel: document.getElementById('channel').value
                    })
                });
                
                const result = await response.json();
                hideTypingIndicator();
                
                if (result.error) {
                    addMessage('agent', `Error: ${result.error}`);
                } else {
                    handleAgentResponse(result);
                }
            } catch (error) {
                hideTypingIndicator();
                addMessage('agent', 'Sorry, I encountered an error. Please try again.');
                console.error('Error sending message:', error);
            }
        }

        // Handle agent response
        function handleAgentResponse(result) {
            if (result.message) {
                addMessage('agent', result.message);
            }
            
            if (result.recommendations) {
                showRecommendations(result.recommendations);
            }
            
            if (result.suggested_actions) {
                showSuggestedActions(result.suggested_actions);
            }
            
            if (result.error) {
                addMessage('agent', `Error: ${result.error}`);
            }
            
            // Show agent activity indicators
            if (result.agent_activity) {
                showAgentActivity(result.agent_activity);
            }
        }

        // Handle agent message from WebSocket
        function handleAgentMessage(data) {
            if (data.type === 'message') {
                addMessage('agent', data.content);
            } else if (data.type === 'recommendations') {
                showRecommendations(data.recommendations);
            }
        }


        // Show recommendations
        function showRecommendations(recommendations) {
            const messagesContainer = document.getElementById('chat-messages');
            
            recommendations.forEach(rec => {
                const productDiv = document.createElement('div');
                productDiv.className = 'product-suggestion';
                productDiv.innerHTML = `
                    <div class="product-name">${rec.product.name}</div>
                    <div class="product-price">${formatIndianPrice(rec.product.price)}</div>
                    <div class="product-reason">${rec.reason}</div>
                    <div style="margin-top: 8px; display: flex; gap: 8px;">
                        <button onclick="addToCart('${rec.product.sku}')" style="padding: 4px 8px; background: #4f46e5; color: white; border: none; border-radius: 4px; font-size: 12px; cursor: pointer;">Add to Cart</button>
                        <button onclick="checkInventory('${rec.product.sku}')" style="padding: 4px 8px; background: #10b981; color: white; border: none; border-radius: 4px; font-size: 12px; cursor: pointer;">Check Stock</button>
                        <button onclick="getSimilarProducts('${rec.product.sku}')" style="padding: 4px 8px; background: #f59e0b; color: white; border: none; border-radius: 4px; font-size: 12px; cursor: pointer;">Similar</button>
                    </div>
                `;
                messagesContainer.appendChild(productDiv);
            });
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        // Product interaction functions
        function addToCart(sku) {
            if (currentSession) {
                document.getElementById('message-input').value = `Add ${sku} to cart`;
                sendMessage();
            }
        }
        
        function checkInventory(sku) {
            if (currentSession) {
                document.getElementById('message-input').value = `Check inventory for ${sku}`;
                sendMessage();
            }
        }
        
        function getSimilarProducts(sku) {
            if (currentSession) {
                document.getElementById('message-input').value = `Show me products similar to ${sku}`;
                sendMessage();
            }
        }
        
        // Format Indian price
        function formatIndianPrice(price) {
            return `₹${price.toLocaleString('en-IN')}`;
        }
        
        // Show agent activity
        function showAgentActivity(activity) {
            const messagesContainer = document.getElementById('chat-messages');
            const activityDiv = document.createElement('div');
            activityDiv.className = 'message agent activity-indicator';
            activityDiv.innerHTML = `
                <div class="message-content">
                    <div style="display: flex; align-items: center; gap: 8px; font-size: 12px; color: #6b7280;">
                        <span class="status-dot" style="width: 6px; height: 6px;"></span>
                        <span>${activity.agent} is ${activity.action}...</span>
                    </div>
                </div>
            `;
            messagesContainer.appendChild(activityDiv);
            
            // Remove after 2 seconds
            setTimeout(() => {
                if (activityDiv.parentNode) {
                    activityDiv.parentNode.removeChild(activityDiv);
                }
            }, 2000);
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        // Enhanced message handling with typing indicators
        function addMessage(sender, content, options = {}) {
            const messagesContainer = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            if (options.isTyping) {
                contentDiv.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="status-dot" style="width: 6px; height: 6px;"></span>
                        <span>${content}</span>
                    </div>
                `;
            } else {
                contentDiv.textContent = content;
            }
            
            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            // Show notification for agent messages
            if (sender === 'agent' && !options.isTyping) {
                showNotification('New message from assistant');
            }
        }

        // Show suggested actions
        function showSuggestedActions(actions) {
            const messagesContainer = document.getElementById('chat-messages');
            
            actions.forEach(action => {
                const button = document.createElement('button');
                button.className = 'scenario-button';
                button.textContent = action;
                button.style.margin = '5px';
                button.onclick = () => {
                    document.getElementById('message-input').value = action;
                    sendMessage();
                };
                messagesContainer.appendChild(button);
            });
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Show typing indicator
        function showTypingIndicator() {
            document.getElementById('typing-indicator').style.display = 'block';
        }

        // Hide typing indicator
        function hideTypingIndicator() {
            document.getElementById('typing-indicator').style.display = 'none';
        }

        // Run demo scenario
        async function runScenario(scenario) {
            if (!currentCustomer) {
                alert('Please select a customer first');
                return;
            }
            
            const scenarios = {
                'product_search': [
                    "I'm looking for a new smartphone",
                    "Show me OnePlus phones",
                    "What's the best phone under ₹50,000?"
                ],
                'channel_switch': [
                    "I want to continue this conversation on WhatsApp",
                    "Can I switch to mobile app?",
                    "Send me details on Telegram"
                ],
                'purchase_flow': [
                    "I want to buy this Samsung phone",
                    "Check if it's available in Mumbai",
                    "Process payment via UPI"
                ],
                'post_purchase': [
                    "I want to return this item",
                    "Track my order",
                    "I have a complaint about delivery"
                ],
                'indian_festivals': [
                    "Show me Diwali offers",
                    "What special deals do you have for Holi?",
                    "Any festival discounts available?"
                ],
                'indian_payments': [
                    "Can I pay via UPI?",
                    "Do you accept Paytm wallet?",
                    "Is COD available for this order?"
                ]
            };
            
            const messages = scenarios[scenario];
            if (messages) {
                for (let i = 0; i < messages.length; i++) {
                    setTimeout(() => {
                        document.getElementById('message-input').value = messages[i];
                        sendMessage();
                    }, i * 2000);
                }
            }
        }

        // Handle Enter key
        document.getElementById('message-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Simplified functionality for image-matching design
        
        // Show notification
        function showNotification(message) {
            // Create notification element if it doesn't exist
            let notification = document.getElementById('notification');
            if (!notification) {
                notification = document.createElement('div');
                notification.id = 'notification';
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #4f46e5;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 8px;
                    font-size: 14px;
                    z-index: 1000;
                    transform: translateX(100%);
                    transition: transform 0.3s ease;
                    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
                `;
                document.body.appendChild(notification);
            }
            
            notification.textContent = message;
            notification.style.transform = 'translateX(0)';
            
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
            }, 3000);
        }
        
        // Load customers on page load
        loadCustomers();
        
        // Initialize agent status monitoring
        initializeAgentStatusMonitoring();
        
        function initializeAgentStatusMonitoring() {
            // Check agent status every 30 seconds
            setInterval(checkAgentStatus, 30000);
            
            // Initial check
            checkAgentStatus();
        }
        
        // Check agent status
        async function checkAgentStatus() {
            try {
                const response = await fetch('/api/agents/status');
                const status = await response.json();
                
                // Update agent badges with status
                updateAgentBadges(status.agents);
                
                // Update system status indicator
                updateSystemStatus(status.system_status);
                
            } catch (error) {
                console.error('Error checking agent status:', error);
            }
        }
        
        // Update agent status in the panel
        function updateAgentBadges(agents) {
            const agentItems = document.querySelectorAll('.agent-item');
            const agentNames = ['Sales Agent', 'Recommendation Agent', 'Inventory Agent', 'Payment Agent', 'Fulfillment Agent', 'Loyalty Agent', 'Post-Purchase Agent'];
            
            agentNames.forEach((name, index) => {
                const agentItem = agentItems[index];
                if (agentItem) {
                    const agentKey = Object.keys(agents).find(key => 
                        key.includes(name.toLowerCase().replace(' ', '_').replace('-', '_'))
                    );
                    
                    const statusElement = agentItem.querySelector('.agent-status');
                    if (statusElement) {
                        if (agentKey && agents[agentKey].status === 'connected') {
                            statusElement.textContent = 'Connected';
                            statusElement.className = 'agent-status connected';
                        } else {
                            statusElement.textContent = 'Disconnected';
                            statusElement.className = 'agent-status disconnected';
                        }
                    }
                }
            });
        }
        
        // Update system status
        function updateSystemStatus(status) {
            const statusDot = document.querySelector('.agent-status-panel .status-dot');
            const statusText = document.querySelector('.agent-status-panel .status-indicator span:last-child');
            
            if (statusDot) {
                if (status === 'operational') {
                    statusDot.style.background = '#10b981';
                } else {
                    statusDot.style.background = '#ef4444';
                }
            }
            
            if (statusText) {
                statusText.textContent = status === 'operational' ? 'All Systems Operational' : 'System Issues Detected';
            }
        }
        
        // Initialize agent status monitoring
        initializeAgentStatusMonitoring();
    </script>
</body>
</html>
    """)

@app.get("/api/customers")
async def get_customers():
    """Get list of demo customers"""
    return [customer.model_dump() for customer in CUSTOMERS]

@app.post("/api/start-conversation")
async def start_conversation(request: Dict[str, Any]):
    """Start a new conversation with a customer"""
    customer_id = request.get("customer_id")
    channel = request.get("channel", "web")
    
    if not customer_id:
        raise HTTPException(status_code=400, detail="Customer ID required")
    
    try:
        result = await sales_agent.execute_task(customer_id, {
            "action": "start_conversation",
            "channel": channel
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send-message")
async def send_message(request: Dict[str, Any]):
    """Send a message in an existing conversation"""
    session_id = request.get("session_id")
    message = request.get("message")
    customer_id = request.get("customer_id")
    channel = request.get("channel", "web")
    
    if not all([session_id, message, customer_id]):
        raise HTTPException(status_code=400, detail="Session ID, message, and customer ID required")
    
    try:
        result = await sales_agent.execute_task(customer_id, {
            "action": "process_message",
            "session_id": session_id,
            "message": message,
            "channel": channel
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/switch-channel")
async def switch_channel(request: Dict[str, Any]):
    """Switch conversation to a different channel"""
    session_id = request.get("session_id")
    new_channel = request.get("new_channel")
    customer_id = request.get("customer_id")
    
    if not all([session_id, new_channel, customer_id]):
        raise HTTPException(status_code=400, detail="Session ID, new channel, and customer ID required")
    
    try:
        result = await sales_agent.execute_task(customer_id, {
            "action": "switch_channel",
            "session_id": session_id,
            "new_channel": new_channel
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{customer_id}")
async def websocket_endpoint(websocket: WebSocket, customer_id: str):
    """WebSocket endpoint for real-time communication"""
    connection_id = await manager.connect(websocket, customer_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message through sales agent
            if message_data.get("type") == "message":
                result = await sales_agent.execute_task(customer_id, {
                    "action": "process_message",
                    "session_id": message_data.get("session_id"),
                    "message": message_data.get("content"),
                    "channel": message_data.get("channel", "web")
                })
                
                # Send response back through WebSocket
                await manager.send_personal_message(
                    json.dumps({
                        "type": "message",
                        "content": result.get("message", ""),
                        "recommendations": result.get("recommendations"),
                        "suggested_actions": result.get("suggested_actions")
                    }),
                    connection_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id)

@app.get("/api/products")
async def get_products(category: str = None, limit: int = 20):
    """Get products from catalog"""
    if category:
        products = product_service.get_products(category=category, limit=limit)
    else:
        products = product_service.get_products(limit=limit)
    
    return [product.model_dump() for product in products]

@app.get("/api/products/search")
async def search_products(q: str):
    """Search products"""
    products = product_service.search_products(q)
    return [product.model_dump() for product in products]

@app.post("/api/run-scenario")
async def run_scenario(request: Dict[str, Any]):
    """Run a demo scenario"""
    scenario_name = request.get("scenario")
    customer_id = request.get("customer_id", "customer_001")
    
    if not scenario_name:
        raise HTTPException(status_code=400, detail="Scenario name required")
    
    try:
        result = await demo_scenarios.run_scenario(scenario_name, customer_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/run-all-scenarios")
async def run_all_scenarios():
    """Run all demo scenarios"""
    try:
        result = await demo_scenarios.run_all_scenarios()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute-workflow")
async def execute_workflow(request: Dict[str, Any]):
    """Execute a workflow orchestration"""
    workflow_type = request.get("workflow_type")
    customer_id = request.get("customer_id")
    initial_data = request.get("data", {})
    
    if not all([workflow_type, customer_id]):
        raise HTTPException(status_code=400, detail="Workflow type and customer ID required")
    
    try:
        result = await orchestrator.execute_workflow(workflow_type, customer_id, initial_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflow-status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get workflow status"""
    status = orchestrator.get_workflow_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status

@app.get("/api/active-workflows")
async def get_active_workflows():
    """Get all active workflows"""
    workflows = orchestrator.get_active_workflows()
    return {"workflows": workflows, "count": len(workflows)}

@app.get("/mobile")
async def get_mobile_interface():
    """Serve the mobile app interface"""
    with open("mobile_app.html", "r") as f:
        return HTMLResponse(content=f.read())

# Social Media Platform Integration Endpoints

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Dict[str, Any]):
    """Handle WhatsApp webhook messages"""
    try:
        message_data = request.get("messages", [{}])[0]
        customer_phone = message_data.get("from")
        message_text = message_data.get("text", {}).get("body", "")
        
        # Find customer by phone number
        customer = next((c for c in CUSTOMERS if c.phone == customer_phone), None)
        if not customer:
            return {"error": "Customer not found"}
        
        # Process message through sales agent
        result = await sales_agent.execute_task(customer.id, {
            "action": "process_message",
            "message": message_text,
            "channel": "whatsapp"
        })
        
        return {
            "success": True,
            "response": result.get("message", ""),
            "customer_id": customer.id
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Dict[str, Any]):
    """Handle Telegram webhook messages"""
    try:
        message_data = request.get("message", {})
        user_id = message_data.get("from", {}).get("id")
        message_text = message_data.get("text", "")
        
        # Find customer by Telegram user ID (mock)
        customer = next((c for c in CUSTOMERS if str(user_id) in c.preferences.get("telegram_id", "")), None)
        if not customer:
            return {"error": "Customer not found"}
        
        # Process message through sales agent
        result = await sales_agent.execute_task(customer.id, {
            "action": "process_message",
            "message": message_text,
            "channel": "telegram"
        })
        
        return {
            "success": True,
            "response": result.get("message", ""),
            "customer_id": customer.id
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/voice/process")
async def process_voice_command(request: Dict[str, Any]):
    """Process voice assistant commands"""
    try:
        customer_id = request.get("customer_id")
        voice_command = request.get("command", "")
        
        if not customer_id:
            return {"error": "Customer ID required"}
        
        # Process voice command through sales agent
        result = await sales_agent.execute_task(customer_id, {
            "action": "process_message",
            "message": voice_command,
            "channel": "voice_assistant"
        })
        
        return {
            "success": True,
            "response": result.get("message", ""),
            "recommendations": result.get("recommendations", []),
            "suggested_actions": result.get("suggested_actions", [])
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/store/kiosk")
async def store_kiosk_interaction(request: Dict[str, Any]):
    """Handle in-store kiosk interactions"""
    try:
        customer_id = request.get("customer_id")
        interaction_type = request.get("type", "greeting")
        data = request.get("data", {})
        
        if not customer_id:
            return {"error": "Customer ID required"}
        
        # Process kiosk interaction
        if interaction_type == "greeting":
            result = await sales_agent.execute_task(customer_id, {
                "action": "start_conversation",
                "channel": "in_store_kiosk"
            })
        else:
            result = await sales_agent.execute_task(customer_id, {
                "action": "process_message",
                "message": data.get("message", ""),
                "channel": "in_store_kiosk"
            })
        
        return {
            "success": True,
            "response": result.get("message", ""),
            "recommendations": result.get("recommendations", []),
            "suggested_actions": result.get("suggested_actions", [])
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/mobile/push")
async def send_mobile_push(request: Dict[str, Any]):
    """Send push notification to mobile app"""
    try:
        customer_id = request.get("customer_id")
        notification_type = request.get("type", "general")
        message = request.get("message", "")
        
        if not customer_id:
            return {"error": "Customer ID required"}
        
        # Mock push notification
        push_result = {
            "success": True,
            "notification_id": f"PUSH_{random.randint(100000, 999999)}",
            "delivered": True,
            "timestamp": datetime.now().isoformat()
        }
        
        return push_result
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    return {
        "agents": {
            "sales_agent": {
                "status": "connected",
                "last_activity": datetime.now().isoformat(),
                "active_sessions": len(sales_agent.active_sessions),
                "capabilities": ["conversation", "routing", "context_management"]
            },
            "recommendation_agent": {
                "status": "connected",
                "last_activity": datetime.now().isoformat(),
                "capabilities": ["product_recommendations", "personalization", "trending_analysis"]
            },
            "inventory_agent": {
                "status": "connected",
                "last_activity": datetime.now().isoformat(),
                "capabilities": ["stock_checking", "fulfillment_options", "reservation_management"]
            },
            "payment_agent": {
                "status": "connected",
                "last_activity": datetime.now().isoformat(),
                "capabilities": ["payment_processing", "upi_support", "cod_management"]
            },
            "fulfillment_agent": {
                "status": "connected",
                "last_activity": datetime.now().isoformat(),
                "capabilities": ["order_fulfillment", "shipping_coordination", "pickup_management"]
            },
            "loyalty_agent": {
                "status": "connected",
                "last_activity": datetime.now().isoformat(),
                "capabilities": ["points_management", "tier_benefits", "offer_generation"]
            },
            "post_purchase_agent": {
                "status": "connected",
                "last_activity": datetime.now().isoformat(),
                "capabilities": ["returns", "support", "feedback_collection"]
            }
        },
        "total_agents": 7,
        "connected_agents": 7,
        "system_status": "operational",
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
