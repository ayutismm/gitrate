// localStorage service for saving and comparing user profiles

const STORAGE_KEY = 'gitrate_saved_profiles';

export const storage = {
    // Get all saved profiles
    getSavedProfiles: () => {
        try {
            const data = localStorage.getItem(STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return [];
        }
    },

    // Save a profile (prevent duplicates by username)
    saveProfile: (profileData) => {
        try {
            const profiles = storage.getSavedProfiles();
            const username = profileData.profile?.username || 'unknown';

            // Check if already saved
            const existingIndex = profiles.findIndex(p => p.profile?.username === username);

            const savedProfile = {
                ...profileData,
                savedAt: new Date().toISOString()
            };

            if (existingIndex >= 0) {
                // Update existing
                profiles[existingIndex] = savedProfile;
            } else {
                // Add new (limit to 10 profiles)
                profiles.unshift(savedProfile);
                if (profiles.length > 10) profiles.pop();
            }

            localStorage.setItem(STORAGE_KEY, JSON.stringify(profiles));
            return true;
        } catch (e) {
            console.error('Error saving to localStorage:', e);
            return false;
        }
    },

    // Remove a profile by username
    removeProfile: (username) => {
        try {
            const profiles = storage.getSavedProfiles();
            const filtered = profiles.filter(p => p.profile?.username !== username);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
            return true;
        } catch (e) {
            console.error('Error removing from localStorage:', e);
            return false;
        }
    },

    // Check if profile is saved
    isProfileSaved: (username) => {
        const profiles = storage.getSavedProfiles();
        return profiles.some(p => p.profile?.username === username);
    },

    // Clear all saved profiles
    clearAll: () => {
        try {
            localStorage.removeItem(STORAGE_KEY);
            return true;
        } catch (e) {
            console.error('Error clearing localStorage:', e);
            return false;
        }
    }
};
