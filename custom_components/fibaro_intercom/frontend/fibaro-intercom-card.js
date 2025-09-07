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
    
    // Build picture-glance configuration with defaults and allow overrides.
    // NOTE: picture-glance does NOT (currently) support a fit_mode option; avoid
    // passing unknown keys that might interfere with internal size calculations.
    const { fit_mode: _ignoredFitMode, ...pgOverrides } = config.picture_glance_options || {};
    this._config = {
      type: 'picture-glance',
      title: config.title || 'FIBARO Intercom',
      camera_view: config.camera_view || 'auto',
      camera_image: config.camera_entity,
      entity: config.camera_entity,
      entities: config.entities || defaultEntities,
      ...pgOverrides
    };

    // If we already have a card instance, just forward the new config instead of recreating.
    if (this._pictureGlanceCard && typeof this._pictureGlanceCard.setConfig === 'function') {
      try {
        this._pictureGlanceCard.setConfig(this._config);
        return; // Reuse existing card
      } catch (e) {
        console.warn('FIBARO Intercom Card: reusing existing card failed, recreating', e);
        this._pictureGlanceCard = null;
      }
    }

    this._createPictureGlanceCard();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._pictureGlanceCard) {
      this._pictureGlanceCard.hass = hass;
    }
  }

  _createPictureGlanceCard() {
    if (!this._config?.camera_image) {
      console.warn('FIBARO Intercom Card: No camera_image configured');
      return;
    }

    // Guard against multiple concurrent creations (race when HA calls setConfig rapidly)
    if (this._creating) {
      this._pendingRecreate = true;
      return;
    }
    this._creating = true;
    const creationToken = (this._creationToken = (this._creationToken || 0) + 1);

    const finalize = (card) => {
      // If a newer creation started, discard this one
      if (creationToken !== this._creationToken) return;

      // Clear previous content (only now, to avoid empty period while async loads)
      this.shadowRoot.innerHTML = '';
      this._pictureGlanceCard = card;
      if (this._hass) {
        this._pictureGlanceCard.hass = this._hass;
      }
      this.shadowRoot.appendChild(this._pictureGlanceCard);
      this._creating = false;
      if (this._pendingRecreate) {
        // A newer config arrived while we were creating; recreate once more.
        this._pendingRecreate = false;
        this._createPictureGlanceCard();
      }
    };

    try {
      const helpersPromise = window.loadCardHelpers && window.loadCardHelpers();
      if (helpersPromise) {
        helpersPromise
          .then((helpers) => {
            if (creationToken !== this._creationToken) return; // stale
            let card;
            try {
              card = helpers.createCardElement(this._config);
            } catch (e) {
              console.warn('FIBARO Intercom Card: helpers.createCardElement failed, fallback to direct element', e);
              card = document.createElement('hui-picture-glance-card');
            }
            // Ensure config applied
            if (typeof card.setConfig === 'function') {
              try { card.setConfig(this._config); } catch (e) { console.error('FIBARO Intercom Card: setConfig failed', e); }
            }
            finalize(card);
          })
          .catch((e) => {
            console.warn('FIBARO Intercom Card: loadCardHelpers promise rejected, fallback to direct creation', e);
            const card = document.createElement('hui-picture-glance-card');
            this._configureDirectCard(card, finalize);
          });
      } else {
        // Fallback: direct element now, attempt a delayed helper usage later (common when card loads early)
        const card = document.createElement('hui-picture-glance-card');
        this._configureDirectCard(card, finalize);
        // Try again shortly with helpers if they become available (single retry)
        setTimeout(() => {
          if (!this._pictureGlanceCard || creationToken !== this._creationToken) return;
          if (window.loadCardHelpers) {
            window.loadCardHelpers().then((helpers) => {
              // If helpers are now ready and we used a raw element with a setConfig, nothing else required.
              // We intentionally do not recreate to avoid flicker.
            });
          }
        }, 250);
      }
    } catch (error) {
      console.error('FIBARO Intercom Card: Unexpected error during creation', error);
      this._creating = false;
      this._showErrorCard(error);
    }
  }

  _configureDirectCard(card, finalizeCb) {
    // Apply config after a microtask to allow element definition upgrade
    queueMicrotask(() => {
      try {
        if (typeof card.setConfig !== 'function') {
          // If the element hasn't upgraded yet, try again next frame
          requestAnimationFrame(() => {
            if (typeof card.setConfig === 'function') {
              try { card.setConfig(this._config); } catch (e) { console.error(e); }
            }
            finalizeCb(card);
          });
          return;
        }
        card.setConfig(this._config);
      } catch (e) {
        console.error('FIBARO Intercom Card: direct card setConfig error', e);
      }
      finalizeCb(card);
    });
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
    if (this._pictureGlanceCard && typeof this._pictureGlanceCard.getCardSize === 'function') {
      try { return this._pictureGlanceCard.getCardSize(); } catch (_) { /* ignore */ }
    }
    return 3; // Fallback size
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
