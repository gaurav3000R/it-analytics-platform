# Contributing to IT Analytics Platform

Thank you for your interest in contributing to the IT Analytics Platform! This document provides guidelines and instructions for contributing to this project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

---

## 🚀 Getting Started

### 1. Fork the Repository

Click the "Fork" button at the top right of the repository page.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/it-analytics-platform.git
cd it-analytics-platform
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/it-analytics-platform.git
```

### 4. Setup Development Environment

Follow the [Setup Guide](./SETUP.md) to configure your development environment.

---

## 🔄 Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/bug-description
```

### Branch Naming Conventions

- **Feature**: `feature/feature-name`
- **Bug Fix**: `fix/bug-description`
- **Documentation**: `docs/what-changed`
- **Performance**: `perf/improvement-description`
- **Refactor**: `refactor/what-changed`

### 2. Make Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add tests for new features
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
npm run test

# Frontend tests
cd frontend && npm run test

# Backend tests
cd backend && pytest

# Lint your code
npm run lint  # (when available)
```

### 4. Commit Your Changes

Follow the [Commit Guidelines](#commit-guidelines) below.

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

Go to the original repository and create a Pull Request from your fork.

---

## 📝 Coding Standards

### General Principles

- **Keep it simple**: Write simple, clear code
- **DRY**: Don't Repeat Yourself
- **SOLID**: Follow SOLID principles
- **Documentation**: Comment complex logic
- **Type Safety**: Use type hints (Python) and TypeScript

### Frontend (TypeScript/React)

#### Style Guide

- Use **functional components** with hooks
- Use **TypeScript** for all new files
- Follow **React best practices**
- Use **Tailwind CSS** for styling

#### Example

```typescript
// Good
interface UserProps {
  name: string;
  email: string;
}

export function UserCard({ name, email }: UserProps) {
  return (
    <div className="p-4 bg-white rounded-lg">
      <h2 className="text-xl font-bold">{name}</h2>
      <p className="text-gray-600">{email}</p>
    </div>
  );
}
```

#### File Structure

```
src/
├── app/              # Next.js app directory
├── components/       # Reusable components
├── lib/              # Utility functions
├── hooks/            # Custom React hooks
├── types/            # TypeScript type definitions
└── styles/           # Global styles
```

### Backend (Python/FastAPI)

#### Style Guide

- Follow **PEP 8** style guide
- Use **type hints** for all functions
- Write **docstrings** for modules and functions
- Use **async/await** for I/O operations

#### Example

```python
# Good
from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[User]:
    """
    Retrieve a list of users.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of user objects
    """
    return db.query(User).offset(skip).limit(limit).all()
```

#### File Structure

```
app/
├── api/              # API route handlers
├── core/             # Core configuration
├── db/               # Database models and session
├── services/         # Business logic
├── ml/               # ML models and utilities
├── tests/            # Test files
└── main.py           # Application entry point
```

### Code Formatting

#### Python

```bash
# Format with black (when configured)
black app/

# Sort imports
isort app/

# Type checking
mypy app/
```

#### TypeScript

```bash
# Format with prettier (when configured)
prettier --write "src/**/*.{ts,tsx}"

# Lint
npm run lint
```

---

## 💬 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
# Good commits
git commit -m "feat(backend): add user authentication endpoint"
git commit -m "fix(frontend): resolve navigation bar responsiveness issue"
git commit -m "docs: update setup guide with Docker instructions"
git commit -m "test(backend): add tests for task service"

# Bad commits
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "WIP"
```

### Detailed Commit Message

```
feat(backend): add user authentication endpoint

- Implement JWT token generation
- Add login and registration routes
- Create user authentication middleware
- Update user model with password hashing

Closes #123
```

---

## 🔍 Pull Request Process

### Before Submitting

1. ✅ Ensure all tests pass
2. ✅ Update documentation if needed
3. ✅ Follow coding standards
4. ✅ Rebase on latest main branch
5. ✅ Write clear commit messages

### PR Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
Describe the tests you ran to verify your changes

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented complex code sections
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] All tests pass locally

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #issue_number
```

### Review Process

1. At least one maintainer must approve
2. All CI checks must pass
3. No merge conflicts with main branch
4. Address all review comments

---

## 🧪 Testing Guidelines

### Frontend Testing

```typescript
// Component test example
import { render, screen } from '@testing-library/react';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  it('renders user information', () => {
    render(<UserCard name="John Doe" email="john@example.com" />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });
});
```

### Backend Testing

```python
# API test example
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_users():
    response = client.get("/api/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_user():
    user_data = {"name": "John Doe", "email": "john@example.com"}
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["name"] == "John Doe"
```

### Test Coverage

- Aim for at least 80% code coverage
- Write tests for:
  - All new features
  - Bug fixes
  - Edge cases
  - Error handling

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check if the bug has already been reported
2. Verify it's reproducible
3. Collect relevant information

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
Add screenshots if applicable

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Node version: [e.g., 18.17.0]
- Python version: [e.g., 3.13.0]

**Additional context**
Any other relevant information
```

---

## 💡 Feature Requests

### Suggesting Features

1. Check if feature already exists or is planned
2. Provide clear use case
3. Explain expected behavior
4. Consider implementation details

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem

**Describe the solution you'd like**
What you want to happen

**Describe alternatives you've considered**
Other solutions you've thought about

**Additional context**
Screenshots, mockups, or other helpful information
```

---

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

## ❓ Questions?

If you have questions about contributing:

1. Check the documentation
2. Search existing issues
3. Ask in discussions
4. Contact maintainers

---

Thank you for contributing to IT Analytics Platform! 🎉
