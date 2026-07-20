# JudiQ AI: Frontend

![JudiQ Hero Banner](./judiq_hero_banner_1778733069009.png)

![Status](https://img.shields.io/badge/Status-Institutional_Beta-gold?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Tech-Vanilla_JS_ES6-blue?style=for-the-badge)

The **JudiQ AI Frontend** is a lightweight, high-performance web interface designed for Indian legal practitioners to strategize and draft litigation. It leverages a modern Vanilla JS ES6 modular architecture, delivering a premium "Blue & White" glassmorphic aesthetic without the overhead of heavy frontend frameworks.

---

## 🏛️ UI/UX Architecture

The frontend is intentionally designed to be framework-agnostic (no React/Vue) to maximize rendering speed and minimize bundle sizes, essential for handling large legal datasets on legacy hardware.

- **ES6 Modular Structure:** Native `import/export` pattern originating from `js/main.js`. No global namespace pollution.
- **Dynamic Theming:** Implements a high-contrast Blue & White light mode and a deep slate dark mode via CSS variables.
- **Glassmorphism 2.0:** Deep shadows, blurred backgrounds (`backdrop-filter`), and distinct overlays create a premium courtroom software feel.
- **Resiliency:** Implements gracefully degraded fallbacks (e.g., offline queues, WebSocket exponential backoff, image fallbacks).

---

## 🚀 Setup & Running Locally

Because strict ES6 modules use CORS protocols natively, you cannot launch `index.html` via `file://`. You must serve it over a local HTTP server.

**Prerequisites:** Python (for a simple HTTP server) or any other local server.

### Windows PowerShell:
```powershell
# From the frontend directory
.\start.ps1
```
*(Or simply run `python -m http.server 8080`)*

Access the application at `http://localhost:8080`.

---

## 🎨 Feature Highlights

### Courtroom Strategy & Forecasting
Visualize adversarial simulations and structural bounds seamlessly using `Chart.js` integrated into the custom `ChartRegistry` (to prevent memory leaks during rapid state re-renders).

![Courtroom Strategy](./judiq_courtroom_strategy.png)

### The Caseroom
Securely upload and manage physical evidence. Real-time bidirectional WebSocket syncing ensures you are always up to date with backend forensic audits.

![Caseroom Strategy](./judiq_survivability_graph.png)

---

## 📁 Directory Structure
- `index.html`: The main structural layout and UI entry point.
- `styles.css`: The central stylesheet containing dynamic theme variables.
- `js/main.js`: Application coordinator.
- `js/modules/`: Isolated business logic modules:
  - `state.js`: Global singleton store.
  - `caseroom.js`: WebSocket logic.
  - `charts.js`: Visualization registry.
  - `error_handler.js` & `ui.js`: DOM sanitization (DOMPurify).

---

© 2026 JudiQ AI. Built for the Institutional Courtroom.
