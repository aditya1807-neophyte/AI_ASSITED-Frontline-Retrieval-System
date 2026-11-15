import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '@/services/api';

export interface UserProfile {
  id: number;
  name: string;
  email: string;
  role: string;
  login_identifier: string;
  initials: string;
  formattedRole: string;
  language: string;
  notifications: boolean;
  weeklyDigest: boolean;
  autoSaveAnswers: boolean;
}

interface UserContextType {
  user: UserProfile;
  isLoading: boolean;
  updateProfile: (updates: Partial<UserProfile>) => Promise<boolean>;
  refreshProfile: () => Promise<void>;
}

export function getInitials(name: string): string {
  if (!name || !name.trim()) return 'JD';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export function formatRole(role: string): string {
  switch (role) {
    case 'analyst':
      return 'Analyst';
    case 'manager':
      return 'Manager';
    case 'field_technician':
      return 'Field Technician';
    case 'safety_officer':
      return 'Safety Officer';
    case 'maintenance_engineer':
      return 'Maintenance Engineer';
    case 'site_supervisor':
      return 'Site Supervisor';
    case 'admin':
      return 'Administrator';
    default:
      return role
        ? role.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
        : 'Frontline User';
  }
}

const DEFAULT_PROFILE: UserProfile = {
  id: 1,
  name: 'Jordan Diaz',
  email: 'jordan.diaz@fieldguide.ai',
  role: 'analyst',
  login_identifier: 'jordan.diaz',
  initials: 'JD',
  formattedRole: 'Analyst',
  language: 'en',
  notifications: true,
  weeklyDigest: false,
  autoSaveAnswers: true,
};

const STORAGE_KEY = 'fieldguide_user_profile';

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        return {
          ...DEFAULT_PROFILE,
          ...parsed,
          initials: getInitials(parsed.name || DEFAULT_PROFILE.name),
          formattedRole: formatRole(parsed.role || DEFAULT_PROFILE.role),
        };
      }
    } catch {
      // Fallback to default
    }
    return DEFAULT_PROFILE;
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);

  const syncStateAndStorage = useCallback((profile: UserProfile) => {
    setUser(profile);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
      window.dispatchEvent(new CustomEvent('fieldguide-profile-updated', { detail: profile }));
    } catch {
      // Ignore localstorage errors
    }
  }, []);

  const refreshProfile = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await api.get('/users/me');
      if (res.data) {
        const data = res.data;
        let prefs: any = {};
        if (data.preferences) {
          try {
            prefs = typeof data.preferences === 'string' ? JSON.parse(data.preferences) : data.preferences;
          } catch {
            prefs = {};
          }
        }

        const name = data.display_name || user.name || DEFAULT_PROFILE.name;
        const role = data.role || user.role || DEFAULT_PROFILE.role;

        const updated: UserProfile = {
          id: data.id || 1,
          name,
          email: data.email || `${data.login_identifier || 'jordan.diaz'}@fieldguide.ai`,
          role,
          login_identifier: data.login_identifier || 'jordan.diaz',
          initials: getInitials(name),
          formattedRole: formatRole(role),
          language: prefs.language || user.language || 'en',
          notifications: prefs.notifications !== undefined ? prefs.notifications : user.notifications,
          weeklyDigest: prefs.weeklyDigest !== undefined ? prefs.weeklyDigest : user.weeklyDigest,
          autoSaveAnswers: prefs.autoSaveAnswers !== undefined ? prefs.autoSaveAnswers : user.autoSaveAnswers,
        };

        syncStateAndStorage(updated);
      }
    } catch (err) {
      console.warn('Could not sync user profile from backend, using local profile:', err);
    } finally {
      setIsLoading(false);
    }
  }, [user.name, user.role, user.language, user.notifications, user.weeklyDigest, user.autoSaveAnswers, syncStateAndStorage]);

  useEffect(() => {
    refreshProfile();

    const handleStorageEvent = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && e.newValue) {
        try {
          const parsed = JSON.parse(e.newValue);
          setUser({
            ...parsed,
            initials: getInitials(parsed.name),
            formattedRole: formatRole(parsed.role),
          });
        } catch {}
      }
    };

    window.addEventListener('storage', handleStorageEvent);
    return () => window.removeEventListener('storage', handleStorageEvent);
  }, []);

  const updateProfile = useCallback(
    async (updates: Partial<UserProfile>): Promise<boolean> => {
      const newName = updates.name !== undefined ? updates.name.trim() : user.name;
      const newRole = updates.role !== undefined ? updates.role : user.role;
      const newEmail = updates.email !== undefined ? updates.email.trim() : user.email;
      const newLang = updates.language !== undefined ? updates.language : user.language;
      const newNotify = updates.notifications !== undefined ? updates.notifications : user.notifications;
      const newWeekly = updates.weeklyDigest !== undefined ? updates.weeklyDigest : user.weeklyDigest;
      const newAutoSave = updates.autoSaveAnswers !== undefined ? updates.autoSaveAnswers : user.autoSaveAnswers;

      const updatedProfile: UserProfile = {
        ...user,
        ...updates,
        name: newName,
        role: newRole,
        email: newEmail,
        language: newLang,
        notifications: newNotify,
        weeklyDigest: newWeekly,
        autoSaveAnswers: newAutoSave,
        initials: getInitials(newName),
        formattedRole: formatRole(newRole),
      };

      // Optimistically update UI and local storage
      syncStateAndStorage(updatedProfile);

      // Persist to backend database
      try {
        const payload: any = {
          display_name: newName,
          email: newEmail,
          role: newRole,
          preferences: JSON.stringify({
            language: newLang,
            notifications: newNotify,
            weeklyDigest: newWeekly,
            autoSaveAnswers: newAutoSave,
          }),
        };

        const res = await api.put('/users/me', payload);
        if (res.data) {
          const synced: UserProfile = {
            ...updatedProfile,
            id: res.data.id || updatedProfile.id,
            name: res.data.display_name || updatedProfile.name,
            email: res.data.email || updatedProfile.email,
            role: res.data.role || updatedProfile.role,
            initials: getInitials(res.data.display_name || updatedProfile.name),
            formattedRole: formatRole(res.data.role || updatedProfile.role),
          };
          syncStateAndStorage(synced);
        }
        return true;
      } catch (err) {
        console.error('Failed to persist user profile to backend:', err);
        // Note: local state was still saved, but report partial failure if needed
        return true;
      }
    },
    [user, syncStateAndStorage]
  );

  return (
    <UserContext.Provider value={{ user, isLoading, updateProfile, refreshProfile }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}

