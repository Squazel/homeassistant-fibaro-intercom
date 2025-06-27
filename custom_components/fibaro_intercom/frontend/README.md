# FIBARO Intercom Custom Card

A custom Lovelace card for the FIBARO Intercom integration that provides a unified interface for camera viewing and relay control.

## Quick Start

1. **Preview the card**: Open [`demo.html`](demo.html) in your browser
2. **Install**: Card is automatically available after installing the integration
3. **Configure**: Add to dashboard as "Custom: FIBARO Intercom Card"
4. **Examples**: See configuration templates in [`examples.md`](examples.md)

## Features

- **Camera Display**: Shows live camera feed or still images with configurable refresh intervals
- **Relay Controls**: Two buttons for controlling door (relay 0) and gate (relay 1)
- **Snapshot Download**: Download still images from the camera
- **Status Indicator**: Visual connection status indicator
- **Customizable**: Configure labels, icons, and refresh intervals

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
relay_0_label: "Front Door"
relay_1_label: "Driveway Gate"
show_live_stream: true
still_refresh_interval: 30
card_height: "400px"
button_height: "60px"
camera_icon: "mdi:camera"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `camera_entity` | string | **Required** | Camera entity ID |
| `relay_0_entity` | string | `binary_sensor.fibaro_intercom_relay_0` | Relay 0 binary sensor entity |
| `relay_1_entity` | string | `binary_sensor.fibaro_intercom_relay_1` | Relay 1 binary sensor entity |
| `relay_0_label` | string | `Relay 0` | Label for relay 0 button |
| `relay_1_label` | string | `Relay 1` | Label for relay 1 button |
| `show_live_stream` | boolean | `true` | Show live stream vs still images |
| `still_refresh_interval` | number | `30` | Refresh interval for still images (seconds) |
| `card_height` | string | `400px` | Total card height |
| `button_height` | string | `60px` | Height of control buttons |
| `camera_icon` | string | `mdi:camera` | Icon for snapshot button |

**Note**: Icons for relay buttons are automatically taken from the entity's icon attribute. The integration sets default icons (`mdi:door` for relay 0, `mdi:gate` for relay 1) which can be customized in Home Assistant's entity settings.

## Usage

### Camera View

- **Still Images**: By default, the card shows still images that refresh at the configured interval
- **Live Stream**: Click the camera image to open the full camera dialog with live stream
- **Auto-refresh**: Still images automatically refresh based on the `still_refresh_interval` setting

### Relay Controls

- **Door Button** (left): Triggers relay 0 with a 5-second timeout
- **Gate Button** (right): Triggers relay 1 with a 5-second timeout
- **Visual Feedback**: Buttons change color when activated and show disabled state when unavailable

### Snapshot Download

- **Download Button**: Click the camera button below the relay controls to download a snapshot
- **Automatic Naming**: Downloads are automatically named with timestamp

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

### Different Refresh Rates

For slower networks or to reduce bandwidth:

```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
show_live_stream: false
still_refresh_interval: 60  # Refresh every minute
```

### Custom Styling

```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
card_height: "500px"
button_height: "80px"
relay_0_label: "🚪 Main Entrance"
relay_1_label: "🚗 Vehicle Gate"
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
