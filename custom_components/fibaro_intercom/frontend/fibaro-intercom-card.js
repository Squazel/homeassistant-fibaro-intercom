/**
 * FIBARO Intercom Card for Home Assistant
 * Custom Lovelace card combining camera view with relay controls
 */

class FibaroIntercomCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = null;
  }

  static get properties() {
    return {
      hass: {},
      config: {}
    };
  }

  setConfig(config) {
    if (!config.camera_entity) {
      throw new Error('You need to define a camera_entity');
    }
    
    const previousCameraEntity = this._config?.camera_entity;
    
    this._config = {
      // Required
      camera_entity: config.camera_entity,
      
      // Optional with defaults - these are binary sensors that show relay state
      relay_0_entity: config.relay_0_entity || 'binary_sensor.fibaro_intercom_relay_0',
      relay_1_entity: config.relay_1_entity || 'binary_sensor.fibaro_intercom_relay_1',
      relay_0_label: config.relay_0_label || 'Relay 0',
      relay_1_label: config.relay_1_label || 'Relay 1',
      
      // Styling
      card_height: config.card_height || '400px',
      button_height: config.button_height || '60px',
      
      ...config
    };
    
    this._render();
    
    // Only recreate the picture card if the camera entity changed
    if (!this._pictureCard || previousCameraEntity !== config.camera_entity) {
      this._createPictureEntityCard();
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._updatePictureEntityCard();
    this._updateStates();
  }

  _render() {
    this.shadowRoot.innerHTML = `
      <style>
        .fibaro-card {
          background: var(--card-background-color);
          border-radius: var(--border-radius);
          box-shadow: var(--box-shadow);
          padding: 16px;
          height: ${this._config.card_height};
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        
        .camera-container {
          flex: 1;
          position: relative;
          border-radius: 8px;
          overflow: hidden;
          background: #000;
          min-height: 200px;
        }
        
        .picture-entity-card {
          width: 100%;
          height: 100%;
          border-radius: 8px;
          overflow: hidden;
        }
        
        .controls {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .relay-controls {
          display: flex;
          gap: 8px;
        }
        
        .relay-button {
          flex: 1;
          height: ${this._config.button_height};
          border: none;
          border-radius: 8px;
          background: var(--primary-color);
          color: var(--text-primary-color);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.2s ease;
        }
        
        .relay-button:hover {
          background: var(--primary-color-dark);
          transform: translateY(-1px);
        }
        
        .relay-button:active {
          transform: translateY(0);
        }
        
        .relay-button:disabled {
          background: var(--disabled-color);
          cursor: not-allowed;
          transform: none;
        }
        
        .icon {
          width: 20px;
          height: 20px;
        }
        
        .status-indicator {
          position: absolute;
          top: 12px;
          right: 12px;
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: var(--error-color);
        }
        
        .status-indicator.connected {
          background: var(--success-color);
        }
        
        .loading {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: var(--secondary-text-color);
        }
      </style>
      
      <div class="fibaro-card">
        <div class="camera-container">
          <div class="status-indicator" id="status-indicator"></div>
          <div class="picture-entity-card" id="picture-entity-container">
            <!-- Picture entity card will be inserted here -->
          </div>
        </div>
        
        <div class="controls">
          <div class="relay-controls">
            <button class="relay-button" id="door-button">
              <ha-icon id="door-icon" icon="mdi:door" class="icon"></ha-icon>
              ${this._config.relay_0_label}
            </button>
            <button class="relay-button" id="gate-button">
              <ha-icon id="gate-icon" icon="mdi:gate" class="icon"></ha-icon>
              ${this._config.relay_1_label}
            </button>
          </div>
        </div>
      </div>
    `;
    
    this._attachEventListeners();
    this._updateStates();
  }

  _attachEventListeners() {
    const doorButton = this.shadowRoot.getElementById('door-button');
    const gateButton = this.shadowRoot.getElementById('gate-button');

    doorButton.addEventListener('click', () => this._openRelay(0));
    gateButton.addEventListener('click', () => this._openRelay(1));
  }

  _getEntityIcon(entityId) {
    if (!this._hass || !entityId) return null;
    const entity = this._hass.states[entityId];
    return entity?.attributes?.icon;
  }

  _createPictureEntityCard() {
    if (!this._config.camera_entity) return;
    
    const container = this.shadowRoot.getElementById('picture-entity-container');
    console.log('Starting _createPictureEntityCard, container:', container);
    console.log('Checking hui-picture-entity-card definition:', window.customElements.get('hui-picture-entity-card'));
    
    // Show loading state
    if (container) {
      container.innerHTML = '<div class="loading">Loading camera...</div>';
    }
    
    // Add timeout fallback
    let timeoutId = setTimeout(() => {
      console.error('Timeout waiting for hui-picture-entity-card to be defined');
      if (container) {
        container.innerHTML = '<div class="loading">Camera loading failed</div>';
      }
    }, 10000); // 10 second timeout
    
    window.customElements.whenDefined('hui-picture-entity-card').then(() => {
      clearTimeout(timeoutId);
      console.log('hui-picture-entity-card is now defined:', window.customElements.get('hui-picture-entity-card'));
      this._pictureCard = document.createElement('hui-picture-entity-card');
      const pictureConfig = {
        type: 'picture-entity',
        entity: this._config.camera_entity,
        show_state: false,
        show_name: false,
        camera_view: 'auto',
        fit_mode: 'cover'
      };
      if (typeof this._pictureCard.setConfig === 'function') {
        console.log('setConfig is a function, configuring card...');
        this._pictureCard.setConfig(pictureConfig);
        console.log('Picture card configured, inserting...');
        this._insertPictureCard();
      } else {
        console.error('setConfig is NOT a function on hui-picture-entity-card:', this._pictureCard);
      }
    }).catch(error => {
      clearTimeout(timeoutId);
      console.error('Error waiting for hui-picture-entity-card:', error);
    });
  }

  _insertPictureCard() {
    const container = this.shadowRoot.getElementById('picture-entity-container');
    console.log('_insertPictureCard called, container:', container, 'pictureCard:', this._pictureCard);
    if (container && this._pictureCard) {
      container.innerHTML = '';
      container.appendChild(this._pictureCard);
      console.log('Picture card appended to container');
      if (this._hass) {
        this._pictureCard.hass = this._hass;
        console.log('Hass assigned to picture card');
      }
    } else {
      console.error('Cannot insert picture card - container or pictureCard missing');
    }
  }

  _updatePictureEntityCard() {
    if (this._pictureCard && this._hass) {
      this._pictureCard.hass = this._hass;
    }
  }

  _updateStates() {
    if (!this._hass) return;

    // Update connection status based on camera entity
    const statusIndicator = this.shadowRoot.getElementById('status-indicator');
    const cameraEntity = this._hass.states[this._config.camera_entity];
    
    if (cameraEntity && cameraEntity.state !== 'unavailable') {
      statusIndicator.classList.add('connected');
    } else {
      statusIndicator.classList.remove('connected');
    }

    // Update relay button states
    const relay0Entity = this._hass.states[this._config.relay_0_entity];
    const relay1Entity = this._hass.states[this._config.relay_1_entity];
    const doorButton = this.shadowRoot.getElementById('door-button');
    const gateButton = this.shadowRoot.getElementById('gate-button');
    const doorIcon = this.shadowRoot.getElementById('door-icon');
    const gateIcon = this.shadowRoot.getElementById('gate-icon');
    
    // Update icons from entity attributes
    const relay0Icon = this._getEntityIcon(this._config.relay_0_entity) || 'mdi:door';
    const relay1Icon = this._getEntityIcon(this._config.relay_1_entity) || 'mdi:gate';
    
    if (doorIcon) doorIcon.setAttribute('icon', relay0Icon);
    if (gateIcon) gateIcon.setAttribute('icon', relay1Icon);
    
    // Update button availability and appearance
    const relay0Available = relay0Entity && relay0Entity.state !== 'unavailable';
    const relay1Available = relay1Entity && relay1Entity.state !== 'unavailable';
    
    doorButton.disabled = !relay0Available;
    gateButton.disabled = !relay1Available;
    
    // Update button colors based on relay state (on = relay is open)
    if (relay0Entity && relay0Entity.state === 'on') {
      doorButton.style.background = 'var(--success-color)';
    } else {
      doorButton.style.background = 'var(--primary-color)';
    }
    
    if (relay1Entity && relay1Entity.state === 'on') {
      gateButton.style.background = 'var(--success-color)';
    } else {
      gateButton.style.background = 'var(--primary-color)';
    }
  }

  async _openRelay(relayNumber) {
    if (!this._hass) return;

    const button = relayNumber === 0 ? 
      this.shadowRoot.getElementById('door-button') : 
      this.shadowRoot.getElementById('gate-button');
    
    button.disabled = true;
    
    try {
      await this._hass.callService('fibaro_intercom', 'open_relay', {
        relay: relayNumber,
        timeout: 5000 // Default 5 second timeout
      });
      
      // Visual feedback
      button.style.background = 'var(--success-color)';
      setTimeout(() => {
        button.style.background = 'var(--primary-color)';
        button.disabled = false;
      }, 2000);
      
    } catch (error) {
      console.error('Failed to open relay:', error);
      button.style.background = 'var(--error-color)';
      setTimeout(() => {
        button.style.background = 'var(--primary-color)';
        button.disabled = false;
      }, 2000);
    }
  }

  getCardSize() {
    return 5; // Approximate card height in grid rows
  }

  static getConfigElement() {
    return document.createElement('fibaro-intercom-card-editor');
  }

  static getStubConfig() {
    return {
      camera_entity: 'camera.fibaro_intercom_camera',
      relay_0_entity: 'binary_sensor.fibaro_intercom_relay_0',
      relay_1_entity: 'binary_sensor.fibaro_intercom_relay_1',
      relay_0_label: 'Relay 0',
      relay_1_label: 'Relay 1'
    };
  }
}

