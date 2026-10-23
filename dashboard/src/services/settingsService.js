import api from "./api";

export const SettingsService = {
    async get() {
        const response = await api.get("/settings");
        return response.data;
    },

    async update(partialSettings) {
        const response = await api.put("/settings", partialSettings);
        return response.data;
    }
};