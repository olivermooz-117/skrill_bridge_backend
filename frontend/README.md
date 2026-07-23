React single-page application for the SkillBridge freelance marketplace platform.

## Features

- User authentication (login, register, logout)
- Browse and search gigs
- Create and manage gigs (freelancers only)
- Place and track orders (clients only)
- Leave reviews and ratings
- User profile management
- Password reset flow
- Protected routes
- Responsive design

## Tech Stack

- React 18.2.0
- React Router 6.20.0
- Vite 5.0.8
- Axios 1.6.0
- CSS3

## Pages and Routes

| Route | Page | Protected |
|-------|------|-----------|
| `/` | Landing / Browse Gigs | No |
| `/login` | Login | No |
| `/register` | Register | No |
| `/password-reset` | Password Reset Request | No |
| `/password-reset/confirm` | Password Reset Confirm | No |
| `/gigs/:id` | Gig Detail | No |
| `/dashboard` | Dashboard | Yes |
| `/profile` | Profile | Yes |
| `/orders` | My Orders | Yes |
| `/gigs/new` | Create Gig | Yes (Freelancer only) |
| `/gigs/:id/edit` | Edit Gig | Yes (Freelancer only) |

## Getting Started

### Prerequisites
- Node.js 16 or higher
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/olivermooz-117/skrill_bridge_frontend.git
cd skrill_bridge_frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your API URL

# Run development server
npm run dev