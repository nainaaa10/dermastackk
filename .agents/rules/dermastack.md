# Dermastack Project Rules

## Technology Stack
- Backend: Python 3.11+ with FastAPI & Pydantic v2
- Machine Learning: PyTorch (Hybrid CNN + Vision Transformer), Grad-CAM
- Database: MongoDB (with in-memory demo persistence fallback)
- Frontend: Next.js (App Router), TypeScript, Tailwind CSS

## Coding Guidelines
- Write clean, readable, modular code with strict typing.
- Keep frontend, backend, and ml code organized separately.
- Use environment variables for secrets and configuration.
- Implement comprehensive input validation and graceful error handling.
- Never claim diagnostic clinical accuracy; Dermastack is strictly educational and experimental.
- Do not hardcode passwords, API keys, or database credentials.
- Always provide demo mode when weights or database are absent.
