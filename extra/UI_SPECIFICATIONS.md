# JobMatch: UI Design System Specifications
**Version 1.0 | Theme: "Operational Clarity"**

## 1. Visual Identity
A premium, minimalist aesthetic designed for executive dashboards and high-velocity recruiters. The look is "Clinical & Precise" (inspired by MedTech/FinTech).

### 1.1 Color Palette
*   **Primary (Canvas):** `Create-Off-White` (#F5F5F7) or `Deep Obsidian` (#121212) for Dark Mode.
*   **Secondary (Surface):** `Pure White` (#FFFFFF) with subtle drop shadows.
*   **Accent (Intelligence):** `Electric Teal` (#00C2CB) - Used mostly for "Match Scores" and "AI Insights".
*   **Action (Primary Button):** `Jet Black` (#000000) - High contrast, authoritative.
*   **Semantic Colors:**
    *   *Risk/Low Confidence:* `Burnt Coral` (#FF6B6B)
    *   *Verified:* `Success Green` (#2E7D32)

### 1.2 Typography
*   **Headings:** *Inter* or *SF Pro Display* (Bold, Tight Tracking).
    *   H1: 32px (Dashboard Titles)
    *   H2: 24px (Section Headers)
*   **Body:** *Inter* or *Roboto* (Regular, 16px).
*   **Data/Code:** *JetBrains Mono* (for Candidate IDs or Raw Scores).

## 2. Component library

### 2.1 The "Candidate Card"
*   **Shape:** Rounded Corners (16px radius).
*   **Content:**
    *   **Top Left:** Candidate Photo (Circular Avatar).
    *   **Top Right:** Match Score Badge (Pill shape, Teal background, White text).
    *   **Center:** Name (Bold), Current Role (Grey).
    *   **Bottom:** Top 3 Skill Tags (Grey Pill outlines).

### 2.2 Buttons & Actions
*   **Primary Action ("Deploy Offer"):** Full-width, Jet Black fill, White Text, 12px Radius.
*   **Secondary Action ("View Details"):** No fill, Black Border (1px), Black Text.

### 2.3 Data Visualization
*   **Confidence Meter:** A semi-circle gauge.
    *   filled arc = Confidence %.
    *   Color changes from Coral (<50%) to Teal (>80%).

## 3. Layout Principles
*   **Whitespace:** Generous padding (24px default). "Airy" layouts prevent information overload.
*   **Hierarchy:** The **Match Score** is always the visual anchor (largest/brightest element).
*   **Micro-Interactions:**
    *   *Hover:* Cards lift slightly (elevation shadow increases).
    *   *Loading:* Skeleton screens (grey pulse) instead of spinners.

## 4. Mockup Scenarios
1.  **Mobile View:** Single column, "Tinder-like" swipe interface for quick screening.
2.  **Desktop Dashboard:** Grid view of candidates with a sidebar for "Drift Monitoring" metrics.
