# FIBARO Intercom Card Configuration Examples

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
```

## Custom Sizing
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
# Note: card_height and button_height are no longer supported
# The card now uses standard picture-glance styling
```

## Multiple Intercoms
```yaml
# Front Door Intercom
type: custom:fibaro-intercom-card
camera_entity: camera.front_door_intercom
relay_0_entity: binary_sensor.front_door_relay_0
relay_1_entity: binary_sensor.front_door_relay_1

# Back Door Intercom
type: custom:fibaro-intercom-card
camera_entity: camera.back_door_intercom
relay_0_entity: binary_sensor.back_door_relay_0
relay_1_entity: binary_sensor.back_door_relay_1
```

## Compact Configuration
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
# Note: Compact sizing no longer available
# The card uses standard picture-glance layout
```

## Custom Icons and Labels Configuration

Button labels and icons are automatically taken from the entity's friendly name and icon attribute. To customize them:

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Find your relay entities (e.g., `binary_sensor.fibaro_intercom_relay_0`)
3. Click the entity to edit its icon

You can also set them via YAML configuration:

```yaml
homeassistant:
  customize:
    binary_sensor.fibaro_intercom_relay_0:
      friendly_name: "Front Door"
      icon: mdi:door
    binary_sensor.fibaro_intercom_relay_1:
      friendly_name: "Driveway Gate"
      icon: mdi:gate
```

The card configuration itself only needs the basic entities:
```yaml
type: custom:fibaro-intercom-card
camera_entity: camera.fibaro_intercom_camera
relay_0_entity: binary_sensor.fibaro_intercom_relay_0
relay_1_entity: binary_sensor.fibaro_intercom_relay_1
```