// Configuration editor for the card
class FibaroIntercomCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  _render() {
    this.shadowRoot.innerHTML = `
      <style>
        .config-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin: 8px 0;
        }
        .config-row label {
          flex: 1;
          margin-right: 16px;
        }
        .config-row ha-textfield,
        .config-row ha-switch {
          flex: 1;
        }
        .section-title {
          font-weight: bold;
          margin: 16px 0 8px 0;
          color: var(--primary-text-color);
        }
      </style>
      
      <div>
        <div class="section-title">Required</div>
        
        <div class="config-row">
          <label>Camera Entity</label>
          <ha-textfield 
            id="camera_entity" 
            .value="${this._config.camera_entity || ''}"
            placeholder="camera.fibaro_intercom_camera"
          ></ha-textfield>
        </div>
        
        <div class="section-title">Relay Controls</div>
        
        <div class="config-row">
          <label>Relay 0 Entity (Door)</label>
          <ha-textfield 
            id="relay_0_entity" 
            .value="${this._config.relay_0_entity || 'binary_sensor.fibaro_intercom_relay_0'}"
          ></ha-textfield>
        </div>
        
        <div class="config-row">
          <label>Relay 1 Entity (Gate)</label>
          <ha-textfield 
            id="relay_1_entity" 
            .value="${this._config.relay_1_entity || 'binary_sensor.fibaro_intercom_relay_1'}"
          ></ha-textfield>
        </div>
        
        <div class="config-row">
          <label>Relay 0 Button Label</label>
          <ha-textfield 
            id="relay_0_label" 
            .value="${this._config.relay_0_label || 'Relay 0'}"
          ></ha-textfield>
        </div>
        
        <div class="config-row">
          <label>Relay 1 Button Label</label>
          <ha-textfield 
            id="relay_1_label" 
            .value="${this._config.relay_1_label || 'Relay 1'}"
          ></ha-textfield>
        </div>
        
        <div class="section-title">Styling</div>
        
        <div class="config-row">
          <label>Card Height</label>
          <ha-textfield 
            id="card_height" 
            .value="${this._config.card_height || '400px'}"
            placeholder="400px"
          ></ha-textfield>
        </div>
        
        <div class="config-row">
          <label>Button Height</label>
          <ha-textfield 
            id="button_height" 
            .value="${this._config.button_height || '60px'}"
            placeholder="60px"
          ></ha-textfield>
        </div>
      </div>
    `;
    
