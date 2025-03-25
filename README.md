# ULocation V2

A Telegram bot with an admin panel for location-based services and promotions.

## Project Structure

- **bot/** - Telegram bot implementation using Aiogram 3.x
- **admin/** - Admin panel using Starlette Admin
- **uploads/** - Directory for storing uploaded files

## Setup

### Prerequisites
- Python 3.10+
- MongoDB
- Docker and Docker Compose (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ulocation-v2.git
cd ulocation-v2
```

2. Set up environment variables:
```bash
cp bot/.env.example bot/.env
# Edit .env file with your configuration
```

3. Run with Docker:
```bash
docker-compose up -d
```

### Running the Admin Panel

The admin panel provides an interface to manage:
- Users
- Partners
- Promotions

To run the admin panel manually:
```bash
cd admin
pip install -r requirements.txt
python main.py
```

Access the admin at: http://localhost:8000/admin/

### Configuring Image Uploads

The system stores images in the `uploads/` directory. Ensure that:
1. The directory exists and has proper permissions
2. The static file serving is properly configured in the admin panel
3. The UPLOAD_DIR environment variable is set correctly

## Features

- User registration and subscription management
- Multilingual support (UZ, RU, EN)
- Location-based services
- Partner promotions with promo codes
- Referral system
