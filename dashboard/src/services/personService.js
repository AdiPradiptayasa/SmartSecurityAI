import api from "./api";

export const PersonService = {
    async getPersons() {
        const response = await api.get("/ai/owners");
        return { persons: response.data.owners };
    }
};