    this._attachListeners();
  }

  _attachListeners() {
    const inputs = this.shadowRoot.querySelectorAll('ha-textfield, ha-switch');
    inputs.forEach(input => {
      input.addEventListener('change', (e) => {
        const key = e.target.id;
        let value = e.target.value;
        
        if (e.target.tagName === 'HA-SWITCH') {
          value = e.target.checked;
        } else if (key === 'card_height' || key === 'button_height') {
          // Keep as string for CSS values
        } else {
          // Other text fields, keep as string
        }
        
        this._config[key] = value;
        this._configChanged();
      });
    });
  }

  _configChanged() {
    const event = new CustomEvent('config-changed', {
      detail: { config: this._config },
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(event);
  }
}

// Register the custom elements
console.log('Registering fibaro-intercom-card and editor...');
customElements.define('fibaro-intercom-card', FibaroIntercomCard);
customElements.define('fibaro-intercom-card-editor', FibaroIntercomCardEditor);

// Register the card with Home Assistant
console.log('Pushing fibaro-intercom-card to window.customCards...');
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'fibaro-intercom-card',
  name: 'FIBARO Intercom Card',
  description: 'Custom card for FIBARO Intercom with camera and relay controls',
  preview: true,
  documentationURL: 'https://github.com/Squazel/homeassistant-fibaro-intercom'
});
