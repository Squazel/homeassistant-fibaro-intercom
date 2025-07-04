# FIBARO Intercom Custom Card

A custom Lovelace card for the FIBARO Intercom integration that provides a unified interface for camera viewing and relay control.

## Features

- **Camera Display**: Uses Home Assistant's built-in picture-entity card for reliable camera viewing
- **Relay Controls**: Two buttons for controlling door (relay 0) and gate (relay 1)
- **Status Indicator**: Visual connection status indicator
- **Customizable**: Configure labels and button styling

## Quick Preview

You can preview the card before installation by opening [`custom_components/fibaro_intercom/frontend/demo.html`](custom_components/fibaro_intercom/frontend/demo.html) in your web browser.

## Installation

The custom card is automatically installed when you install the FIBARO Intercom integration:

1. Install the FIBARO Intercom integration
2. Go to your Lovelace dashboard  
3. Add a new card
4. Choose "Custom: FIBARO Intercom Card"
5. Configure the card with your camera entity

## Basic Configuration

```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
relay_0_label: "Front Door"
relay_1_label: "Driveway Gate"
```

## Complete Documentation

For detailed configuration options, troubleshooting, advanced usage, and development information, see the complete documentation:

**📖 [Full Card Documentation](custom_components/fibaro_intercom/frontend/README.md)**

This includes:
- Complete configuration reference
- Troubleshooting guide
- Advanced configuration examples
- Integration with automations
- Development and testing instructions

## Quick Support

For card-specific issues:
1. Check your camera entity exists and is available
2. Verify the configuration matches the examples
3. See the [complete documentation](custom_components/fibaro_intercom/frontend/README.md) for detailed troubleshooting
4. Report issues on [GitHub](https://github.com/Squazel/homeassistant-fibaro-intercom/issues)
