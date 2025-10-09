# IT Analytics Platform - Complete Frontend Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup & Installation](#setup--installation)
4. [Project Structure](#project-structure)
5. [API Integration](#api-integration)
6. [Component Library](#component-library)
7. [State Management](#state-management)
8. [Styling & Theming](#styling--theming)
9. [Best Practices](#best-practices)
10. [Deployment](#deployment)

---

## Overview

The IT Analytics Platform frontend is a production-ready, Next.js 15 application that provides a comprehensive dashboard for monitoring IT project risks, resources, costs, and performance metrics. Built with modern technologies and following industry best practices.

### Key Highlights

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript for type safety
- **UI/UX**: Futuristic design with glassmorphism and smooth animations
- **State**: React Query for server state, Zustand for client state
- **Styling**: Tailwind CSS 4 with custom design system
- **Performance**: Code splitting, lazy loading, optimized rendering

---

## Architecture

### Design Patterns

1. **Component-Driven Architecture**
   - Reusable UI components in `/components/ui/`
   - Feature-specific components in `/components/[feature]/`
   - Layout components in `/components/layout/`

2. **Service Layer Pattern**
   - API client abstraction in `/services/api-client.ts`
   - Endpoint-specific services in `/services/api.ts`
   - Type-safe API calls with TypeScript

3. **State Management**
   - Server state with React Query (caching, refetching)
   - Client state with Zustand (theme, sidebar, filters)
   - No prop drilling with context/store patterns

4. **File-based Routing**
   - Next.js App Router for automatic routing
   - Dynamic routes for detail pages
   - Parallel routes for complex layouts

### Data Flow

```
User Action → Component → React Query/API Service → Backend API
                ↓
        State Update (Zustand/React Query Cache)
                ↓
        UI Re-render with New Data
```

---

## Setup & Installation

### Prerequisites

```bash
Node.js >= 20.0.0
npm >= 10.0.0
```

### Step-by-Step Installation

1. **Clone and Navigate**
```bash
cd /path/to/it-analytics-platform/frontend
```

2. **Install Dependencies**
```bash
npm install --legacy-peer-deps
```

3. **Environment Configuration**
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

4. **Start Development Server**
```bash
npm run dev
```

5. **Access Application**
```
http://localhost:3000
```

### Build for Production

```bash
npm run build
npm start
```

---

## Project Structure

```
frontend/
├── src/
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx                # Root layout with providers
│   │   ├── page.tsx                  # Home/Dashboard page
│   │   ├── providers.tsx             # React Query provider
│   │   └── globals.css               # Global styles & variables
│   │
│   ├── components/
│   │   ├── ui/                       # Reusable UI Components
│   │   │   ├── button.tsx           # Button with variants
│   │   │   ├── card.tsx             # Card with hover effects
│   │   │   └── badge.tsx            # Badge component
│   │   │
│   │   ├── layout/                   # Layout Components
│   │   │   ├── sidebar.tsx          # Collapsible sidebar
│   │   │   ├── header.tsx           # Top header with search
│   │   │   └── dashboard-layout.tsx # Main layout wrapper
│   │   │
│   │   └── dashboard/                # Dashboard Components
│   │       ├── dashboard-overview.tsx
│   │       ├── projects-table.tsx
│   │       ├── risk-chart.tsx
│   │       └── alerts-list.tsx
│   │
│   ├── services/                      # API Layer
│   │   ├── api-client.ts             # Axios client with interceptors
│   │   └── api.ts                    # API endpoint functions
│   │
│   ├── lib/                           # Utilities
│   │   ├── utils.ts                  # Helper functions
│   │   └── constants.ts              # API endpoints & query keys
│   │
│   ├── types/                         # TypeScript Definitions
│   │   └── index.ts                  # All type definitions
│   │
│   ├── hooks/                         # Custom React Hooks
│   │
│   └── store/                         # State Management
│       └── index.ts                  # Zustand stores
│
├── public/                            # Static Assets
├── tailwind.config.js                # Tailwind configuration
├── tsconfig.json                     # TypeScript config
├── next.config.ts                    # Next.js config
└── package.json                      # Dependencies
```

---

## API Integration

### API Client Setup

The API client is configured with:
- Base URL from environment variable
- Request/response interceptors
- Authentication token management
- Error handling
- TypeScript types

```typescript
// Usage example
import { projectsApi } from '@/services/api'

const projects = await projectsApi.getAll()
```

### Available API Functions

#### Projects API
```typescript
projectsApi.getAll()
projectsApi.getById(id)
projectsApi.uploadCsv(file, onProgress)
projectsApi.loadDefaultCsv()
projectsApi.generateSampleData(count)
```

#### Analytics API
```typescript
analyticsApi.getOverview()
analyticsApi.getRiskDashboard()
```

#### AI Insights API
```typescript
aiInsightsApi.getRiskAnalysis(projectId)
aiInsightsApi.getRecommendations(projectId)
aiInsightsApi.getPortfolioTrends()
aiInsightsApi.getExecutiveSummary()
```

### React Query Integration

```typescript
const { data, isLoading, error, refetch } = useQuery({
  queryKey: QUERY_KEYS.PROJECTS,
  queryFn: projectsApi.getAll,
  staleTime: 60000, // 1 minute
})
```

---

## Component Library

### UI Components

#### Button
```tsx
<Button variant="default" size="default">
  Click Me
</Button>

// Variants: default, destructive, outline, secondary, ghost, link, success, warning
// Sizes: default, sm, lg, icon
```

#### Card
```tsx
<Card hover glow>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content</CardContent>
  <CardFooter>Footer</CardFooter>
</Card>
```

#### Badge
```tsx
<Badge variant="success">Active</Badge>

// Variants: default, success, warning, danger, info, secondary
```

### Layout Components

#### Dashboard Layout
```tsx
<DashboardLayout>
  <YourContent />
</DashboardLayout>
```

#### Sidebar
- Collapsible/expandable
- Active route highlighting
- Icon-based navigation
- Persistent state

#### Header
- Search functionality
- Theme toggle
- Notifications
- User profile

---

## State Management

### React Query (Server State)

Handles all server data:
- Automatic caching
- Background refetching
- Loading/error states
- Optimistic updates

```typescript
// Query configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})
```

### Zustand (Client State)

Manages UI state:

```typescript
// Theme Store
const { theme, toggleTheme } = useThemeStore()

// Sidebar Store
const { isCollapsed, toggleCollapsed } = useSidebarStore()

// Filter Store
const { riskLevels, setRiskLevels } = useFilterStore()

// Notification Store
const { addNotification, notifications } = useNotificationStore()
```

---

## Styling & Theming

### Design System

#### Colors
```css
/* Primary Palette */
--primary: Purple (#a855f7)
--secondary: Slate (#1e293b)
--success: Green (#10b981)
--warning: Yellow (#f59e0b)
--danger: Red (#ef4444)
--info: Blue (#3b82f6)
```

#### Utility Classes
```css
.glass          /* Glassmorphism effect */
.glass-hover    /* Glass with hover state */
.glow           /* Purple glow effect */
.gradient-text  /* Gradient text effect */
.gradient-bg    /* Gradient background */
```

### Tailwind Configuration

Custom animations:
- `fade-in`
- `slide-in-right/left/up`
- `pulse-glow`
- `shimmer`

### Dark/Light Mode

Implemented with Zustand store and CSS variables:
```typescript
const { theme, toggleTheme } = useThemeStore()
```

---

## Best Practices

### Code Organization

1. **One Component Per File**
2. **Co-locate Related Files**
3. **Use TypeScript Strictly**
4. **Follow Naming Conventions**

### Performance

1. **Code Splitting**: Automatic with Next.js
2. **Lazy Loading**: Use `dynamic()` for heavy components
3. **Memoization**: Use `React.memo()` for expensive renders
4. **Image Optimization**: Use Next.js `<Image>` component

### Accessibility

1. **Semantic HTML**
2. **ARIA Labels**
3. **Keyboard Navigation**
4. **Focus Management**
5. **Color Contrast**: WCAG AA compliant

### Error Handling

```typescript
try {
  const data = await api.getData()
} catch (error) {
  toast.error('Failed to load data')
  console.error(error)
}
```

---

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Environment Variables

Production `.env`:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NODE_ENV=production
```

---

## Troubleshooting

### Common Issues

#### 1. Module Not Found
```bash
rm -rf .next node_modules
npm install --legacy-peer-deps
```

#### 2. Port Already in Use
```bash
lsof -ti:3000 | xargs kill -9
```

#### 3. API Connection Failed
- Check backend is running
- Verify CORS settings
- Check environment variables

#### 4. Build Errors
```bash
npm run lint
npm run build
```

---

## Performance Metrics

Target metrics:
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3.5s
- **Lighthouse Score**: > 90
- **Bundle Size**: < 500KB

---

## Contributing

1. Create feature branch
2. Follow coding standards
3. Write tests
4. Submit PR with description

---

## Support

For issues and questions:
- Check documentation
- Review backend API logs
- Contact development team

---

**Last Updated**: October 2025
**Version**: 1.0.0
