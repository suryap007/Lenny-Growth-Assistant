# UI/UX Design Document

## Design Philosophy: Impeccable Style

The visual theme for the Lenny Growth Assistant is modeled after the **Impeccable** graphic design system (`impeccable.style`). The objective is to create an interface that feels highly editorial, premium, and inherently readable, stepping away from the saturated "cyber/glassmorphic" trends in favor of timeless contrast and typography.

### Core Objectives
1. **Uncompromising Readability**: Prioritize typography and contrast. Text should feel like a printed editorial layout.
2. **Cognitive Calm**: Reduce visual noise. Remove unnecessary gradients, borders, and blurs.
3. **Intentional Hierarchy**: Use strong structural dividers and high-contrast accents to guide the user's eye organically.

---

## The CSS Variable System

We centralized the design tokens in standard CSS variables (`:root`) to allow for systemic application across all components.

```css
:root {
  /* Core Palette */
  --color-primary: #CC8800;           /* Amber / Accent */
  --color-secondary: #C55221;         /* Burnt Orange / Structural */
  --color-success: #16A34A;           /* Functional Green */

  /* Surface & Base Colors */
  --color-surface-base: #FFFFFF;      /* Pure White Base Container */
  --color-surface-cream: #FDFBF7;     /* Warm Cream Background (Editorial) */
  --color-surface-dark: #121212;      /* Deep Neutral Surface */
  --color-text-main: #1C1917;         /* High-Contrast Warm Dark Text */
  --color-text-muted: #78716C;        /* Secondary / Subdued Text */

  /* Borders & Dividers */
  --color-border-subtle: #E7E5E4;     /* Crisp Divider Border */
  --color-border-strong: #1C1917;     /* High-Contrast Poster Line */
}
```

### Surface Allocation
- **Main Workspace (`--color-surface-cream`)**: The primary background for reading. The warm cream color (`#FDFBF7`) reduces eye strain and invokes a natural, paper-like feel.
- **Structural Panels (`--color-surface-base`)**: The Sidebar and Artifact Viewer utilize pure white (`#FFFFFF`) to visually separate them from the main conversational flow.
- **Code Highlights (`--color-surface-dark`)**: To preserve the native contrast of the `vscDarkPlus` syntax highlighter, code blocks and raw markdown previews are wrapped in deep neutral (`#121212`) containers, creating a striking "cutout" effect against the light UI.

---

## UX Interactions & Layout

### 1. The Artifact Viewer (Slide-In Panel)
Rather than a traditional modal that obscures context, the Artifact Viewer utilizes a flexbox-based sliding animation. 
- **Interaction**: When a user clicks "View Artifact", the viewer dynamically calculates the layout and slides in from the right.
- **Benefit**: The user maintains context of the chat while simultaneously reading the generated artifact.
- **Responsive**: On mobile screens, the flex-direction cascades into a stacked column, ensuring the artifact is still readable.

### 2. Conversation Bubbles
- **User Intent**: The user's input is styled aggressively with the `--color-primary` (Amber) background. This instantly anchors the user's eye to their own prompts as they scroll through history.
- **Assistant Response**: The assistant uses an understated `--color-surface-base` with a subtle crisp border. This prevents the UI from feeling top-heavy and allows the generated content to breathe.

### 3. State Management & Accessibility
- **Loading States**: The application uses a subtle, non-blocking CSS typing indicator (`.typing-dots`) to provide immediate feedback without shifting layout elements.
- **Contrast Ratios**: All primary text (`--color-text-main` on `--color-surface-cream`) exceeds WCAG AA standards, ensuring perfect accessibility.
