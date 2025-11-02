# AI-Driven Conversational Sales Agent

A comprehensive multi-agent system that revolutionizes retail sales experience by providing seamless, personalized customer interactions across online and physical channels.

## System Architecture

### Core Components
- **Sales Agent**: Main orchestrator managing multi-channel conversations
- **Worker Agents**: Specialized agents handling specific tasks
  - Recommendation Agent
  - Inventory Agent  
  - Payment Agent
  - Fulfillment Agent
  - Loyalty and Offers Agent
  - Post-Purchase Support Agent

### Features
- Multi-channel support (web, mobile, messaging, in-store)
- Real-time inventory management
- Personalized recommendations
- Seamless payment processing
- Cross-channel session continuity
- Post-purchase support

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the application:
```bash
python main.py
```

4. Access the demo interface at `http://localhost:8000`

## Demo Scenarios

The system includes several demo scenarios showcasing:
- Customer journey from mobile app to in-store
- Product recommendations and inventory checks
- Payment processing and fulfillment
- Cross-channel session continuity

## API Documentation

Available at `http://localhost:8000/docs` when running the application.
