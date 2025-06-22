# ChaTEE Frontend Rebrand Implementation Plan

## Project Overview
Transform SecretGPT frontend from dark theme to professional earthy-toned "ChaTEE" interface while maintaining existing vanilla JavaScript functionality and improving user experience.

## Color Palette - Earthy Professional Theme

### Primary Colors
- **Primary Green**: `#2d5016` - Deep forest green for headers/accents
- **Secondary Green**: `#87a96b` - Sage green for status indicators  
- **Warm Brown**: `#8b4513` - Rich earth brown for text/borders
- **Background Tan**: `#f5f5dc` - Light tan/cream for main background
- **Card Background**: `#f0f0e8` - Slightly darker tan for contrast cards
- **Accent Red**: `#cc5500` - Burnt orange-red for alerts/errors
- **Text Primary**: `#3e2723` - Dark brown for primary text
- **Text Secondary**: `#5d4037` - Medium brown for secondary text

### Status Indicator Colors
- **Connected/Success**: `#4caf50` - Green circle
- **Error/Failed**: `#f44336` - Red circle
- **Checking/Loading**: `#ff9800` - Amber circle (with pulse animation)
- **Unknown/Disconnected**: `#9e9e9e` - Gray circle

## Layout Structure Redesign

### Header Layout
```
[ChaTEE Logo]           [chaTEE]           [Chat | Attestation]
```
- Logo placeholder on left
- Center brand name in primary green
- Navigation menu on right with current page highlighted

### Main Interface Layout (Chat Page)

#### Left Sidebar (Attestation Status Panel)
1. **ChaTEE Attestation Status**
   - Status circle + "ChaTEE Attestation"
   - Status text: "Connected" | "Error" | "Checking..." | "Unknown"

2. **Secret AI Attestation Status**
   - Status circle + "Secret AI Attestation"  
   - Status text: "Connected" | "Error" | "Checking..." | "Unknown"

3. **Model Information**
   - Label: "Model:"
   - Display: Current Secret AI model (e.g., "deepseek-r1:70b")

4. **Generate Proof Section**
   - Section title: "Generate Proof"
   - Password input field with earthy styling
   - Generate button in primary green

#### Central Chat Area
- Large chat interface with tan background
- Message bubbles with earthy styling
- Input field at bottom with warm brown borders

#### Footer
- "powered by secret network" in secondary text color

### Attestation Page Layout
- Same header structure
- Main content area with detailed attestation information
- Card-based layout with earthy color scheme
- Expandable sections for detailed technical data

## Implementation Plan

### Phase 1: CSS Color & Theme Overhaul (Day 1)

#### File: `static/css/style.css`
**Tasks:**
1. Replace all dark theme colors with earthy palette
2. Update background colors (dark → tan/cream)
3. Change text colors (light → dark brown)
4. Update button styling with earthy tones
5. Modify form input styling
6. Add status circle styling with animations

**Key Changes:**
- Body background: Dark → `#f5f5dc`
- Primary text: Light → `#3e2723`
- Headers: Current colors → `#2d5016`
- Buttons: Current styling → earthy green with hover effects
- Cards/containers: Dark → `#f0f0e8` with brown borders

### Phase 2: HTML Structure Updates (Day 1-2)

#### File: `templates/index.html`
**Tasks:**
1. Update page title and branding text
2. Restructure left sidebar layout
3. Reorder attestation status elements
4. Add status circle placeholders
5. Update footer branding
6. Add navigation structure for chat/attestation

**Specific Changes:**
- Replace "SecretGPT" → "ChaTEE" throughout
- Move ChaTEE attestation above Secret AI
- Add status indicator containers
- Restructure sidebar sections

### Phase 3: JavaScript Functionality Updates (Day 2)

#### File: `static/js/app.js`
**Tasks:**
1. Update text strings and labels
2. Modify status indicator logic
3. Add circle animation for loading states
4. Update attestation display functions
5. Ensure all references work with new structure

**Key Functions to Update:**
- `updateAttestationStatus()` - Use circles instead of checkmarks
- `updateAttestationDisplay()` - Match new layout structure
- `displayChatMessage()` - Apply earthy styling
- Text strings throughout application

### Phase 4: Attestation Page Styling (Day 2-3)

#### Create consistent styling for attestation page
**Tasks:**
1. Apply same color scheme to attestation details
2. Create card-based layout for technical information
3. Add expandable sections with earthy styling
4. Ensure professional presentation of technical data
5. Add proper status indicators throughout

### Phase 5: Testing & Polish (Day 3)

**Tasks:**
1. Cross-browser testing
2. Responsive design verification
3. Status indicator animation testing
4. Color contrast accessibility check
5. Final visual polish and adjustments

## Detailed Component Specifications

### Status Indicators
```css
.status-circle {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.status-connected { background-color: #4caf50; }
.status-error { background-color: #f44336; }
.status-checking { 
    background-color: #ff9800; 
    animation: pulse 1.5s infinite;
}
.status-unknown { background-color: #9e9e9e; }
```

### Typography
- **Headers**: Bold, primary green color
- **Body text**: Regular weight, dark brown
- **Status text**: Medium weight, secondary brown
- **Font family**: System fonts for professional appearance

### Button Styling
- **Primary buttons**: Forest green background, cream text
- **Hover state**: Darker green with subtle transition
- **Disabled state**: Gray with reduced opacity
- **Rounded corners**: 4px border-radius for modern look

### Card Components
- **Background**: Slightly darker tan for contrast
- **Border**: 1px solid warm brown
- **Padding**: Consistent 16px spacing
- **Shadow**: Subtle earth-tone shadow for depth

## File Structure
```
static/
├── css/
│   └── style.css (updated with earthy theme)
├── js/
│   └── app.js (updated branding & status logic)
└── images/
    └── chatee-logo.png (new logo file)

templates/
└── index.html (restructured layout)
```

## Branding Guidelines

### Logo Placement
- Header left: ChaTEE logo placeholder
- Consistent sizing and positioning
- Maintain clear space around logo

### Text References
- **Old**: "SecretGPT" → **New**: "ChaTEE"
- **Old**: "Secret GPT" → **New**: "ChaTEE"
- Maintain "powered by secret network" footer
- Keep technical terms (attestation, proof, etc.)

### Professional Presentation
- Clean, uncluttered interface
- Consistent spacing and alignment
- Professional status indicators
- Clear information hierarchy
- Accessible color contrasts

## Success Criteria
1. Complete visual transformation from dark to earthy theme
2. All functionality preserved and working
3. Professional, enterprise-ready appearance
4. Improved user experience with better layout
5. Consistent branding throughout application
6. Status indicators working correctly
7. Responsive design maintained
8. Cross-browser compatibility verified

## Timeline
- **Day 1**: CSS overhaul and basic HTML structure
- **Day 2**: JavaScript updates and attestation page
- **Day 3**: Testing, polish, and final adjustments

## Notes
- Maintain existing vanilla JavaScript architecture
- Preserve all current functionality
- Focus on visual improvements and better UX
- Ensure professional appearance suitable for enterprise use
- Keep security/attestation focus prominent in design