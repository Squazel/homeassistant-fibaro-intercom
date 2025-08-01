/**
 * FIBARO Intercom Card for Home Assistant
 * A wrapper around picture-glance card with predefined relay controls
 * 
 * This card acts as a simplified interface to create a picture-glance card
 * with sensible defaults for FIBARO Intercom integration, while allowing
 * full customization via picture_glance_options and entities overrides.
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
    
    // Store the original config for reference
    this._originalConfig = { ...config };
    
    // Build default entities configuration
    const defaultEntities = [
      {
        entity: config.relay_0_entity || 'binary_sensor.fibaro_intercom_relay_0',
        tap_action: {
          action: 'perform-action',
          perform_action: 'fibaro_intercom.open_relay',
          data: { relay: 0 }
        }
      },
      {
        entity: config.relay_1_entity || 'binary_sensor.fibaro_intercom_relay_1',
        tap_action: {
          action: 'perform-action',
          perform_action: 'fibaro_intercom.open_relay',
          data: { relay: 1 }
        }
      },
      {
        entity: config.connection_status_entity || 'binary_sensor.fibaro_intercom_connection_status'
      }
    ];
    
    // Build picture-glance configuration with defaults and allow overrides
    this._config = {
      type: 'picture-glance',
      title: config.title || 'FIBARO Intercom',
      camera_view: config.camera_view || 'auto',
      fit_mode: config.fit_mode || 'cover',
      camera_image: config.camera_entity,
      entity: config.camera_entity,
      entities: config.entities || defaultEntities,
      // Allow any picture-glance options to be overridden
      ...config.picture_glance_options
    };
    
    // Try to create the card immediately, with retry if needed
    this._createPictureGlanceCard();
    
    // If initial creation failed, try again after a short delay
    if (!this._pictureGlanceCard) {
      setTimeout(() => this._createPictureGlanceCard(), 100);
    }
  }

  set hass(hass) {
    this._hass = hass;
    if (this._pictureGlanceCard) {
      this._pictureGlanceCard.hass = hass;
    }
  }

  _createPictureGlanceCard() {
    if (!this._config.camera_image) {
      console.warn('FIBARO Intercom Card: No camera_image configured');
      return;
    }
    
    console.log('FIBARO Intercom Card: Attempting to create picture-glance card');
    
    // Clear shadow root first
    this.shadowRoot.innerHTML = '';
    
    try {
      // Use Home Assistant's card creation helper instead of direct element creation
      const helpers = window.loadCardHelpers && window.loadCardHelpers();
      
      if (helpers) {
        console.log('FIBARO Intercom Card: Using loadCardHelpers to create card');
        helpers.then((cardHelpers) => {
          try {
            this._pictureGlanceCard = cardHelpers.createCardElement(this._config);
            console.log('FIBARO Intercom Card: Created card using cardHelpers');
            
            if (this._hass) {
              this._pictureGlanceCard.hass = this._hass;
              console.log('FIBARO Intercom Card: Set hass on picture-glance card');
            }
            
            // Append the card
            this.shadowRoot.appendChild(this._pictureGlanceCard);
            console.log('FIBARO Intercom Card: Successfully created and appended picture-glance card');
          } catch (helperError) {
            console.warn('FIBARO Intercom Card: cardHelpers failed, falling back to direct creation:', helperError);
            this._createCardDirectly();
          }
        }).catch((error) => {
          console.warn('FIBARO Intercom Card: loadCardHelpers failed, falling back to direct creation:', error);
          this._createCardDirectly();
        });
      } else {
        console.log('FIBARO Intercom Card: loadCardHelpers not available, using direct creation');
        this._createCardDirectly();
      }
      
    } catch (error) {
      console.error('FIBARO Intercom Card: Failed to create picture-glance card:', error);
      this._showErrorCard(error);
    }
  }

  _createCardDirectly() {
    try {
      // Create the picture-glance card element directly
      this._pictureGlanceCard = document.createElement('hui-picture-glance-card');
      console.log('FIBARO Intercom Card: Created hui-picture-glance-card element directly');
      
      // Wait a tick for the element to be fully constructed
      setTimeout(() => {
        try {
          if (typeof this._pictureGlanceCard.setConfig !== 'function') {
            throw new Error('hui-picture-glance-card not properly loaded - setConfig method missing');
          }
          
          console.log('FIBARO Intercom Card: Setting config on picture-glance card');
          this._pictureGlanceCard.setConfig(this._config);
          
          if (this._hass) {
            this._pictureGlanceCard.hass = this._hass;
            console.log('FIBARO Intercom Card: Set hass on picture-glance card');
          }
          
          // Append the card
          this.shadowRoot.appendChild(this._pictureGlanceCard);
          console.log('FIBARO Intercom Card: Successfully created and appended picture-glance card');
          
        } catch (configError) {
          console.error('FIBARO Intercom Card: Failed to configure card:', configError);
          this._showErrorCard(configError);
        }
      }, 0);
      
    } catch (error) {
      console.error('FIBARO Intercom Card: Direct card creation failed:', error);
      this._showErrorCard(error);
    }
  }

  _showErrorCard(error) {
    this.shadowRoot.innerHTML = `
      <ha-card>
        <div class="card-content">
          <h3>FIBARO Intercom Card Error</h3>
          <p>Failed to load picture-glance card: ${error.message}</p>
          <p>Please ensure the card is properly configured with a camera_entity.</p>
          <details>
            <summary>Debug Info</summary>
            <pre>Config: ${JSON.stringify(this._config, null, 2)}</pre>
          </details>
        </div>
      </ha-card>
    `;
  }

  getCardSize() {
    return 3; // Standard picture-glance card size
  }

  static getConfigElement() {
    return document.createElement('fibaro-intercom-card-editor');
  }

  static getStubConfig() {
    return {
      camera_entity: 'camera.fibaro_intercom_camera',
      relay_0_entity: 'binary_sensor.fibaro_intercom_relay_0',
      relay_1_entity: 'binary_sensor.fibaro_intercom_relay_1',
      connection_status_entity: 'binary_sensor.fibaro_intercom_connection_status',
      title: 'FIBARO Intercom'
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
        .help-text {
          font-size: 0.9em;
          color: var(--secondary-text-color);
          margin-top: 4px;
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
        
        <div class="section-title">Basic Configuration</div>
        
        <div class="config-row">
          <label>Title</label>
          <ha-textfield 
            id="title" 
            .value="${this._config.title || 'FIBARO Intercom'}"
            placeholder="FIBARO Intercom"
          ></ha-textfield>
        </div>
        
        <div class="config-row">
          <label>Relay 0 Entity</label>
          <ha-textfield 
            id="relay_0_entity" 
            .value="${this._config.relay_0_entity || 'binary_sensor.fibaro_intercom_relay_0'}"
            placeholder="binary_sensor.fibaro_intercom_relay_0"
          ></ha-textfield>
        </div>
        
        <div class="config-row">
          <label>Relay 1 Entity</label>
          <ha-textfield 
            id="relay_1_entity" 
            .value="${this._config.relay_1_entity || 'binary_sensor.fibaro_intercom_relay_1'}"
            placeholder="binary_sensor.fibaro_intercom_relay_1"
          ></ha-textfield>
        </div>
        
        <div class="config-row">
          <label>Connection Status Entity</label>
          <ha-textfield 
            id="connection_status_entity" 
            .value="${this._config.connection_status_entity || 'binary_sensor.fibaro_intercom_connection_status'}"
            placeholder="binary_sensor.fibaro_intercom_connection_status"
          ></ha-textfield>
        </div>
        
        <div class="section-title">Picture-Glance Options</div>
        <div class="help-text">These settings control the camera display (same as picture-glance card)</div>
        
        <div class="config-row">
          <label>Camera View</label>
          <ha-textfield 
            id="camera_view" 
            .value="${this._config.camera_view || 'auto'}"
            placeholder="auto"
          ></ha-textfield>
        </div>
        
        <div class="config-row">
          <label>Fit Mode</label>
          <ha-textfield 
            id="fit_mode" 
            .value="${this._config.fit_mode || 'cover'}"
            placeholder="cover"
          ></ha-textfield>
        </div>
        
        <div class="section-title">Advanced</div>
        <div class="help-text">For custom entities or overrides, edit the YAML directly</div>
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

try {
  customElements.define('fibaro-intercom-card', FibaroIntercomCard);
  console.log('Successfully registered fibaro-intercom-card');
} catch (error) {
  console.error('Failed to register fibaro-intercom-card:', error);
}

try {
  customElements.define('fibaro-intercom-card-editor', FibaroIntercomCardEditor);
  console.log('Successfully registered fibaro-intercom-card-editor');
} catch (error) {
  console.error('Failed to register fibaro-intercom-card-editor:', error);
}

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

console.log('fibaro-intercom-card registration complete. Total custom cards:', window.customCards.length);
