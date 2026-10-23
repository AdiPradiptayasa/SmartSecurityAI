import api from "./api";

export const EventService = {
    async getAll(limit = 50) {
        const response = await api.get("/events", {
            params: { limit }
        });
        return response.data;
    },

    async deleteOne(eventId) {
        const response = await api.delete(`/events/${eventId}`);
        return response.data;
    },

    async deleteAll() {
        const response = await api.delete("/events");
        return response.data;
    }
};