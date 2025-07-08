# secretGPT Preview Pages

This directory contains static HTML preview pages for the secretGPT web interface, designed for UI development and testing with VS Code Live Server.

## Files

- `chat-preview.html` - Chat interface preview page
- `attestation-preview.html` - Attestation documentation preview page

## Usage

1. **Install VS Code Live Server Extension**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Live Server" by Ritwick Dey
   - Install the extension

2. **Open Preview Pages**
   - Open the `F:/coding/secretGPT/preview` folder in VS Code
   - Right-click on either `chat-preview.html` or `attestation-preview.html`
   - Select "Open with Live Server"
   - Your browser will open with the preview page

3. **Live Editing**
   - Edit the HTML, CSS, or JavaScript directly in the preview files
   - Save the file (Ctrl+S)
   - The browser will automatically refresh with your changes

## Features

### Chat Preview
- Interactive chat interface with sample messages
- Working message input and send functionality
- Simulated AI responses
- Status indicators with demo animations
- Streaming toggle functionality
- Clear chat functionality

### Attestation Preview
- Progressive disclosure educational content
- Interactive VM verification buttons
- Animated status indicators
- Technical documentation sections
- Working navigation between pages

## Differences from Production

These preview pages are simplified versions of the actual application:
- All CSS is inline for easy editing
- JavaScript functions are simplified mock implementations
- No actual backend connectivity
- Sample data and responses are hardcoded
- Uses CDN links for Bootstrap and Font Awesome

## Development Workflow

1. Make UI changes in the preview files
2. Test in Live Server
3. Once satisfied, apply changes to the actual template files:
   - `interfaces/web_ui/templates/index.html`
   - `interfaces/web_ui/templates/attestation.html`
   - `interfaces/web_ui/static/css/style.css`

## Color Scheme

The preview pages use the Attest AI color palette:
- Primary Green: #2d5016
- Secondary Green: #87a96b  
- Background Tan: #f5f5dc
- Card Background: #f0f0e8
- Text Primary: #3e2723
- Status indicators with appropriate colors for different states

## Interactive Elements

Both pages include interactive elements for testing:
- Hover effects on cards and buttons
- Animated status indicators
- Progressive disclosure sections (attestation page)
- Form interactions
- Navigation between pages
