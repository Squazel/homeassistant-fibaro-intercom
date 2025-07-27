# FIBARO Intercom Card

A custom Lovelace card for FIBARO Intercom that wraps the native `picture-glance` card with predefined relay controls and sensible defaults.

## Quick Start

1. **Preview the card**: Open [`demo.html`](demo.html) in your browser
2. **Install**: Card is automatically available after installing the integration
3. **Configure**: Add to dashboard as "Custom: FIBARO Intercom Card"
4. **Examples**: See configuration templates in [`examples.md`](examples.md)

## Features

- **Camera Display**: Uses Home Assistant's built-in picture-entity card for reliable camera viewing
- **Relay Controls**: Two buttons for controlling door (relay 0) and gate (relay 1)
- **Automatic Configuration**: Wraps the native picture-glance card with sensible defaults
- **Customizable**: Configure labels and button styling
- **Simple Integration**: Works seamlessly with existing FIBARO Intercom entities

## Preview

Before installing, you can preview how the card looks and behaves by opening [`demo.html`](demo.html) in your web browser. This standalone demo shows:

- The complete card layout and styling
- Interactive button behavior with visual feedback
- How the card adapts to your configuration
- Expected appearance in different themes

The demo file is located in this directory and works in any modern web browser without requiring Home Assistant.

## Installation

The FIBARO Intercom card is automatically available after installing the integration. The integration registers the frontend resources automatically.

### Automatic Installation (Default)

When you install the FIBARO Intercom integration, the card becomes available automatically:
- The card is served from `/fibaro_intercom/fibaro-intercom-card.js`
- No manual resource registration is needed
- The card will appear in the "Add Card" list as "FIBARO Intercom Card"

### Manual Installation (Alternative)

If you prefer to use a manual setup or encounter issues:

1. Download `fibaro-intercom-card.js` from this directory
2. Place it in your `www` folder: `config/www/fibaro-intercom-card.js`
3. Add the resource manually:
   - Go to **Settings** → **Dashboards** → **Resources**
   - Click **Add Resource**
   - URL: `/local/fibaro-intercom-card.js`
   - Resource type: **JavaScript module**
   - Click **Create**

## Configuration

### Basic Configuration

```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
```

### Full Configuration

```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
relay_0_entity: binary_sensor.fibaro_intercom_relay_0
relay_1_entity: binary_sensor.fibaro_intercom_relay_1
title: "Front Door Intercom"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `camera_entity` | string | **Required** | Camera entity ID |
| `relay_0_entity` | string | `binary_sensor.fibaro_intercom_relay_0` | Relay 0 binary sensor entity |
| `relay_1_entity` | string | `binary_sensor.fibaro_intercom_relay_1` | Relay 1 binary sensor entity |
| `title` | string | `FIBARO Intercom` | Card title |
| `camera_view` | string | `auto` | Camera view mode (auto, live) |
| `fit_mode` | string | `cover` | How the camera image fits (cover, contain, fill) |

**Note**: Button labels and icons are taken from the entity's friendly name and icon attributes in Home Assistant. To customize them, edit the entity settings in **Settings** → **Devices & Services** → **Entities**.

## Usage

### Camera View

- **Picture Entity Card**: Uses Home Assistant's built-in picture-entity card for optimal camera display
- **Live Stream**: Click the camera to open the full camera dialog with live stream
- **Automatic Updates**: Camera view updates automatically when entity state changes

### Relay Controls

- **Door Button** (left): Triggers relay 0 with a 5-second timeout
- **Gate Button** (right): Triggers relay 1 with a 5-second timeout
- **Visual Feedback**: Buttons change color when activated and show disabled state when unavailable

## Troubleshooting

### Card Not Showing

1. Ensure the FIBARO Intercom integration is installed and configured
2. Check that your camera entity exists and is available
3. Verify the card configuration in your dashboard

### Camera Not Loading

1. Check that the camera entity is available in Home Assistant
2. Verify network connectivity to the intercom device
3. Check Home Assistant logs for camera-related errors

### Relay Buttons Not Working

1. Ensure the relay switch entities exist and are available
2. Check that the FIBARO Intercom service is registered
3. Verify network connectivity to the intercom device

### Custom Icons Not Showing

1. Ensure you're using valid Material Design Icons (mdi:) names
2. Check that the icon names are correctly spelled
3. Some icons may not be available in older Home Assistant versions

## Advanced Configuration

### Custom Entity Names

If your entities have different names (e.g., if you have multiple intercoms):

```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.front_door_intercom
relay_0_entity: binary_sensor.front_door_relay_0
relay_1_entity: binary_sensor.front_door_relay_1
```

### Different Camera Settings

All camera-specific settings (live stream, refresh rates, image quality) are handled by the picture-entity card and can be configured through Home Assistant's camera entity settings.

### Custom Styling

The card now uses the standard picture-glance card styling. For custom appearance, you can:

1. **Customize Entity Names**: Set friendly names for your entities to control button labels:
```yaml
homeassistant:
  customize:
    binary_sensor.fibaro_intercom_relay_0:
      friendly_name: "🚪 Main Entrance"
    binary_sensor.fibaro_intercom_relay_1:
      friendly_name: "🚗 Vehicle Gate"
