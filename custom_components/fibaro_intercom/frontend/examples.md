# FIBARO Intercom Card Configuration Templates

## Basic Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
```

## Standard Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
relay_0_entity: binary_sensor.fibaro_intercom_relay_0
relay_1_entity: binary_sensor.fibaro_intercom_relay_1
relay_0_label: "Front Door"
relay_1_label: "Driveway Gate"
```

## Advanced Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
relay_0_entity: binary_sensor.fibaro_intercom_relay_0
relay_1_entity: binary_sensor.fibaro_intercom_relay_1
relay_0_label: "🚪 Main Entrance"
relay_1_label: "🚗 Vehicle Gate"
show_live_stream: false
still_refresh_interval: 45
card_height: "450px"
button_height: "70px"
camera_icon: "mdi:camera-iris"
```

## Multiple Intercoms
```yaml
# Front Door Intercom
type: custom:fibaro-intercom-card
camera_entity: camera.front_door_intercom
relay_0_entity: binary_sensor.front_door_relay_0
relay_1_entity: binary_sensor.front_door_relay_1
relay_0_label: "Front Door"
relay_1_label: "Front Gate"

# Back Door Intercom
type: custom:fibaro-intercom-card
camera_entity: camera.back_door_intercom
relay_0_entity: binary_sensor.back_door_relay_0
relay_1_entity: binary_sensor.back_door_relay_1
relay_0_label: "Back Door"
relay_1_label: "Service Gate"
```

## Compact Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
card_height: "300px"
button_height: "50px"
relay_0_label: "Door"
relay_1_label: "Gate"
```

## High-refresh Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
show_live_stream: false
still_refresh_interval: 10  # Refresh every 10 seconds
```

## Custom Icons Configuration

Icons for relay buttons are automatically taken from the entity's icon attribute. To customize icons:

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Find your relay entities (e.g., `binary_sensor.fibaro_intercom_relay_0`)
3. Click the entity and edit the icon

You can also set icons via YAML configuration:

```yaml
homeassistant:
  customize:
    binary_sensor.fibaro_intercom_relay_0:
      icon: mdi:home-import-outline
    binary_sensor.fibaro_intercom_relay_1:
      icon: mdi:garage-variant
```

Card configuration (camera icon only):
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
camera_icon: "mdi:download"
```
