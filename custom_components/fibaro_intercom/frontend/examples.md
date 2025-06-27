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
relay_0_entity: switch.fibaro_intercom_relay_0
relay_1_entity: switch.fibaro_intercom_relay_1
door_label: "Front Door"
gate_label: "Driveway Gate"
```

## Advanced Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
relay_0_entity: switch.fibaro_intercom_relay_0
relay_1_entity: switch.fibaro_intercom_relay_1
door_label: "🚪 Main Entrance"
gate_label: "🚗 Vehicle Gate"
show_live_stream: false
still_refresh_interval: 45
card_height: "450px"
button_height: "70px"
door_icon: "mdi:door-open"
gate_icon: "mdi:gate-open"
camera_icon: "mdi:camera-iris"
```

## Multiple Intercoms
```yaml
# Front Door Intercom
type: custom:fibaro-intercom-card
camera_entity: camera.front_door_intercom
relay_0_entity: switch.front_door_relay_0
relay_1_entity: switch.front_door_relay_1
door_label: "Front Door"
gate_label: "Front Gate"

# Back Door Intercom
type: custom:fibaro-intercom-card
camera_entity: camera.back_door_intercom
relay_0_entity: switch.back_door_relay_0
relay_1_entity: switch.back_door_relay_1
door_label: "Back Door"
gate_label: "Service Gate"
```

## Compact Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
card_height: "300px"
button_height: "50px"
door_label: "Door"
gate_label: "Gate"
```

## High-refresh Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
show_live_stream: false
still_refresh_interval: 10  # Refresh every 10 seconds
```

## Custom Icons Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
door_icon: "mdi:home-import-outline"
gate_icon: "mdi:garage-variant"
camera_icon: "mdi:download"
```