```

2. **Use Theme Variables**: The card respects Home Assistant theme variables for colors and styling.

3. **Override Picture-Glance Options**: Pass any picture-glance configuration through `picture_glance_options`:
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
picture_glance_options:
  theme: dark
  aspect_ratio: "16:9"
```

## Integration with Automations

The card works seamlessly with Home Assistant automations. You can trigger the same relay actions programmatically:

```yaml
automation:
  - alias: "Auto-open door for family"
    trigger:
      platform: device_tracker
      entity_id: device_tracker.family_phone
      to: "home"
    action:
      service: fibaro_intercom.open_relay
      data:
        relay: 0
        timeout: 5000
```

## Styling and Themes

The card respects your Home Assistant theme colors:

- Uses `--card-background-color` for the card background
- Uses `--primary-color` for relay buttons
- Uses `--text-primary-color` for text colors
- Uses theme border radius and shadows

## Version Compatibility

- **Home Assistant**: 2023.4.0+
- **FIBARO Intercom Integration**: 1.0.0+
- **Browser**: Modern browsers with ES6 module support

## Development and Testing

### Visual Testing

The `demo.html` file provides a standalone way to test and preview the card:

```bash
# Open in your browser to see the card design
open custom_components/fibaro_intercom/frontend/demo.html  # macOS
start custom_components/fibaro_intercom/frontend/demo.html  # Windows
xdg-open custom_components/fibaro_intercom/frontend/demo.html  # Linux
```

This demo is useful for:
- **Visual Design**: Testing layout changes and styling
- **Interaction Testing**: Verifying button behavior and feedback
- **Theme Compatibility**: Seeing how the card looks with different color schemes
- **Documentation**: Showing users what to expect before installation

### Card Development

When modifying the card JavaScript:

1. Test changes in the demo first for quick iteration
2. Update the demo if you change the visual design
3. Ensure the actual card implementation matches the demo appearance
4. Test in Home Assistant after demo validation

## Integration Details

The card integrates with the main FIBARO Intercom integration and uses these entities:

- `camera.fibaro_intercom_camera` - Camera feed
- `binary_sensor.fibaro_intercom_relay_0` - Door control state
- `binary_sensor.fibaro_intercom_relay_1` - Gate control state
- Connection status from the integration coordinator

## Files in this Directory

- **[`fibaro-intercom-card.js`](fibaro-intercom-card.js)** - Main custom Lovelace card implementation
- **[`demo.html`](demo.html)** - Standalone preview/demo of the card
- **[`examples.md`](examples.md)** - Configuration examples and templates

## Support

For issues specific to the custom card:

1. Check the browser console for JavaScript errors
2. Verify your configuration matches the examples above
3. Test with the basic configuration first
4. Use the demo.html to verify expected appearance
5. Report issues on the [GitHub repository](https://github.com/Squazel/homeassistant-fibaro-intercom/issues)
