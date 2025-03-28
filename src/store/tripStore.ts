import { create } from 'zustand';

type WeatherType = 'hot' | 'cold' | 'tropical';
type EnvironmentType = 'beach' | 'mountain' | 'historic' | 'nature';
type ActivityType = 'adventure' | 'relaxation' | 'cultural' | 'mixed';

interface Preferences {
  weather: WeatherType;
  environment: EnvironmentType;
  activityType: ActivityType;
}

interface TripState {
  budget: number;
  remainingBudget: number;
  preferences: Preferences | null;
  selectedDestination: string | null;
  setBudget: (amount: number) => void;
  setPreferences: (prefs: Preferences) => void;
  setSelectedDestination: (destination: string) => void;
  updateRemainingBudget: (amount: number) => void;
  reset: () => void;
}

const initialState: TripState = {
  budget: 0,
  remainingBudget: 0,
  preferences: null,
  selectedDestination: null,
  setBudget: function (_amount: number): void {
    throw new Error('Function not implemented.');
  },
  setPreferences: function (_prefs: Preferences): void {
    throw new Error('Function not implemented.');
  },
  setSelectedDestination: function (_destination: string): void {
    throw new Error('Function not implemented.');
  },
  updateRemainingBudget: function (_amount: number): void {
    throw new Error('Function not implemented.');
  },
  reset: function (): void {
    throw new Error('Function not implemented.');
  }
};

export const useTripStore = create<TripState>((set) => ({
  ...initialState,

  setBudget: (amount) =>
    set(() => ({
      budget: amount,
      remainingBudget: amount,
    })),

  setPreferences: (prefs) =>
    set(() => ({
      preferences: prefs,
    })),

  setSelectedDestination: (destination) =>
    set(() => ({
      selectedDestination: destination,
    })),

  updateRemainingBudget: (amount) =>
    set((state) => ({
      remainingBudget: Math.max(0, state.remainingBudget - amount),
    })),

  reset: () => set(initialState),
}));
