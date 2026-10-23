export const APP_CONFIG = {

    APP_NAME: import.meta.env.VITE_APP_NAME,

    CAMERA_NAME: import.meta.env.VITE_CAMERA_NAME,

    MQTT_BROKER: import.meta.env.VITE_MQTT_BROKER,

    TELEGRAM_ENABLED:

        import.meta.env.VITE_ENABLE_TELEGRAM === "true"

};