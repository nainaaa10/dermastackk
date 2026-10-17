# Dermastack Next.js Frontend

A skincare intelligence dashboard built with Next.js 14 (App Router), TypeScript, Tailwind CSS, and Lucide Icons.

## Features

- **Skin Image Analysis**: Responsive drag-and-drop file upload with format/dimension verification and local preview.
- **Grad-CAM Heatmap Viewer**: Side-by-side or interactive comparison slider displaying convolutional feature activations with honest demo-mode fallbacks.
- **Formulation Checker**: Automated INCI parser matching ingredients against documented cosmetic science literature, identifying comedogenicity/irritancy profiles, and warning against user sensitivities.
- **Persistence & History**: Review past analyses stored locally or in MongoDB Atlas.

## Getting Started

1. **Install Dependencies**:
   ```bash
   npm install
   ```
   *(On Windows PowerShell with strict script policies, use `npm.cmd install`)*

2. **Configure Environment**:
   ```bash
   cp .env.example .env.local
   ```
   Ensure `NEXT_PUBLIC_API_URL` points to your running FastAPI backend (default: `http://localhost:8000`).

3. **Development Server**:
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser.

4. **Production Build & Typecheck**:
   ```bash
   npm run build
   ```
