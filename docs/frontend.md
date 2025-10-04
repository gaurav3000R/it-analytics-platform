# Frontend Documentation

## 📋 Overview

The frontend is built with **Next.js 15** and **React 19**, providing a modern, fast, and SEO-friendly web application. It uses **Tailwind CSS v4** for styling and **TypeScript** for type safety.

## 🏗️ Architecture

```
frontend/
├── src/
│   └── app/              # Next.js App Router
│       ├── layout.tsx    # Root layout
│       ├── page.tsx      # Home page
│       ├── globals.css   # Global styles
│       └── favicon.ico   # Favicon
├── public/               # Static assets
├── node_modules/         # Dependencies
├── .next/                # Build output (auto-generated)
├── eslint.config.mjs     # ESLint configuration
├── next.config.ts        # Next.js configuration
├── tsconfig.json         # TypeScript configuration
├── postcss.config.mjs    # PostCSS configuration
├── package.json          # Dependencies and scripts
└── README.md             # Frontend-specific docs
```

## 🔧 Technology Stack

- **Framework**: Next.js 15 (App Router)
- **UI Library**: React 19
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS v4
- **Build Tool**: Turbo (via Turborepo)
- **Linting**: ESLint with Next.js config
- **Package Manager**: npm

## 🚀 Getting Started

### Installation

From the frontend directory:

```bash
# Install dependencies
npm install
```

### Running the Development Server

```bash
# Start development server
npm run dev

# Open in browser
# Navigate to http://localhost:3000
```

### Building for Production

```bash
# Create production build
npm run build

# Start production server
npm run start
```

### Linting

```bash
# Run ESLint
npm run lint
```

## 📁 Project Structure

### Current Structure

```
src/app/
├── layout.tsx      # Root layout with metadata
├── page.tsx        # Home page (main entry)
├── globals.css     # Global CSS and Tailwind directives
└── favicon.ico     # App icon
```

### Recommended Structure (for scaling)

```
src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Auth route group
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/         # Dashboard page
│   ├── tasks/             # Tasks pages
│   ├── analytics/         # Analytics pages
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # Reusable components
│   ├── ui/               # Basic UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Input.tsx
│   ├── layout/           # Layout components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── Sidebar.tsx
│   └── features/         # Feature-specific components
│       ├── TaskList.tsx
│       └── UserCard.tsx
├── lib/                  # Utility functions
│   ├── api.ts           # API client
│   ├── utils.ts         # Helper functions
│   └── constants.ts     # Constants
├── hooks/                # Custom React hooks
│   ├── useAuth.ts
│   ├── useTasks.ts
│   └── useAnalytics.ts
├── types/                # TypeScript type definitions
│   ├── user.ts
│   ├── task.ts
│   └── analytics.ts
└── styles/               # Additional styles
    └── globals.css
```

## 🎨 Styling with Tailwind CSS

### Configuration

Tailwind CSS v4 is configured in the project. The configuration is in `postcss.config.mjs`:

```javascript
export default {
  plugins: {
    '@tailwindcss/postcss': {}
  }
}
```

### Using Tailwind

```typescript
// Example component with Tailwind
export function Button({ children }: { children: React.ReactNode }) {
  return (
    <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
      {children}
    </button>
  );
}
```

### Global Styles

Located in `src/app/globals.css`:

```css
@import "tailwindcss";
```

## 🔄 Data Fetching

### Server Components (Recommended)

```typescript
// app/tasks/page.tsx
async function getTasks() {
  const res = await fetch('http://localhost:8000/api/tasks', {
    cache: 'no-store' // or 'force-cache' for static
  });
  return res.json();
}

export default async function TasksPage() {
  const tasks = await getTasks();
  
  return (
    <div>
      {tasks.map(task => (
        <div key={task.id}>{task.title}</div>
      ))}
    </div>
  );
}
```

### Client Components

```typescript
'use client';

import { useEffect, useState } from 'react';

export default function TaskList() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/tasks')
      .then(res => res.json())
      .then(data => setTasks(data));
  }, []);

  return (
    <div>
      {tasks.map(task => (
        <div key={task.id}>{task.title}</div>
      ))}
    </div>
  );
}
```

### API Client (Recommended Pattern)

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.statusText}`);
  }

  return res.json();
}

// Usage
export const getTasks = () => fetchAPI('/api/tasks');
export const getTaskById = (id: string) => fetchAPI(`/api/tasks/${id}`);
export const createTask = (data: TaskCreate) => 
  fetchAPI('/api/tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  });
```

## 🎯 Routing

### App Router (Next.js 15)

```
app/
├── page.tsx              # /
├── about/
│   └── page.tsx         # /about
├── tasks/
│   ├── page.tsx         # /tasks
│   └── [id]/
│       └── page.tsx     # /tasks/[id]
└── dashboard/
    ├── layout.tsx       # Dashboard layout
    └── page.tsx         # /dashboard
```

### Dynamic Routes

```typescript
// app/tasks/[id]/page.tsx
export default async function TaskPage({ 
  params 
}: { 
  params: { id: string } 
}) {
  const task = await getTaskById(params.id);
  
  return <div>{task.title}</div>;
}
```

### Route Groups

```
app/
├── (auth)/              # Grouped routes (not in URL)
│   ├── login/
│   └── register/
└── (main)/
    ├── dashboard/
    └── tasks/
```

## 🧩 Components

### Server Components (Default)

```typescript
// Async server component
export default async function UserList() {
  const users = await getUsers();
  
  return (
    <div>
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

### Client Components

```typescript
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

## 🔧 Configuration

### Next.js Config

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Add custom configuration here
};

export default nextConfig;
```

### TypeScript Config

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

## 🧪 Testing (To be implemented)

### Recommended Testing Stack

- **Unit Tests**: Jest + React Testing Library
- **E2E Tests**: Playwright or Cypress
- **Component Tests**: Storybook

### Example Test

```typescript
// __tests__/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
});
```

## 📱 Responsive Design

### Tailwind Breakpoints

```typescript
// Mobile-first responsive design
<div className="w-full md:w-1/2 lg:w-1/3">
  {/* Full width on mobile, half on tablet, third on desktop */}
</div>

// Common breakpoints:
// sm: 640px
// md: 768px
// lg: 1024px
// xl: 1280px
// 2xl: 1536px
```

## 🎨 UI Components (Planned)

### Button Component

```typescript
// components/ui/Button.tsx
import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md',
  ...props 
}: ButtonProps) {
  const baseStyles = 'rounded font-medium transition-colors';
  const variantStyles = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-500 text-white hover:bg-red-600',
  };
  const sizeStyles = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

## 🔐 Authentication (Planned)

### Auth Context

```typescript
// lib/auth.tsx
'use client';

import { createContext, useContext, useState } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    setUser(data.user);
    localStorage.setItem('token', data.token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```dockerfile
# Dockerfile
FROM node:18-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

## 📊 Performance Optimization

### Image Optimization

```typescript
import Image from 'next/image';

export function UserAvatar({ src }: { src: string }) {
  return (
    <Image
      src={src}
      alt="User avatar"
      width={50}
      height={50}
      className="rounded-full"
    />
  );
}
```

### Font Optimization

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.className}>
      <body>{children}</body>
    </html>
  );
}
```

## 🔗 Related Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

For more details, see the [Frontend README](../frontend/README.md).
